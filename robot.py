import cv2 as cv
import requests
import numpy as np
import serial
import time

URL = r'http://choilab409.iptime.org:12345/'
THRESHOLD = 190
ANIMAL_SIZE = 500
ANIMAL_MAX_SIZE = 40000
sr = serial.Serial("COM3", 57600, timeout=0, rtscts=False)

if not sr.is_open:
    print('Serial Port is NOT Open')


# denoise
def getKernel(size):
    size = int(size)
    return cv.getStructuringElement(cv.MORPH_ELLIPSE, (size, size),
                                    ((int((size - 1) / 2), int((size - 1) / 2))))


def denoiseBinaryImage(binaryImage):
    """
    __denoiseBinaryImage : remove small artifacts from the binary Image using the cv.morphologyEx function
    :param binaryImage: boolean image
    :return: denoised binary image
    """
    # opening -> delete noise : erode and dilate
    # closing -> make into big object : dilate and erode
    denoisedBinaryImage = binaryImage
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_OPEN, getKernel(3))
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_OPEN, getKernel(5))
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(10))
    return denoisedBinaryImage


# Read Image
def checkAnimal(THRESHOLD):
    vc = cv.VideoCapture(URL)
    _, img = vc.read()

    binaryImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    binaryImg = cv.threshold(binaryImg, THRESHOLD, 255, cv.THRESH_TOZERO)[1]
    binaryImg = denoiseBinaryImage(binaryImg)
    cv.imshow('Robot', binaryImg)
    cv.waitKey(10)
    cnts = cv.findContours(binaryImg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]

    # Find the largest contour
    cnts = cv.findContours(binaryImg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]
    if len(cnts) == 0:
        return (0, 0)

    maxCntSize = 0
    maxCntIndex = None
    for j, cnt in enumerate(cnts):
        area = cv.contourArea(cnt)
        if area > maxCntSize:
            maxCntSize = area
            maxCntIndex = j
    img = cv.drawContours(img, cnts, maxCntIndex, [0, 0, 255], thickness=2)
    cv.imshow('Robot', img)
    cv.waitKey(1)

    center = cv.minEnclosingCircle(cnts[maxCntIndex])[0]

    return (maxCntSize, center)

    # img = cv.drawContours(img, cnts, maxCntIndex, [0,0,255], thickness=2)
    # cv.imshow('Robot', img)
    # cv.waitKey(0)
    # cv.destroyWindow('Robot')


startTime = time.time()
lastSendTime = startTime
while time.time() - startTime < 120:
    if time.time() - lastSendTime > 0.2:
        lastSendTime = time.time()
        animalLevel, center = checkAnimal(THRESHOLD)
        if animalLevel < ANIMAL_SIZE:
            print(f'animalNotFound {animalLevel}')
            sr.write('xaaaaaaaaaa'.encode())
        else:
            if animalLevel > ANIMAL_MAX_SIZE:
                sr.write('x'.encode())
                print('Collision Alert')
            else:
                print(f'animalFound {animalLevel}')
                if np.abs(center[0] - 320) < 100:
                    sr.write('xwwwwwwwwwwwww'.encode())
                    print('Run!')
                else:
                    if center[0] < 320:
                        sr.write('xaaaaa'.encode())
                        print('go left')
                    else:
                        sr.write('xddddd'.encode())
                        print('go right')

sr.write('x'.encode())