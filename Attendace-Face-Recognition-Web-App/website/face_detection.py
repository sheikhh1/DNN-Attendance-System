from mtcnn.mtcnn import MTCNN
from matplotlib import pyplot
from website.utility_functions import clean_directory
import cv2
import random

detector = MTCNN()

def convert_box_coordinates(box):
    box[2] = box[2] + box[0]
    box[3] = box[3] + box[1]

    return box

def get_face_box(image_path):
    img = cv2.imread(image_path)

    pixels_image = pyplot.imread(image_path)

    faces_detected = detector.detect_faces(pixels_image)
    if len(faces_detected) > 1:
        return "Error"
    else:

        for face in faces_detected:
            if face['confidence'] > 0.98:
                bbox = convert_box_coordinates(face['box'])

                cropped_face = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    
        return cropped_face

def detect_faces(image_path):
    img = cv2.imread(image_path)

    pixels_image = pyplot.imread(image_path)

    faces_detected = detector.detect_faces(pixels_image)

    print(len(faces_detected))

    for face in faces_detected:
        if face['confidence'] > 0.98:
            bbox = convert_box_coordinates(face['box'])

            cropped_face = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]

            image_file_name = str(random.randint(0,1000)) + '.jpg'

            cv2.imwrite('./website/static/query_faces/' + image_file_name, cropped_face)
    return True
        


        
