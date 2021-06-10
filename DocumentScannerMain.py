import cv2
import numpy as np
import utlis





########################################################################
webCamFeed = True
pathImage = "IMG.jpg"
# cap = cv2.VideoCapture(1)
# cap.set(10,160)
heightImg = 800
widthImg  = 1000
########################################################################

utlis.initializeTrackbars()
count=0
#v
vid = cv2.VideoCapture(0)

pts1 = np.float32([[0, 260], [640, 260], [0, 400], [640, 400]])
pts2 = np.float32([[0, 0], [400, 0], [0, 640], [400, 640]])

while True:
    #v
    ret, img = vid.read()
    cv2.imshow('frame', img)


    imgBlank = np.zeros((heightImg, widthImg, 3),np.uint8)

    # if webCamFeed:
    #     success, img = cap.read()
    # else:
    # img = cv2.imread(pathImage)

    img = cv2.resize(img, (widthImg, heightImg), interpolation=cv2.INTER_AREA) # RESIZE IMAGE
    imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8) # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
    thres=utlis.valTrackbars() # GET TRACK BAR VALUES FOR THRESHOLDS
    imgThreshold = cv2.Canny(imgBlur,thres[0],thres[1]) # APPLY CANNY BLUR
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=2) # APPLY DILATION
    imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION

    ## FIND ALL COUNTOURS
    imgContours = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # FIND ALL CONTOURS
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10) # DRAW ALL DETECTED CONTOURS

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    testimage = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

    imgGray = cv2.cvtColor(testimage, cv2.COLOR_BGR2GRAY)
    imgfin = cv2.adaptiveThreshold(imgGray, 255, 1, 1, 7, 3)
    imgfin = cv2.bitwise_not(imgfin)
    imgfin = cv2.medianBlur(imgfin, 3)

    imgfin = cv2.rotate(imgfin, cv2.ROTATE_180)

    cv2.imshow("imagetest", imgfin)

    # FIND THE BIGGEST COUNTOUR
    biggest, maxArea = utlis.biggestContour(contours) # FIND THE BIGGEST CONTOUR
    if biggest.size != 0:
        biggest=utlis.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
        imgBigContour = utlis.drawRectangle(imgBigContour,biggest,2)
        pts1 = np.float32(biggest) # PREPARE POINTS FOR WARP

        pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))


        #REMOVE 20 PIXELS FORM EACH SIDE
        imgWarpColored=imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
        imgWarpColored = cv2.resize(imgWarpColored,(widthImg,heightImg))

        # APPLY ADAPTIVE THRESHOLD
        imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre= cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre=cv2.medianBlur(imgAdaptiveThre,3)

        # Image Array for Display

        imageArray = ([img,imgGray,imgThreshold,imgContours],
                      [imgBigContour,imgWarpColored, imgWarpGray,imgAdaptiveThre])

    else:
        imageArray = ([img,imgGray,imgThreshold,imgContours],
                      [imgBlank, imgBlank, imgBlank, imgBlank])

    # LABELS FOR DISPLAY
    lables = [["Original","Gray","Threshold","Contours"],
              ["Biggest Contour","Warp Prespective","Warp Gray","Adaptive Threshold"]]

    stackedImage = utlis.stackImages(imageArray,0.75,lables)
    # cv2.imshow("Result",stackedImage)
    cv2.imshow("search ", imgContours)

    # SAVE IMAGE WHEN 's' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("Scanned/myImage"+str(count)+".jpg",imgWarpColored)
        cv2.rectangle(stackedImage, ((int(stackedImage.shape[1] / 2) - 230), int(stackedImage.shape[0] / 2) + 50),
                      (1100, 350), (0, 255, 0), cv2.FILLED)
        cv2.putText(stackedImage, "Scan Saved", (int(stackedImage.shape[1] / 2) - 200, int(stackedImage.shape[0] / 2)),
                    cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
        cv2.imshow('Result', stackedImage)
        cv2.waitKey(300)
        count += 1
