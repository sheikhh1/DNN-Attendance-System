import glob, os
import random

def get_images(directory):

        image_list = []

        for filename in glob.glob(directory + '*.jpg'): #assuming gif
            image_list.append(filename)
        
        for filename in glob.glob(directory + '*.jpeg'): #assuming gif
            image_list.append(filename)

        for filename in glob.glob(directory + '*.png'): #assuming gif
            image_list.append(filename)
        return image_list


def clean_directory(directory):
     # Clean up shot directory 
    files = glob.glob(directory)
    for f in files: 
        os.remove(f)

def shot_folder_manager():
        # Directory for saved shots 
        try:
            os.mkdir('./shots')
        except OSError as error:
            pass

        # Clean up shot directory 
        clean_directory('./shots/*')

def generate_student_ID():
    return random.randint(0,9999)

def delete_file_from_directory(image_file_path):
    os.remove(image_file_path)


    
