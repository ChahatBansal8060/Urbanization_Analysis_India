from PIL import Image
import numpy as np
import os, sys

districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
main_input_folder = 'BU_NBU_maps'

destination_directory = 'CBU_CNBU_Changing_Maps'

for district in districts:
    input_file_path = main_input_folder+'/'+district
    image_2016_path = input_file_path+'/'+district+'_BU_NBU_2016.png'
    image_2019_path = input_file_path+'/'+district+'_BU_NBU_2019.png'

    image_2016 = np.array( Image.open(image_2016_path) )
    image_2019 = np.array( Image.open(image_2019_path) )

    image_changing = np.array( Image.open(image_2016_path) ) #initializing with base image

    for i in range(image_2016.shape[0]):
        for j in range(image_2016.shape[1]):
            if image_2016[i][j] == 130 and image_2019[i][j] == 65:
                image_changing[i][j] = 195
            else:
                image_changing[i][j] = image_2016[i][j]                  

    image_changing = Image.fromarray(image_changing)
    
    os.makedirs( destination_directory, exist_ok = True )
    image_changing.save(destination_directory+'/'+district+'_CBU_CNBU_Changing.png')

print("Conversion Successful !!")
