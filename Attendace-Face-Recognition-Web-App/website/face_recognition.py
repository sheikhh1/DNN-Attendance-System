from operator import itemgetter
from deepface import DeepFace
from website.utility_functions import get_images
import re


model = "ArcFace"
distance_metric = "cosine"

load_model = DeepFace.build_model(model)

# Load all query images

records_to_be_added = []

def preform_face_recognition(query_images, reference_images):
    
    database_records = []


    if len(query_images) == 0 or len(reference_images) == 0:
        return

    
    database_records = []

    for q_img in query_images:

        all_distances = []
        print("QUERY IMAGE: ", q_img)

        for r_img in reference_images:

            result = DeepFace.verify(img1_path=q_img, img2_path=r_img, model_name=model, distance_metric=distance_metric, enforce_detection=False, detector_backend='mtcnn')

            if result['distance'] <=0.73:
                verified = True
            else: 
                verified = False

            all_distances.append({'verified': verified, 'distance':result['distance'], 'r_img':r_img})
        
        # Sort list by distance & get smallest distance

        sorted_list = (sorted(all_distances, key=itemgetter('distance')))

        print("SORTED LIST: ", sorted_list)


        sorted_list = (sorted(all_distances, key=itemgetter('distance')))[0]

        student_roll_no = int((re.findall('[0-9]+', sorted_list['r_img']))[0])

        reference_images.remove(sorted_list['r_img'])

        database_records.append([sorted_list['r_img'], student_roll_no, sorted_list['verified']])

    
    if len(reference_images) > 0:

        for r_img2 in reference_images:
            student_roll_no = int((re.findall('[0-9]+', r_img2))[0])
            database_records.append([r_img2, student_roll_no, False])
    
    print("DATABASE RECORDS: ", database_records)
    return database_records




        
        


