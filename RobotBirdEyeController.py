"""
RobotBirdEyeController.py
@Knowblesse 2022
Robot control script for mecanum wheel robot developed in SM robotics lab
"""

from time import sleep, time

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import serial
import scipy.ndimage

###############################################################
#               Environment Dependent Constants               #
###############################################################
ROBOT_PORT = "COM3"
MOTION_URL = r'http://192.168.0.77:8081/'

###############################################################
#             Environment Independent Constants               #
###############################################################
robotColorRange = 50
rewardColorRange = 50
dangerColor = np.array([ 47, 56, 175]) # Danger indication color for visual input
dangerObjectSize = 100
punishCountLimit = 10
destinationThreshold = 30
movementUpdateInterval = 3


###############################################################
#                    Setup Connections                        #
###############################################################
# Setup Robot
robot = serial.Serial(ROBOT_PORT, 57600, timeout=0, rtscts=False)
if not robot.is_open:
    print('Serial Port is NOT Open')

# Setup Visual Input
vc_eye = cv.VideoCapture(MOTION_URL)
keyInput = -1
while keyInput < 0:
    ret, img = vc_eye.read()
    cv.imshow('Test Visual', img)
    keyInput = cv.waitKey(1)
cv.destroyWindow('Test Visual')

# Setup Birdeye Camera
vc = cv.VideoCapture(0)
ret, img = vc.read()
frame_size = [img.shape[0], img.shape[1]]
keyInput = -1
while keyInput < 0:
    ret, img = vc.read()
    cv.imshow('Test Birdeye Camera', img)
    keyInput = cv.waitKey(1)
cv.destroyWindow('Test Birdeye Camera')

