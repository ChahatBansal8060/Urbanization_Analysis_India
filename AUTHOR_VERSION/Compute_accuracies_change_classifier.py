# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

import os, sys
from PIL import Image
import numpy as np
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 


'''
This function computes the overall accuracy across all districts
'''
def Get_overall_accuracy(districts, tiffiles_folder, pixelType_dict):
    actual_output = []
    predicted_output = []
    
    for district in districts:    
        for pixel_type in pixelType_dict.keys():
            tif_files_path = tiffiles_folder+'/'+district+'/'+district+'_'+pixel_type
            
            for tif_file in os.listdir(tif_files_path):
                tif_image = np.array( Image.open(tif_files_path+'/'+tif_file) )
                tif_output = tif_image.flatten().tolist()
                tif_output = list(filter(lambda a: a != 0, tif_output)) #remove all background pixels
                
                actual_output += [ pixelType_dict[pixel_type] ] * len(tif_output)
                predicted_output += tif_output
                
    print('\n*************Overall Classification Report******************')
    print('Label distribution of ground-truth: ', np.unique(np.array(actual_output), return_counts=True) )
    print(classification_report(actual_output, predicted_output, target_names=['CBU', 'CNBU', 'Changing'])) 


'''
This function computes the overall accuracy across all districts
'''
def Get_district_wise_accuracy(districts, tiffiles_folder, pixelType_dict):
    
    for district in districts:    
        actual_output = []
        predicted_output = []
        for pixel_type in pixelType_dict.keys():
            tif_files_path = tiffiles_folder+'/'+district+'/'+district+'_'+pixel_type
            
            for tif_file in os.listdir(tif_files_path):
                tif_image = np.array( Image.open(tif_files_path+'/'+tif_file) )
                tif_image = np.array( Image.open(tif_files_path+'/'+tif_file) )
                tif_output = tif_image.flatten().tolist()
                tif_output = list(filter(lambda a: a != 0, tif_output)) #remove all background pixels
                
                actual_output += [ pixelType_dict[pixel_type] ] * len(tif_output)
                predicted_output += tif_output

        print('\n**************',district,' Classification Report******************')
        print(classification_report(actual_output, predicted_output, target_names=['CBU', 'CNBU', 'Changing']))
        print('\n')


'''
Driver code begins here
'''
print("\n************ Checking the Accuracy of CBU/CNBU/Changing Maps **************\n")
# list of districts for which the accuracy is to be calculated as its groundtruth is available
districts = ['Bangalore', 'Chennai', 'Delhi', 'Mumbai']

# Name of the main folder where the cropped tif files of predictions are stored
tiffiles_folder = 'Balanced_Trimmed_tiffiles'

# this dictionary stores the integer code of each pixel type
pixelType_dict = {}
pixelType_dict['CBU'] = 65
pixelType_dict['CNBU'] = 130
pixelType_dict['Changing'] = 195

Get_overall_accuracy(districts, tiffiles_folder, pixelType_dict)
Get_district_wise_accuracy(districts, tiffiles_folder, pixelType_dict)



