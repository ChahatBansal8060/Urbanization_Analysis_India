from PIL import Image
import numpy as np
import os, sys

districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
main_input_folder = 'CBU_CNBU_Changing_Maps'

destination_directory = main_input_folder+'/Colored_CBU-CNBU_Changing_Maps'

for district in districts:
    input_file_path = main_input_folder+'/'+district+'_CBU_CNBU_Changing.png'
    image_1d = np.array( Image.open(input_file_path) )

    image_3d = np.zeros( [image_1d.shape[0],image_1d.shape[1],3], dtype=np.uint8 )
 
    for i in range(image_1d.shape[0]):
        for j in range(image_1d.shape[1]):
            if image_1d[i][j] == 195:
                image_3d[i][j] = [255,0,0]
            else:
                if image_1d[i][j] == 0: #background
                    image_3d[i][j] = [0,0,0]
                elif image_1d[i][j] == 65: #BU
                    image_3d[i][j] = [160,160,160]
                elif image_1d[i][j] == 130: #NBU
                    image_3d[i][j] = [0,255,0]                  

    image_3d = Image.fromarray(image_3d)
    
    os.makedirs( destination_directory, exist_ok = True )
    image_3d.save(destination_directory+'/'+district+'_Colored_CBU_CNBU_Changing.png')

print("Your CBU/CNBU/Changing maps are successfully color-coded!! Background (black), CBU (gray), CNBU (green), and Changing (red)\n")
