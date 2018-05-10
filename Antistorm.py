import requests
import os
import shutil
import timeit
from PIL import Image, ImageDraw
from StringIO import StringIO

import sys
sys.path.insert(0, './display/')

from display import refreshDisplay

from AntistormInfo import AntistormInfo

class AntiStormGenerator:
    host = 'https://antistorm.eu'
    apiAddress = "{0}/ajaxPaths.php?lastTimestamp=0&type=radar"
    mapAddress = "{0}/map/final-map.png"
    rainAddress = "{0}/visualPhenom/{1}-radar-visualPhenomenon.png"
    stormAddress = "{0}/visualPhenom/{1}-storm-visualPhenomenon.png"

    colorSpace = 'RGBA'
    apiDelimiter = '<br>'
    imageExtension = '.png'
    imagesTempDir = 'temp'
    outputImage = 'out.png'
    mapImage = 'map.png'
    expectedChunksCount = 6
    targetSize = (350, 350)
    einkSize = (176, 264)
    warsawPosition = (230, 135)
    warsawPositionColor = (250, 50, 0)

    def createFullMap(self):
        computationStart = timeit.default_timer()
        antistormInfo = self.loadInfo()
        if antistormInfo is not None:
            urls = self.createUrls(antistormInfo)
            self.createOrEraseTemp()
            for index, url in enumerate(urls):
                self.downloadAndResizeImage(url, index)
            self.concatImages()
            self.printComputationTime(computationStart)
            refreshDisplay()

    def printComputationTime(self, computationStart):
        computationStop = timeit.default_timer()
        computationTime = computationStop-computationStart
        print "Generated in: {0:.2f}s".format(computationTime)

    def createUrls(self, antistormInfo):
        rainUrl = self.rainAddress.format(
            self.host, antistormInfo.frontFileName)
        stormUrl = self.stormAddress.format(
            self.host, antistormInfo.frontFileName)
        mapUrl = self.mapAddress.format(self.host)
        return [rainUrl, stormUrl, mapUrl]

    def downloadAndResizeImage(self, address, index):
        try:
            imageResponse = requests.get(address)
            image = Image.open(StringIO(imageResponse.content)).convert(self.colorSpace)
            image.thumbnail(self.targetSize, Image.ANTIALIAS)
            image.save(os.path.join(self.imagesTempDir, "image_{0}{1}".format(
                index, self.imageExtension)), 'png')
        except Exception as e:
            print e

    def concatImages(self):
        images = self.findImages()
        images.sort()

        rainImage = Image.open(images[0])
        stormImage = Image.open(images[1])
        mapImage = Image.open(images[2])

        blended = Image.alpha_composite(rainImage, stormImage)
        bg = Image.new(self.colorSpace, self.targetSize, "white")
        bg.paste(blended, (0,0), blended)
		
        self.markWarsaw(bg)

        leftOffset = 120
        cropped = bg.crop((leftOffset, 0, self.einkSize[0] + leftOffset, self.einkSize[1])) 
        cropped.save(self.outputImage, 'png')

        mapImage = mapImage.crop((leftOffset, 0, self.einkSize[0] + leftOffset, self.einkSize[1])) 
        mapImage.save(self.mapImage, 'png')

    def markWarsaw(self, image):
        draw = ImageDraw.Draw(image)
        dotSize = 2
        x = self.warsawPosition[0]
        y = self.warsawPosition[1]
        left = x - dotSize
        top = y - dotSize
        right = x + dotSize
        bottom = y + dotSize
        draw.ellipse((left, top, right, bottom), fill=self.warsawPositionColor)

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
    def parseChunk(self, chunk, itemIndex=0):
        tokensIndex = chunk.find(':')
        if tokensIndex is -1:
            raise Exception('Missing tokens separator')
        tokensString = chunk[(tokensIndex + 1):]
        tokens = tokensString.split(',')
        return tokens[itemIndex]


AntiStormGenerator().createFullMap()
