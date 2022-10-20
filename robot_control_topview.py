import cv2 as cv
import numpy as np
from time import sleep, time
import serial
import matplotlib.pyplot as plt
import scipy.ndimage


# Setup Robot
robot = serial.Serial("COM3", 57600, timeout=0, rtscts=False)

if not robot.is_open:
    print('Serial Port is NOT Open')

# Setup Eye
URL = r'http://192.168.0.77:8081/'
THRESHOLD = 190
ANIMAL_SIZE = 500
punishColor = np.array([ 47., 56., 175.])
vc_eye = cv.VideoCapture(URL)
keyInput = -1
while keyInput < 0:
    ret, img = vc_eye.read()
    cv.imshow('Test', img)
    keyInput = cv.waitKey(1)
cv.destroyWindow('Test')

# Setup VideoCapture
vc = cv.VideoCapture(0)
ret, img = vc.read()
frame_size = [img.shape[0], img.shape[1]]
keyInput = -1
while keyInput < 0:
    ret, img = vc.read()
    cv.imshow('Test', img)
    keyInput = cv.waitKey(1)
cv.destroyWindow('Test')

# Select Global Mask
#mask_position = (30, 27, 589, 430)
ret, img = vc.read()
cv.putText(img, 'Select Global Mask', (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
mask_position = cv.selectROI('Select Global Mask', img)
cv.waitKey()
cv.destroyWindow('Select Global Mask')

global_mask = np.zeros(frame_size, dtype=np.uint8)
global_mask[mask_position[1]:mask_position[1] + mask_position[3], mask_position[0]:mask_position[0] + mask_position[2]] = 255

# Select Operation Range
#operation_range = np.array([149, 112, 382, 228])
ret, img = vc.read()
cv.putText(img, 'Select Operation Range', (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
operation_range = np.array(cv.selectROI('Select Operation Range', img))
cv.destroyWindow('Select Operation Range')

# Define proprocess filter
def getFrame():
    ret, img = vc.read()
    img = cv.bitwise_and(img, img, mask=global_mask)
    img = cv.rectangle(img, operation_range[0:2], operation_range[0:2] + operation_range[2:4], color=(0,0,255), thickness=2)
    return img

def getKernel(size):
    size = int(size)
    return cv.getStructuringElement(cv.MORPH_ELLIPSE, (size, size),
                                    ((int((size - 1) / 2), int((size - 1) / 2))))
##################################
#         Robot Processing       #
##################################

# Select robot Color
# robot = np.array([ 25.0959596 ,  28.28787879, 171.15151515])
img = getFrame()
cv.putText(img, 'Select Robot', (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
loc = cv.selectROI('Select Robot', img)
cv.destroyWindow('Select Robot')

selectedImage = img[loc[1]:loc[1]+loc[3], loc[0]:loc[0] + loc[2], :]

# Get color (b,g,r)
robotColor = np.median(np.reshape(selectedImage, (selectedImage.shape[0] * selectedImage.shape[1], -1), order='F'), 0)
RANGE = 50


binaryImage = cv.inRange(img, robotColor - RANGE, robotColor + RANGE)

# Denoise
denoisedBinaryImage = cv.morphologyEx(binaryImage, cv.MORPH_OPEN, getKernel(1))
denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(20))

# Find the contour
cnts = cv.findContours(denoisedBinaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]

img = getFrame()
rewardMask = np.zeros(frame_size, dtype=np.uint8)
cv.drawContours(rewardMask, cnts, -1, 255, -1)
cv.threshold(rewardMask, 10, 255, cv.THRESH_BINARY)
img = cv.bitwise_and(img, img, mask=rewardMask)

cv.imshow('Robot Position', img)
cv.waitKey(3000)

img = getFrame()

robotLocation = np.round(cv.minEnclosingCircle(cnts[0])[0]).astype(int)
cv.drawMarker(img, robotLocation, (0, 0, 255), markerType=cv.MARKER_DIAMOND, thickness=3)

cv.imshow('Robot Position', img)
cv.waitKey()
cv.destroyWindow('Robot Position')

##################################
#        Reward Processing       #
##################################
# Select Reward Color
img = getFrame()
cv.putText(img, 'Select Reward', (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8, color=(255, 255, 255))
loc = cv.selectROI('Select Reward', img)
cv.destroyWindow('Select Reward')

selectedImage = img[loc[1]:loc[1]+loc[3], loc[0]:loc[0] + loc[2], :]

# Get color (b,g,r)
rewardColor = np.median(np.reshape(selectedImage, (selectedImage.shape[0] * selectedImage.shape[1], -1), order='F'), 0)

binaryImage = cv.inRange(img, rewardColor - 20, rewardColor + 20)

# Denoise
denoisedBinaryImage = cv.morphologyEx(binaryImage, cv.MORPH_OPEN, getKernel(1))
denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(20))

# Find the contour
cnts = cv.findContours(denoisedBinaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]

img = getFrame()
rewardMask = np.zeros(frame_size, dtype=np.uint8)
cv.drawContours(rewardMask, cnts, -1, 255, -1)
cv.threshold(rewardMask, 10, 255, cv.THRESH_BINARY)
img = cv.bitwise_and(img, img, mask=rewardMask)

cv.imshow('Reward Position', img)
cv.waitKey(1500)

img = getFrame()
rewardLocations = []
for cnt in cnts:
    rewardLocations.append(np.round(cv.minEnclosingCircle(cnt)[0]).astype(int))
    cv.drawMarker(img, rewardLocations[-1], (0, 255, 255), markerType=cv.MARKER_STAR, thickness=3)

cv.imshow('Reward Position', img)
cv.waitKey()
cv.destroyWindow('Reward Position')


#############################
# Show Contour Graph
def drawContourGraph():
    rewardMatrix = np.zeros(frame_size)
    for loc in rewardLocations:
        rewardMatrix[loc[0], loc[1]] = 1

    rewardMatrix = scipy.ndimage.gaussian_filter(rewardMatrix, 50) * 200

    fig = plt.figure()
    ax = fig.subplots(1,3)
    ax[0].imshow(rewardMatrix, 'jet')







startTime = time()

lastTurnTime = time()
lastLocationTime = time()
lastDangerTime = 0
lastLocation = []

isFirstIteration = True
isMoving = False
global destination
DESTINATION_THRESHOLD = 30
MOVEMENT_UPDATE_INTERVAL = 3

def setDestination(event, x, y, flags, userData):
    if event == cv.EVENT_LBUTTONDBLCLK:
        global destination
        destination = [x, y]
        destination = rewardLocations.pop()
        print(f'Destination set : ({x} , {y})')


cv.namedWindow('Main')
cv.setMouseCallback('Main', setDestination)

robotMovementState_FB = 0
robotMovementState_LR = 0
command2send = ''


#destination = rewardLocations.pop()
isPunishTriggered = False
punishCount = 0
keyInput = -1
while keyInput < 0:
    img = getFrame()
    vc_eye = cv.VideoCapture(URL)
    ret, img_eye = vc_eye.read()
    currentTime = time()

    ######### Eye Image ###############
    binaryImage = cv.inRange(img_eye, punishColor - 50, punishColor + 50)

    # Denoise
    denoisedBinaryImage = cv.morphologyEx(binaryImage, cv.MORPH_OPEN, getKernel(2))
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(10))

    cnts = cv.findContours(denoisedBinaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]
    punishSize = 0
    if not isPunishTriggered and len(cnts) > 0:
        largestContourIndex = np.argmax(np.array([cv.contourArea(cnt) for cnt in cnts]))
        largestContour = cnts[largestContourIndex]
        cv.drawContours(img_eye, largestContour, 0, (0, 100, 255), 3)
        punishSize = cv.contourArea(largestContour)
        if punishSize > 100:
            punishCount += 1
            print(punishCount)
        if punishCount > 10:
            print("triggered")
            lastDangerTime = currentTime
            isPunishTriggered = True
            isMoving = False
            robot.write('x'.encode())
            robotMovementState_FB = 0
            robotMovementState_LR = 0
            # destination = center
            if len(rewardLocations) != 0:
                destination = rewardLocations.pop()
            else:
                break
            continue


    ######### Top Image ##################
    # Mask Color
    binaryImage =cv.inRange(img, robotColor - RANGE, robotColor + RANGE)

    # Denoise
    denoisedBinaryImage = cv.morphologyEx(binaryImage, cv.MORPH_OPEN, getKernel(2))
    denoisedBinaryImage = cv.morphologyEx(denoisedBinaryImage, cv.MORPH_CLOSE, getKernel(10))

    # Find the largest contour
    cnts = cv.findContours(denoisedBinaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]

    if len(cnts) > 0:
        largestContourIndex = np.argmax(np.array([cv.contourArea(cnt) for cnt in cnts]))
        largestContours = cnts[largestContourIndex]

        # Find center
        center = np.round(cv.minEnclosingCircle(largestContours)[0]).astype(int)

        # On the first trial,
        # Set the last location and the destination
        if isFirstIteration:
            isFirstIteration = False
            destination = center
            #destination = rewardLocations[0]
            lastLocation = center
            lastLocationTime = currentTime
        else:
            # If there is a difference between the destination and the current location,
            if ((center[0] - destination[0]) ** 2 + (center[1] - destination[1]) ** 2) ** 0.5 > DESTINATION_THRESHOLD:
                if not isMoving:
                    isMoving = True
                    robot.write('wwww'.encode())
                    robotMovementState_FB = 4
                    print('Start moving')
                else: # if already moving, but not yet arrived,
                    # For every {MOVEMENT_UPDATE_INTERVAL} second, get velocity vector and adjust movement
                    if (currentTime - lastLocationTime) > MOVEMENT_UPDATE_INTERVAL:
                        vec_center = center - lastLocation
                        vec_destination = destination - lastLocation

                        if np.all(vec_center == 0):
                            print('not moved')
                            continue

                        degree_offset = -np.cross(vec_destination, vec_center) / (np.dot(vec_center, vec_center)**.5 * np.dot(vec_destination, vec_destination)**.5)
                        print(degree_offset)
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
                        lastLocationTime = currentTime
            else:
                if isMoving:
                    isMoving = False
                    robot.write('x'.encode())
                    robotMovementState_FB = 0
                    robotMovementState_LR = 0
                    #destination = center
                    if len(rewardLocations) != 0:
                        destination = rewardLocations.pop()
                    else:
                        break


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

robot.write('sssssss'.encode())