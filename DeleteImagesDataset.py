import os
import cv2
from scipy.io import savemat
import shutil

# Charuco parameters
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 9
SQUARE_LENGTH = 0.03
MARKER_LENGTH = 0.022

def detect_images_corners(path_to_images_calib, save_path):
    # Define the aruco dictionary and charuco board
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()

    # Load PNG & JPG images from folder
    image_files = [os.path.join(path_to_images_calib, f) for f in os.listdir(path_to_images_calib) if f.endswith((".png", ".jpg"))]
    image_files.sort()  # Ensure files are in order

    for image_file in image_files:
        image = cv2.imread(image_file)

        # Modify image to be readable by openCV
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # OpenCV detect markers
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(frame, dictionary)
        print(image_file)
        #print(len(marker_corners))
        # Skip processing if no markers are detected
        if marker_corners is not None:

            # If at least one marker is detected
            if len(marker_ids) > 0:
                # Improve position estimation using the Aruco markers
                charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(marker_corners,

                                                                                                   marker_ids, image, board)
                print('Corners#)')
                print(len(charuco_corners))
                #cv2.aruco.drawDetectedCornersCharuco(frame, charuco_corners, charuco_ids)
                #resized_img = cv2.resize(frame, (1400, 1000))
                #cv2.imshow('Charuco Detection', resized_img)
                #cv2.waitKey(0)
                if len(charuco_corners) > 47:
                    print(f"save {image_file}  enough detected corners")
                    os.makedirs(save_path, exist_ok=True)
                    destination = os.path.join(save_path, os.path.basename(image_file))
                    shutil.move(image_file, destination)


    print(f"Images moved to {save_path}")

