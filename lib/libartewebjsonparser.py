# -*- coding: utf-8 -*-
import requests
import json 
import libmediathek4utils as lm4utils

#https://player-v5-dev.arte.tv/static

#https://api.arte.tv/api/emac/v3/en/web/data/MANUAL_TEASERS/?imageFormats=landscape&code=highlights_category&page=2&limit=6

headers = {'Authorization':'Bearer YTEwZWE3M2UxMTVmYmRjZmE0YTdmNjA4ZTI2NDczZDU3YjdjYmVmMmRmNGFjOTM3M2RhNTM5ZjIxYmI3NTc1Zg'}


class APIParser:
	def __init__(self):
		self.result = {'items':[],'pagination':{'currentPage':0}}
		self.baseURL = 'https://www.arte.tv/guide/api/emac/v3'
		self.baseURLGuide = 'https://www.arte.tv/api/emac/v3'
		self.baseURLApp = 'https://api-cdn.arte.tv/api/emac/v3/'
		self.token = 'YTEwZWE3M2UxMTVmYmRjZmE0YTdmNjA4ZTI2NDczZDU3YjdjYmVmMmRmNGFjOTM3M2RhNTM5ZjIxYmI3NTc1Zg'
		self.baseURLAppPreprod = 'https://api-preprod.arte.tv/api/emac/v3/'
		self.tokenPreprod = 'MWZmZjk5NjE1ODgxM2E0MTI2NzY4MzQ5MTZkOWVkYTA1M2U4YjM3NDM2MjEwMDllODRhMjIzZjQwNjBiNGYxYw'
		self.baseURLAppDev = 'https://emac-dev.arte.tv/api/emac/v3'
		self.tokenDev = ''
		self.playerURL = 'https://api.arte.tv/api'
		self.generalUrl = 'https://static-cdn.arte.tv/static/artevp/5.0.6/config/json/general.json'
		self._setLang()
		#https://api-preprod.arte.tv/api/opa/v3
		#https://api.arte.tv/api/opa/v3/
		#https://static-cdn.arte.tv/static-preprod/artevp
		#https://player-v5-dev.arte.tv/static/artevp/5.0.6/config/json/general.json

	def parseHome(self):
		j = requests.get(f'{self.baseURL}/{self.lang}/web/HOME/').json()
		for zone in j['zones']:
			d = {'type':'dir', 'params':{'mode':'libArteListData'}, 'metadata':{'art':{}}}
			if zone['code']['name'] != None:
				d['metadata']['name'] = zone['title']
				d['params']['code'] = zone['code']['name']
				self.result['items'].append(d)
		return self.result
		

	def parseDataCode(self,code='playlists_HOME',data='MANUAL_TEASERS'):
		return self._getData(f'{self.baseURL}/{self.lang}/web/data/{data}/?imageFormats=square,landscape,banner,portrait&code={code}&page=1&limit=100')

	def parseData(self,data,uriParams):
		url = f'{self.baseURL}/{self.lang}/web/data/{data}/?imageFormats=square,landscape,banner,portrait&page=1&limit=100'
		print(url)
		print(uriParams)
		for k,v in json.loads(uriParams).items():
			url += f'&{k}={v}'
		print(url)
		return self._getData(url)

	def _getData(self,url):
		j = requests.get(url, headers=headers).json()
		for item in j['data']:
			if item['kind']['code'] == 'SHOW' or item['kind']['code'] == 'BONUS':
				d = {'type':'video', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}}
				d['metadata']['duration'] = item['duration']
				d['metadata']['mpaa'] = item['ageRating']
				d['params']['programId'] = item['programId']
			elif item['kind']['code'] == 'LIVE_EVENT':
				d = {'type':'video', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}}
				d['metadata']['mpaa'] = item['ageRating']
				d['params']['programId'] = item['programId']
			else:
				#d = {'type':'dir', 'params':{'mode':'libArteListCollection'}, 'metadata':{'art':{}}}
				#d['params']['collectionId'] = item['programId']
				d = {'type':'dir', 'params':{'mode':'libArteListData', 'data':'COLLECTION_VIDEOS'}, 'metadata':{'art':{}}}
				d['params']['uriParams'] = f'{{"collectionId":"{item["programId"]}"}}'
			#d['metadata']['name'] = item['title']
			d['metadata']['tvshowtitle'] = item['title']
			if item['subtitle'] != None:
				d['metadata']['name'] = item['subtitle']
			else:
				d['metadata']['name'] = item['title']
			d['metadata']['plot'] = item['shortDescription']
			d['metadata']['plotoutline'] = item['subtitle']
			if item['images']['landscape'] != None:
				d['metadata']['art']['thumb'] = item['images']['landscape']['resolutions'][2]['url']
				d['metadata']['art']['fanart'] = item['images']['landscape']['resolutions'][2]['url']
			if item['images']['banner'] != None:
				d['metadata']['art']['banner'] = item['images']['banner']['resolutions'][2]['url']
			if item['images']['square'] != None:
				d['metadata']['art']['icon'] = item['images']['square']['resolutions'][2]['url']
			if item['images']['portrait'] != None:
				d['metadata']['art']['poster'] = item['images']['portrait']['resolutions'][2]['url']

			self.result['items'].append(d)
		return self.result

		
	def parseCollection(self,collectionId):
		#j = requests.get(f'{self.baseURL}/{self.lang}/web/data/COLLECTION_VIDEOS/?collectionId={collectionId}&page=1&limit=100', headers=headers).json()
		#self._getShows(j)
		url = f'{self.baseURL}/{self.lang}/web/data/COLLECTION_VIDEOS/?collectionId={collectionId}&page=1&limit=100'
		self._getData(url)
		return self.result

	def _getShows(self,j):
		for item in j['data']:
			d = {'type':'video', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}}
			
			d['metadata']['tvshowtitle'] = item['title']
			if item['subtitle'] != None:
				d['metadata']['name'] = item['subtitle']
			else:
				d['metadata']['name'] = item['title']

			d['metadata']['duration'] = item['duration']
			d['metadata']['mpaa'] = item['ageRating']
			d['metadata']['art']['thumb'] = item['images']['landscape']['resolutions'][2]['url']

			d['params']['programId'] = item['programId']
			self.result['items'].append(d)

		

	def parsePagesShows(self,uri):
		self.result['content'] = 'tvshows'
		print(f'{self.baseURL}/{self.lang}/web/pages/{uri}')
		j = requests.get(f'{self.baseURL}/{self.lang}/web/pages/{uri}').json()
		for item in j['zones'][0]['data']:
			d = {'type':'dir', 'params':{'mode':'libArteListCollection'}, 'metadata':{'art':{}}}
			
			d['metadata']['name'] = item['title']
			d['metadata']['plotoutline'] = item['subtitle']
			d['metadata']['plot'] = item['shortDescription']
			d['metadata']['art']['thumb'] = item['images']['landscape']['resolutions'][2]['url']

			d['params']['programId'] = item['programId']
			d['params']['collectionId'] = item['programId']
			self.result['items'].append(d)
		#try:
		#	self.result['pagination']['pages'].append(d)

		return self.result

	def parsePagesVideos(self,uri,content='videos'):
		self.result['content'] = content
		print(f'{self.baseURL}/{self.lang}/web/pages/{uri}')
		j = requests.get(f'{self.baseURL}/{self.lang}/web/pages/{uri}').json()
		for item in j['zones'][0]['data']:
			#d = {'type':'dir', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}, 'type': 'video'}
			if item['type'] == 'teaser':
				d = {'type':'video', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}}
			else:
				d = {'type':'dir', 'params':{'mode':'libArteListCollection'}, 'metadata':{'art':{}}}
			
			d['metadata']['name'] = item['title']
			d['metadata']['plot'] = item['shortDescription']
			d['metadata']['duration'] = item['duration']
			d['metadata']['mpaa'] = item['ageRating']
			d['metadata']['art']['thumb'] = item['images']['landscape']['resolutions'][2]['url']

			d['params']['programId'] = item['programId']
			d['params']['collectionId'] = item['programId']
			self.result['items'].append(d)
		#try:
		#	self.result['pagination']['pages'].append(d)

		return self.result


	def parseDate(self,date='2020-01-30'):
		j = requests.get(f'{self.baseURL}/{self.langGuide}/app/pages/TV_GUIDE/?day={date}').json()
		for item in j['zones'][1]['data']:
			d = {'type':'video', 'params':{'mode':'libArtePlayWeb'}, 'metadata':{'art':{}}}
			#d = {'type':'dir', 'params':{'mode':'libArteListCollection'}, 'metadata':{'art':{}}, 'type': 'dir'}
			
			d['metadata']['name'] = item['title']
			d['metadata']['duration'] = item['duration']
			d['metadata']['mpaa'] = item['ageRating']
			d['metadata']['plot'] = item['shortDescription']
			d['metadata']['art']['thumb'] = item['images']['landscape']['resolutions'][2]['url']

			d['params']['programId'] = item['programId']
			d['params']['collectionId'] = item['programId']
			self.result['items'].append(d)
		return self.result


	def _setLang(self):
		availableLanguages = ['en','de','es','fr','it','pl',]
		s = lm4utils.getSetting('language')
		if s == 'system' or s == '':
			l = lm4utils.getISO6391()
			if l in availableLanguages:
				self.lang = l
				self.langGuide = l
			else:
				self.lang = 'en'
				self.langGuide = 'en'
		else:
			self.lang = s
			self.langGuide = s















	
