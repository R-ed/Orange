import struct
import imghdr
import os
import random

#Got the function below from https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
def getImageSize(imagePath):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(imagePath, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(imagePath) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(imagePath) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(imagePath) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

#Got the function below from https://stackoverflow.com/questions/120656/directory-listing-in-python
def getAllFilePaths(dirPath):

    listOfFiles = []

    for dirname, dirnames, filenames in os.walk(dirPath):

        # print path to all filenames.
        for filename in filenames:
            if(filename != None):
                listOfFiles.append(dirname + "/" + filename)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

    return listOfFiles

def makeTrendline(dataPoints):
    
    m = 0
    b = 0

    sumX = 0
    sumY = 0
    sumXY = 0
    sumXSquared = 0
    numOfData = len(dataPoints)
    for x, y in dataPoints:
        sumX = sumX + x
        sumY = sumY + y
        sumXY = sumXY + (x*y)
        sumXSquared = sumXSquared + (x**2)

    #Equation of the slope and y-intercept I got from http://classroom.synonym.com/calculate-trendline-2709.html
    m = ((numOfData*sumXY) - (sumX*sumY))/((numOfData*sumXSquared) - (sumX**2))
    b = (sumY - (m*sumX))/numOfData

    return m, b

def populateDataPoints(dirPath):
    '''create data points given training data'''
    trainingDataDimensions = []
    listOfData = getAllFilePaths(dirPath)
    x = 0

    for data in listOfData:
        (length, width) = getImageSize(data)
        trainingDataDimensions.append((x, (length/width)))
        x = x + 1

    return trainingDataDimensions

def isItOrange(image):

    likelyPercentage = 0
    #randomX = random.uniform(0,4)
    (m, b) = makeTrendline(populateDataPoints('trainingData'))
    trendlineY = (m*2) + b
    (length, width) = getImageSize(image)
    ratio = length / width

    if(ratio <= trendlineY):
        likelyPercentage = (ratio / trendlineY) * 100
    else:
        likelyPercentage = (trendlineY / ratio) * 100

    return "I'm " + str(round(likelyPercentage, 2)) + "%" + " sure that the image you sent me is an orange."

if __name__ == '__main__':
    print(isItOrange('./orange.png'))