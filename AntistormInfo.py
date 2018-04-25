class AntistormInfo:
    folderName = "" #nazwa_folderu
    fileName = "" #nazwa_pliku
    frontFileName = "" #nazwa_pliku_front
    
    def __init__(self, folderName, fileName, frontFileName):
        self.folderName = folderName
        self.fileName = fileName
        self.frontFileName = frontFileName

    def toString(self):
        return "folderName: {0}\nfileName: {1}\nfrontFileName: {2}".format(self.folderName, self.fileName, self.frontFileName)