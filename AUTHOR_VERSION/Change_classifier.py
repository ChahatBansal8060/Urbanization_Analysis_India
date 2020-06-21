import numpy as np
from scipy import ndimage
import numpy as np
from PIL import Image
import os, sys

    
'''
Driver code starts here
'''
districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
years = ['2016', '2017', '2018', '2019']
for district in districts:
    print(district)
    main_folder = 'Cost_results_from_Regression/'+district
    cost_array = np.loadtxt(main_folder+'/'+district+'_regression_cost_array.txt')
    
    #divide cost array by 1000 because we multiplied 1000 during storage of file
    cost_array = cost_array/1000  
    
    threshold = 1.95
    print('threshold for ',district,' is: ',threshold)
    
    district_image_base_year = np.array(Image.open('BU_NBU_maps/'+district+'/'+district+'_BU_NBU_'+years[0]+'.png'))
    # bring images to label 0 for background pixels, 1 for BU, and 2 for NBU
    district_image_base_year = district_image_base_year//65
    image_dimensions = district_image_base_year.shape

    background_vs_non_background_image = np.sign(district_image_base_year)
    boundary_identifying_kernel = np.array([[1,1,1],[1,1,1],[1,1,1]]) 
    boundary_vs_non_boundary_mask = ndimage.convolve(background_vs_non_background_image, boundary_identifying_kernel, mode='constant', cval=0.0)

    '''
    For creating the CBU/CNBU/Changing maps, 
    we assign label 0 to background pixels
    label 65 (1x65) to CBU pixels
    label 130 (2x65) to CNBU pixels, and
    label 195 (3x65) to Changing pixels
    '''
    current_pixel = 0
    CBU_pixel_count = 0
    CNBU_pixel_count = 0
    Changing_pixel_count = 0
    CBU_CNBU_Changing_map = district_image_base_year 

    for j in range(image_dimensions[0]):
        for k in range(image_dimensions[1]):
            if (boundary_vs_non_boundary_mask[j][k] == 9):
                if (cost_array[current_pixel] <= threshold):
                    if (district_image_base_year[j][k] == 1):
                        CBU_CNBU_Changing_map[j][k] = 65
                        CBU_pixel_count += 1
                    else:
                        CBU_CNBU_Changing_map[j][k] = 130
                        CNBU_pixel_count += 1
                
                else:
                    CBU_CNBU_Changing_map[j][k] = 195
                    Changing_pixel_count += 1
                current_pixel += 1
            else:
                CBU_CNBU_Changing_map[j][k] = 0

    # save the CBU_CNBU_Changing map
    os.makedirs("CBU_CNBU_Changing_Maps", exist_ok=True)
    CBU_CNBU_Changing_map = ( Image.fromarray(CBU_CNBU_Changing_map) ).convert("L")
    CBU_CNBU_Changing_map.save('CBU_CNBU_Changing_Maps/'+district+'_CBU_CNBU_Changing.png')

    total_pixels = CBU_pixel_count + CNBU_pixel_count + Changing_pixel_count
    print("Percentage of CBU pixels: ", (CBU_pixel_count*100)/total_pixels,'%')
    print("Percentage of CNBU pixels: ", (CNBU_pixel_count*100)/total_pixels,'%')
    print("Percentage of Changing pixels: ", (Changing_pixel_count*100)/total_pixels,'%')
    

