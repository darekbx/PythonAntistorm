import requests
import os
import shutil
from PIL import Image
from StringIO import StringIO

from AntistormInfo import AntistormInfo

class AntiStormGenerator:
	host = 'https://antistorm.eu'
	apiAddress = "{0}/ajaxPaths.php?lastTimestamp=0&type=radar"
	mapAddress = "{0}/map/final-map.png"
	windAddress = "{0}/archive/{1}/{2}-radar-velocityMapImg.png"
	probabilityAddress = "{0}/archive/{1}/{2}-radar-probabilitiesImg.png"
	rainAddress = "{0}/visualPhenom/{1}-radar-visualPhenomenon.png"
	stormAddress = "{0}/visualPhenom/{1}-storm-visualPhenomenon.png"

	colorSpace = 'RGBA'
	apiDelimiter = '<br>'
	imageExtension = '.png'
	imagesTempDir = 'temp'
	expectedChunksCount = 6
	targetSize = 350, 350

	def createFullMap(self):
		antistormInfo = self.loadInfo()
		if antistormInfo is not None:
			urls = self.createUrls(antistormInfo)

			self.createOrEraseTemp()
			for index, url in enumerate(urls):
				self.downloadAndResizeImage(url, index)
			
			self.concatImages()

	def createUrls(self, antistormInfo):
		windUrl = self.windAddress.format(self.host, antistormInfo.folderName, antistormInfo.fileName)
		probabilityUrl = self.probabilityAddress.format(self.host, antistormInfo.folderName, antistormInfo.fileName)
		rainUrl = self.rainAddress.format(self.host, antistormInfo.frontFileName)
		stormUrl = self.stormAddress.format(self.host, antistormInfo.frontFileName)
		mapUrl = self.mapAddress.format(self.host)
		return [windUrl, probabilityUrl, rainUrl, stormUrl, mapUrl] 

	def downloadAndResizeImage(self, address, index):
		try:
			imageResponse = requests.get(address)
			image = Image.open(StringIO(imageResponse.content)).convert(self.colorSpace)
			image.thumbnail(self.targetSize, Image.ANTIALIAS)
			image.save(os.path.join(self.imagesTempDir, "image_{0}{1}".format(index, self.imageExtension)), 'png')
		except Exception as e:
			print e

	def concatImages(self):
		images = self.findImages()
		images.sort()
		imagesMap = map(Image.open, images)

		blended = Image.blend(imagesMap[2], imagesMap[1], alpha=0.3) # append rain
		blended = Image.alpha_composite(blended, imagesMap[3]) # append storm
		blended = Image.alpha_composite(blended, imagesMap[0]) # append wind
		blended = Image.alpha_composite(imagesMap[4], blended) # append map
		
		blended.save('out.png', 'png')
		
	def findImages(self):
		files = os.listdir(self.imagesTempDir)
		images = []
		for file in files:
			if file.find(self.imageExtension) == -1:
				continue
			images.append(os.path.join(self.imagesTempDir, file))
		return images
	
	def createOrEraseTemp(self):
		if not os.path.exists(self.imagesTempDir):
			os.makedirs(self.imagesTempDir)
		else:
			shutil.rmtree(self.imagesTempDir)
			os.makedirs(self.imagesTempDir)

	def loadInfo(self):
		try:
			apiResponse = requests.get(self.apiAddress.format(self.host))
			content = apiResponse.content
			chunks = content.split(self.apiDelimiter)
			
			if len(chunks) != self.expectedChunksCount:
				raise Exception('Invalid chunks size')

			folderName = self.parseChunk(chunks[1])
			fileName = self.parseChunk(chunks[2])
			frontFileName = self.parseChunk(chunks[3])
			return AntistormInfo(folderName, fileName, frontFileName)
		except Exception as e:
			print e
			return None
		
	# Chunk:
	# Sample: nazwa_pliku:15-20,15-10,15-0,14-50,14-40,14-30,14-20,14-10,14-0,13-50
	# name:token,token...
	def parseChunk(self, chunk, itemIndex = 0):
		tokensIndex = chunk.find(':')
		if tokensIndex is -1:
			raise Exception('Missing tokens separator')
		tokensString = chunk[(tokensIndex + 1):]
		tokens = tokensString.split(',')
		return tokens[itemIndex]


AntiStormGenerator().createFullMap()