###############################################################
#                    Setup Global Mask                        #
###############################################################
# Select Global Mask
ret, img = vc.read()
cv.putText(img, 'Select Global Mask', (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
mask_position = cv.selectROI('Select Global Mask', img)
cv.waitKey()
cv.destroyWindow('Select Global Mask')

global_mask = np.zeros(frame_size, dtype=np.uint8)
global_mask[mask_position[1]:mask_position[1] + mask_position[3], mask_position[0]:mask_position[0] + mask_position[2]] = 255

###############################################################
#                    Define simple functions                  #
###############################################################
def getFrame():
    _, img = vc.read()
    img = cv.bitwise_and(img, img, mask=global_mask)
    return img

def getKernel(size):
    size = int(size)
    return cv.getStructuringElement(cv.MORPH_ELLIPSE, (size, size),
                                    ((int((size - 1) / 2), int((size - 1) / 2))))

def findContoursByColor(img, targetColor, colorRange):
    binaryImage = cv.inRange(img, targetColor - colorRange, targetColor + colorRange)

    # Denoise
    denoisedBinaryImage = cv.morphologyEx(binaryImage, cv.MORPH_OPEN, getKernel(1))
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(20))

    # Find the contour
    cnts = cv.findContours(denoisedBinaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]

    return cnts


###############################################################
#        Select Target color for rewards and the robot        #
###############################################################
def selectTargetColor(targetName, colorRange, markerType, markerColor):
    # Open select ROI and select Target color and show detected object

    # Select robot Color
    img = getFrame()
    cv.putText(img, 'Select ' + targetName, (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
    loc = cv.selectROI('Select ' + targetName, img)
    cv.destroyWindow('Select ' + targetName)

    selectedImage = img[loc[1]:loc[1]+loc[3], loc[0]:loc[0] + loc[2], :]

    targetColor = np.median(np.reshape(selectedImage, (selectedImage.shape[0] * selectedImage.shape[1], -1), order='F'), 0)

    cnts = findContoursByColor(img, targetColor, colorRange)

    # Show detected object with mask
    img = getFrame()
    mask = np.zeros(frame_size, dtype=np.uint8)
    cv.drawContours(mask, cnts, -1, 255, -1)
    cv.threshold(mask, 10, 255, cv.THRESH_BINARY)
    img = cv.bitwise_and(img, img, mask=mask)

    cv.imshow(targetName + ' Position', img)
    cv.waitKey(3000)

    # Show object with marker
    img = getFrame()
    objectLocations = []
    for cnt in cnts:
        objectLocations.append(np.round(cv.minEnclosingCircle(cnt)[0]).astype(int))
        cv.drawMarker(img, objectLocations[-1], markerColor, markerType=markerType, thickness=3)

    cv.imshow(targetName + ' Position', img)
    cv.waitKey()
    cv.destroyWindow(targetName + ' Position')

    return [robotColor, objectLocations]

robotColor, robotLocations = selectTargetColor('Robot', 50, cv.MARKER_DIAMOND, (0, 0, 255))
rewardColor, rewardLocations = selectTargetColor('Reward', 50, cv.MARKER_STAR, (0, 255, 255))

if len(robotLocation) == 1:
    raise(BaseException("Wrong robot location"))

###############################################################
#                      Initialize States                      #
###############################################################

# Init. times
startTime = time()
lastLocationUpdateTime = startTime

# Init. states
isMoving = False
lastLocation = robotLocations[0]
global destination
destination = robotLocations[0]
robotMovementState_FB = 0
robotMovementState_LR = 0
command2send = ''
isPunishTriggered = False
punishCount = 0
lastDangerTime = 0 

# Define mouse double click callback function
def setDestination(event, x, y, flags, userData):
    if event == cv.EVENT_LBUTTONDBLCLK:
        global destination
        if len(rewardLocations) > 0:
            destination = rewardLocations.pop()
        else:
            destination = [x, y]
        print(f'Destination set : ({x} , {y})')

# Setup windows
cv.namedWindow('Main')
cv.namedWindow('Eye')
cv.setMouseCallback('Main', setDestination)


###############################################################
#                               Run!                          #
###############################################################
keyInput = -1
while keyInput < 0:

    # Get all image data for the current iteration
    img = getFrame()
    vc_eye = cv.VideoCapture(MOTION_URL)
    ret, img_eye = vc_eye.read()
    currentTime = time()
    
    ###########################################################
    #         Check the presence of the danger object         #
    ###########################################################
    # Logic :
    # 1. Assume there is only one danger object in the field.
    # 2. If, the robot did not encounter the danger object, (isPunishTriggered)
    #    check if the danger object exist in the field. 
    # 3. Check by the `dangerColor` first,
    #    then if the object is larger than `dangerObjectSize`,
    #    increase the `punishCount`.
    # 4. If the `punishCount` exceed `punishCountLimit`,
    #    give up the current destination (reward) and move on to the next destination.

    cnts = findContoursByColor(img_eye, dangerColor, 50)

    if not isPunishTriggered and len(cnts) > 0:
        largestContourIndex = np.argmax(np.array([cv.contourArea(cnt) for cnt in cnts]))
        largestContour = cnts[largestContourIndex]
        cv.drawContours(img_eye, largestContour, 0, (0, 100, 255), 3)
        punishSize = cv.contourArea(largestContour)
        if punishSize > dangerObjectSize:
            punishCount += 1
        if punishCount > punishCountLimit:
            lastDangerTime = currentTime
            isPunishTriggered = True
            isMoving = False
            robot.write('x'.encode())
            robotMovementState_FB = 0
            robotMovementState_LR = 0
            if len(rewardLocations) != 0:
                destination = rewardLocations.pop()
            else:
                break
            continue

    ###########################################################
    #                     Control robot                       #
    ###########################################################
    # Logic
    # 1. First, find robot. If fail, try in the next iteration.
    # 2. If the robot is found, check if the destination is far away from the robot.
    # 3. isMoving: True  | arrived to destination: False ==> adjust movement
    #    isMoving: True  | arrived to destination: True  ==> stop
    #    isMoving: False | arrived to destination: False ==> start moving 
    #    isMoving: False | arrived to destination: True  ==> do nothing

    cnts = findContoursByColor(img, robotColor, robotColorRange)

    if len(cnts) > 0:
        largestContourIndex = np.argmax(np.array([cv.contourArea(cnt) for cnt in cnts]))
        largestContours = cnts[largestContourIndex]
        # Find center and use as robot location
        center = np.round(cv.minEnclosingCircle(largestContours)[0]).astype(int)

        # If there is a difference between the destination and the current location,
        if ((center[0] - destination[0]) ** 2 + (center[1] - destination[1]) ** 2) ** 0.5 > destinationThreshold:
            if not isMoving:
                isMoving = True
                robot.write('wwww'.encode())
                robotMovementState_FB = 4
                print('Start moving')
            else: # if already moving, but not yet arrived,
                # For every {movementUpdateInterval} second, get velocity vector and adjust movement
                if (currentTime - lastLocationUpdateTime) > movementUpdateInterval:
                    vec_center = center - lastLocation
                    vec_destination = destination - lastLocation

                    if np.all(vec_center == 0):
                        print('not moved')
                        continue

                    degree_offset = -np.cross(vec_destination, vec_center) / (np.dot(vec_center, vec_center)**.5 * np.dot(vec_destination, vec_destination)**.5)
                    targetMovementState_FB = np.round((0.5 - np.abs(degree_offset))*3) + 3  # if perfectly aligned, FB = + 10
                    targetMovementState_LR = np.round(degree_offset*5) # if plus, turn right

                    command2send = \
                        int(np.max(targetMovementState_FB - robotMovementState_FB, 0)) * 'w' + \
                        int(np.max(robotMovementState_FB - targetMovementState_FB, 0)) * 's' + \
                        int(np.max(targetMovementState_LR - robotMovementState_LR, 0)) * 'd' + \
                        int(np.max(robotMovementState_LR - targetMovementState_LR, 0)) * 'a'

                    print(command2send)
                    robot.write(command2send.encode())

                    robotMovementState_FB = targetMovementState_FB
                    robotMovementState_LR = targetMovementState_LR

                    lastLocation = center
                    lastLocationUpdateTime = currentTime
        else: # Near destination
            if isMoving:
                isMoving = False
                robot.write('x'.encode())
                robotMovementState_FB = 0
                robotMovementState_LR = 0
                if len(rewardLocations) != 0:
                    destination = rewardLocations.pop()
                else:
                    break

        ###########################################################
        #                    Draw Camera Input                    #
        ###########################################################

        cv.putText(img, f"Foward Speed : {robotMovementState_FB}|{'Right' if robotMovementState_LR > 0 else 'Left'}{robotMovementState_LR}", (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8,
                   color=(255, 255, 255))
        cv.putText(img, command2send, (10, 60), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=.8,
                   color=(255, 255, 255))
        cv.arrowedLine(img, lastLocation, center, color=(0, 0, 255), thickness=2)
        cv.arrowedLine(img, lastLocation, destination, color=(255, 255, 255), thickness=2)
        cv.drawMarker(img, center, (255, 255, 0), markerType=cv.MARKER_STAR, thickness=2)
        cv.imshow('Main', img)
        if isPunishTriggered and (currentTime-lastDangerTime < 3):
            cv.putText(img_eye, "Danger!", (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
        cv.imshow('Eye', img_eye)
        keyInput = cv.waitKey(1)
        sleep(0.1)

cv.destroyWindow('Main')
cv.destroyWindow('Eye')
robot.write('x'.encode())

