import cv2 as cv
import numpy as np
from time import sleep, time

vc = cv.VideoCapture(0)

ret, img = vc.read()

frame_size = [img.shape[0], img.shape[1]]

# Select Global Mask
mask_position = cv.selectROI('Select ROI', img)
cv.destroyWindow('Select ROI')
global_mask = np.zeros(frame_size, dtype=np.uint8)
global_mask[mask_position[1]:mask_position[1] + mask_position[3],mask_position[0]:mask_position[0] + mask_position[2]] = 255

img = cv.bitwise_and(img, img, mask=global_mask)

loc = cv.selectROI('Select Object', img)
cv.destroyWindow('Select Object')

selectedImage = img[loc[1]:loc[1]+loc[3],loc[0]:loc[0] + loc[2], :]
cv.imshow('Selected', selectedImage)
cv.waitKey()
cv.destroyWindow('Selected')

# Get color (b,g,r)
objectColor = np.mean(np.reshape(selectedImage, (selectedImage.shape[0] * selectedImage.shape[1], -1), order='F'), 0)
RANGE = 50


def getKernel(size):
    size = int(size)
    return cv.getStructuringElement(cv.MORPH_ELLIPSE, (size, size),
                                    ((int((size - 1) / 2), int((size - 1) / 2))))

startTime = time()
while(time() - startTime < 60):
    ret, img = vc.read()

    img = cv.bitwise_and(img, img, mask=global_mask)

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
        cv.drawMarker(img, center, (255, 255, 0), markerType=cv.MARKER_STAR, thickness=2)
        cv.imshow('Selected', cv.drawContours(img, largestContours, 2, (100, 155, 255), 2))
        cv.waitKey(1)
        sleep(0.1)

cv.destroyWindow('Selected')




