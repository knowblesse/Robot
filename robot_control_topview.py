import cv2 as cv
import numpy as np
from time import sleep, time
import serial

# Setup Robot
robot = serial.Serial("COM3", 57600, timeout=0, rtscts=False)

if not robot.is_open:
    print('Serial Port is NOT Open')

#robot.write('xaaaaaaaaaa'.encode())


# Setup Tracking Color
vc = cv.VideoCapture(0)

ret, img = vc.read()

frame_size = [img.shape[0], img.shape[1]]

# Select Global Mask
mask_position = (30, 27, 589, 430)
# mask_position = cv.selectROI('Select ROI', img)
# cv.waitKey()
# cv.destroyWindow('Select ROI')
global_mask = np.zeros(frame_size, dtype=np.uint8)
global_mask[mask_position[1]:mask_position[1] + mask_position[3],mask_position[0]:mask_position[0] + mask_position[2]] = 255


# Select Operation Range
operation_range = np.array([149, 112, 382, 228])
# operation_range = np.array(cv.selectROI('Select Operation Range', img))
# cv.destroyWindow('Select Operation Range')

# Define proprocess filter
def getFrame():
    ret, img = vc.read()
    img = cv.bitwise_and(img, img, mask=global_mask)
    img = cv.rectangle(img, operation_range[0:2], operation_range[0:2] + operation_range[2:4], color=(0,0,255), thickness=2)
    return img

objectColor = np.array([ 25.0959596 ,  28.28787879, 171.15151515])
# img = getFrame()
# loc = cv.selectROI('Select Object', img)
# cv.destroyWindow('Select Object')
#
# selectedImage = img[loc[1]:loc[1]+loc[3],loc[0]:loc[0] + loc[2], :]
# cv.imshow('Selected', selectedImage)
# cv.waitKey()
# cv.destroyWindow('Selected')
#
# # Get color (b,g,r)
# objectColor = np.median(np.reshape(selectedImage, (selectedImage.shape[0] * selectedImage.shape[1], -1), order='F'), 0)
RANGE = 50

def getKernel(size):
    size = int(size)
    return cv.getStructuringElement(cv.MORPH_ELLIPSE, (size, size),
                                    ((int((size - 1) / 2), int((size - 1) / 2))))



startTime = time()

lastTurnTime = time()
lastLocationTime = time()
lastLocation = []

isFirstIteration = True
isMoving = False
global destination
DESTINATION_THRESHOLD = 30
MOVEMENT_UPDATE_INTERVAL = 5

def setDestination(event, x, y, flags, userData):
    if event == cv.EVENT_LBUTTONDBLCLK:
        global destination
        destination = [x, y]
        print(f'Destination set : ({x} , {y})')


cv.namedWindow('Main')
cv.setMouseCallback('Main', setDestination)

robotMovementState_FB = 0
robotMovementState_LR = 0
command2send = ''

while(time() - startTime < 60):
    img = getFrame()
    currentTime = time()

    # Mask Color
    binaryImage =cv.inRange(img, objectColor - RANGE, objectColor + RANGE)

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
                        targetMovementState_FB = np.round((0.5 - np.abs(degree_offset))*2) + 3  # if perfectly aligned, FB = + 10
                        targetMovementState_LR = np.round(degree_offset*3) # if plus, turn right

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
                    destination = center


            cv.putText(img, f"Foward Speed : {robotMovementState_FB}|{'Right' if robotMovementState_LR > 0 else 'Left'}{robotMovementState_LR}", (10, 30), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=0.8,
                       color=(255, 255, 255))
            cv.putText(img, command2send, (10, 60), fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=.8,
                       color=(255, 255, 255))
            cv.arrowedLine(img, lastLocation, center, color=(0, 0, 255), thickness=2)
            cv.arrowedLine(img, lastLocation, destination, color=(255, 255, 255), thickness=2)
            cv.drawMarker(img, center, (255, 255, 0), markerType=cv.MARKER_STAR, thickness=2)
        cv.imshow('Main', img)
        cv.waitKey(1)
        sleep(0.1)

        # if ( (center[0] < operation_range[0] or center[0] > operation_range[0] + operation_range[2]) or (center[1] < operation_range[1] or center[1] > operation_range[1] + operation_range[3])
        #         and time()-lastTurnTime > 2):
        #     # stop robot
        #     robot.write('x'.encode())
        #     robot.write('ddddddd'.encode())
        #     sleep(2)
        #     robot.write('xwwwwwww'.encode())
        #     lastTurnTime = time()

cv.destroyWindow('Main')
robot.write('x'.encode())

robot.write('sssssss'.encode())