'''
def getVideos(url):
	l = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	for video in j['videos']:
		d = {}
		#d['_name'] = video['title']
		if video['subtitle'] != None:
			d['_name'] = video['subtitle']
		else:
			d['_name'] = video['title']
		
		d['_tvshowtitle'] = video['title']
		if video['imageUrl'] != None:
			d['_thumb'] = video['imageUrl']
		if video['durationSeconds'] != None:
			d['_duration'] = str(video['durationSeconds'])
		if video['teaserText'] != None:
			d['_plotoutline'] = video['teaserText']
			d['_plot'] = video['teaserText']
		if video['fullDescription'] != None:
			d['_plot'] = video['fullDescription']
		elif video['shortDescription'] != None:
			d['_plot'] = video['shortDescription']
		#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+video['programId']+'/'+video['kind']+'/'+video['platform']+'/de/DE'
		d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+video['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
		d['mode'] = 'libArtePlay'
		d['_type'] = 'date'
		l.append(d)
	if j['meta']['page'] < j['meta']['pages']:
		d = {}
		d['url'] = url.split('&page=')[0] + '&page=' + str(j['meta']['page'] + 1)
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l

def getAZ():
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/home/de')
	#response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/home/v2/de')#TODO
	j = json.loads(response)
	for mag in j['teasers']['magazines']:
		d = {}
		d['_name'] = mag['label']['de']
		d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/' + mag['url'] + '/de'
		d['_channel'] = 'Arte'
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l
	
def getPlaylists():#,playlists, highlights
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/home/de')
	j = json.loads(response)
	for playlist in j['teasers']['playlists']:
		d = {}
		d['_name'] = playlist['title']
		d['_subtitle'] = playlist['subtitle']
		d['_thumb'] = playlist['imageUrl']
		d['_plot'] = playlist['teaserText']
		d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/PLAYLIST/' + playlist['programId'] + '/de'
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l
		
	
	
def getDate(yyyymmdd):
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/programs/'+yyyymmdd+'/de')
	j = json.loads(response)
	for program in j['programs']:
		if program['video'] != None:
			d = {}
			#d['_airedtime'] = program['broadcast']['broadcastBeginRounded'].split(' ')[-2][:5]
			s = program['broadcast']['broadcastBeginRounded'].split(' ')[-2].split(':')
			d['_airedtime'] = str(int(s[0]) + 1) + ':' + s[1]
			if len(d['_airedtime']) == 4:
				d['_airedtime'] = '0' + d['_airedtime']
			d['_name'] = program['program']['title']
			#d['url'] = 'http://www.arte.tv/papi/tvguide/videos/stream/player/D/'+program['video']['emNumber']+'_PLUS7-D/ALL/ALL.json'
			#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/SHOW/ARTEPLUS7/de/DE'
			#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/'+program['video']['kind']+'/'+program['video']['platform']+'/de/DE'
			
			d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+program['video']['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
			#d['programId'] = program['video']['programId']
			
			if program['video']['imageUrl'] != None:
				d['_thumb'] = program['video']['imageUrl']
			if program['video']['durationSeconds'] != None:
				d['_duration'] = str(program['video']['durationSeconds'])
			if program['video']['teaserText'] != None:
				d['_plotoutline'] = program['video']['teaserText']
				d['_plot'] = program['video']['teaserText']
			if program['video']['fullDescription'] != None:
				d['_plot'] = program['video']['fullDescription']
			d['mode'] = 'libArtePlay'
			d['_type'] = 'date'
			l.append(d)
	return l

def getDateNew(yyyymmdd):
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/guideTV/v2/day/'+yyyymmdd+'/de')
	j = json.loads(response)
	for program in j['programs']:
		d = {}
		#"Tue, 01 Oct 2019 03:00:00 +0000"
		"""
		t = program['broadcastDate'].split(', ')[1]
		libMediathek.log(t)
		broadcastDate = datetime.strptime(t,'%d %b %Y %H:%M:%S')
		d['date'] = broadcastDate.strftime('%Y%m%d')
		d['_airedtime'] = broadcast.strftime('%H:%M')
		"""
		#d['date'] = broadcastDate.strftime('%Y%m%d')
		d['_airedtime'] = program['broadcastDate'][17:19]+':'+program['broadcastDate'][20:22]

		d['_duration'] = str(int(program['duration']*60))
		
		d['_name'] = program['title']
		#d['url'] = 'http://www.arte.tv/papi/tvguide/videos/stream/player/D/'+program['video']['emNumber']+'_PLUS7-D/ALL/ALL.json'
		#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/SHOW/ARTEPLUS7/de/DE'
		#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/'+program['video']['kind']+'/'+program['video']['platform']+'/de/DE'
		
		d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+program['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
		#d['programId'] = program['video']['programId']
		
		if program['imageUrl'] != None:
			d['_thumb'] = program['imageUrl']
		if program['teaserText'] != None:
			d['_plotoutline'] = program['teaserText']
			d['_plot'] = program['teaserText']
		if program['shortDescription'] != None:
			d['_plot'] = program['shortDescription']
		d['mode'] = 'libArtePlay'
		d['_type'] = 'date'

		for sticker in program['stickers']:
			if sticker['code'] == 'FULL_VIDEO':
				l.append(d)
		
	return l

def getSearch(s):
	l = []
	url = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/search/text/'+urllib.quote_plus(s)+'/de'
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	#http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/MAGAZINE/RC-014077/de
	for teaser in j['teasers']:
		d = {}
		d['_name'] = teaser['title']
		d['_tvshowtitle'] = teaser['title']
		if teaser['imageUrl'] != None:
			d['_thumb'] = teaser['imageUrl']
		if teaser['kind'] == 'PLAYLIST' or teaser['kind'] == 'TV_SERIES' or teaser['kind'] == 'TOPIC':
			d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/MAGAZINE/'+teaser['programId']+'/de'
			d['mode'] = 'libArteListVideos'
			d['_type'] = 'dir'
			l.append(d)
		elif teaser['kind'] == 'SHOW':
			d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+teaser['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
			d['mode'] = 'libArtePlay'
			d['_type'] = 'video'
			l.append(d)
		else:
			libMediathek.log('unsupported kind found: '+teaser['kind'])
	return l


preferences = {
				'ignore':0,
				'FR':1,
				'OV':2,
				'OMU':3,
				'DE':4,}
	
languages = {
				'FR':'FR',
				'OMU':'DE',
				'DE':'DE'}
				
bitrates = {
				'EQ':800,
				'HQ':1500,
				'SQ':2200,}
	
#legend:
#
#VO Original Voice	
#VOA Original Voice	Allemande
#VOF Original Voice Francaise
#VA Voice Allemande
#VF Voice Francaise
#VAAUD Audio Description Allemande
#VFAUD Audio Description Francaise
#VE* Other Voice
#
#STA Subtitle Allemande
#STF Subtitle Francaise
#STE* Subtitle Other
#STMA Subtitle Mute Allemande
#STMF Subtitle Mute Francaise
#
#* is always followed by the provided language
#[ANG] English
#[ESP] Spanish
#[POL] Polish
#
#examples:
#VOF-STE[ANG] original audio (french), english subtitles
#VOA-STMA orignal audio (german), with french mute sutitles

lang = {
		'VO':'ov',
		'OmU':'ov',
		'VA':'de',
		'VF':'fr',
		'VA-STA':'de',
		'VF-STF':'fr',
		
		'VOA':'de',
		'VOF':'fr',
		'VOA-STA':'omu',
		'VOA-STE':'omu',
		'VOF-STA':'omu',
		'VOF-STE':'omu',
		'VAAUD':'de',
		'VFAUD':'fr',
		'VE[ANG]':'en',
		'VE[ESP]':'es',
		'VE[POL]':'pl',
		
		'STA':'de',
		'STF':'fr',
		'STMA':'de',
		'STMF':'fr',
		'STE[ANG]':'en',
		'STE[ESP]':'es',
		'STE[POL]':'pl',
}
def getVideoUrl(url):
	d = {}
	d['media'] = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	storedLang = 0
	for stream in j['videoStreams']:
		properties = {}
		properties['url'] = stream['url']
		properties['bitrate'] = bitrates[stream['quality']]
		
		s = stream['audioCode'].split('-')
		properties['lang'] = lang[s[0]]
		if s[0] == 'VAAUD' or s[0] == 'VFAUD':
			properties['audiodesc'] = True
		if len(s) > 1:
			properties['subtitlelang'] = lang[s[1]]
			if s[1] == 'STMA' or s[1] == 'STMF':
				properties['sutitlemute'] = True
		
		properties['type'] = 'video'
		properties['stream'] = 'MP4'
		d['media'].append(properties)
	return d
	
def getVideoUrlWeb(url):
	d = {}
	d['media'] = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	#for caption in j.get('captions',[]):
	#	if caption['format'] == 'ebu-tt-d-basic-de':
	#		d['subtitle'] = [{'url':caption['uri'], 'type':'ttml', 'lang':'de', 'colour':True}]
	#	#elif caption['format'] == 'webvtt':
	#	#	d['subtitle'] = [{'url':caption['uri'], 'type':'webvtt', 'lang':'de', 'colour':False}]
	storedLang = 0
	for key in j['videoJsonPlayer']['VSR']:#oh, this is such bullshit. there are endless and senseless permutations of language/subtitle permutations. i'll have to rewrite this in the future for french and other languages, subtitles, hearing disabled, ... who the hell uses baked in subtitles in 2017?!?!
		l = lang.get(j['videoJsonPlayer']['VSR'][key]['versionCode'].split('[')[0],'ignore').upper()
		if preferences.get(l,0) > storedLang and j['videoJsonPlayer']['VSR'][key]['mediaType'] == 'hls':
			storedLang = preferences.get(l,0)
			result = {'url':j['videoJsonPlayer']['VSR'][key]['url'], 'type': 'video', 'stream':'HLS'}
	d['media'].append(result)
	
	d['metadata'] = {}
	d['metadata']['name'] = j['videoJsonPlayer']['VTI']
	if 'VDE' in j['videoJsonPlayer']:
		d['metadata']['plot'] = j['videoJsonPlayer']['VDE']
	elif 'V7T' in j['videoJsonPlayer']:
		d['metadata']['plot'] = j['videoJsonPlayer']['V7T']
	d['metadata']['thumb'] = j['videoJsonPlayer']['VTU']['IUR']
	d['metadata']['duration'] = str(j['videoJsonPlayer']['videoDurationSeconds'])
	return d
	'''