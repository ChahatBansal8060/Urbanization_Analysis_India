# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

import sys,os
from os import listdir
from os.path import isfile, join
import numpy as np
from PIL import Image
import statistics 
import math
import shutil


'''
Method to calculate total images, total no of pixels, mean and median of image size for each category
Inputs:
1) input_folder = This is the complete directory path where the trimmed tiffiles of a particular category is stored
'''
def image_statistics(input_folder):
    x = []
    y = []
    total_pixels = 0
    total_images = 0
    for tif in os.listdir(input_folder):
        total_images += 1
        tif_image_path = input_folder + '/' + tif
        tif_image = np.asarray(Image.open(tif_image_path))
        image_size_x = tif_image.shape[0]
        image_size_y = tif_image.shape[1]
        x.append(image_size_x)
        y.append(image_size_y)
        for i in range(image_size_x):
            for j in range(image_size_y):
                if tif_image[i][j] != 0:
                    total_pixels += 1
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)
    x_median = statistics.median(x)
    y_median = statistics.median(y)	
    return total_pixels, total_images, x_mean, y_mean, x_median, y_median


'''
Method to print the details of groundtruth 
'''
def print_groundtruth_statistics(image_statistics_dict):
    print('Category -> ','total_pixels | ', 'total_images | ', 'x_mean | ', 'y_mean | ', 'x_median | ', 'y_median | ')
    for key,value in image_statistics_dict.items():
        print(key, '->', value)


'''
method to calculate cropping dimensions
'''
def crop_dimensions(image_statistics_dict):
    temp = min(image_statistics_dict.values()) #min value of each parameter in CBU, CNBU, Changing 
    
    min_cat = [key for key in image_statistics_dict if image_statistics_dict[key] == temp] 	
    min_cat = min_cat[0] #name of the category having minimum values
    min_cat_pixels = image_statistics_dict[min_cat][0] #minimum number of pixels in a category
    min_cat_x_mean = int(image_statistics_dict[min_cat][2]) #minimum average of rows 
    min_cat_y_mean = int(image_statistics_dict[min_cat][3]) #minimum average of columns

    crop_size = {}
    for key,value in image_statistics_dict.items():
        if key != min_cat:
            xy = int(math.sqrt((min_cat_pixels)/(image_statistics_dict[key][1]))) + 3
            crop_size[key] = xy
    return crop_size, min_cat


'''
This function crops the tiffile from its center at the desired dimension
Inputs:
1) original_tiffile = The tiffile to be cropped
2) crop_width = The dimension to crop along the width
3) 2) crop_height = The dimension to crop along the height
'''
def crop_center(original_tiffile, crop_width, crop_height):
    img_width, img_height = original_tiffile.size
    return original_tiffile.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


'''
Method to crop the images of desired dimensions
inputs:
1) input_folder = Input directory path where the original tiffiles images are stored
2) output_folder = Output directory path where the cropped tiffiles will be stored
3) crop_size = The dimension against which the tiffiles should be cropped
'''
def crop_images(input_folder, output_folder, crop_size):
    if not os.path.exists(output_folder): 
        os.makedirs(output_folder)

    tiffiles = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]

    for tiffile in tiffiles:
        tiffile_path = input_folder + '/' + tiffile
        img = Image.open(tiffile_path)
        cropped_img = crop_center(img, crop_size, crop_size)

        output_tiffile_path = output_folder + '/' + tiffile
        cropped_img.save(output_tiffile_path, quality=100)


'''
Driver code begins here
'''
def main():
    #districts for which groundtruth is present
    districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Mumbai']
    categories = ['CBU', 'CNBU', 'Changing']

    input_groundtruth_directory = 'Trimmed_tiffiles'
    output_groundtruth_directory = 'Balanced_Trimmed_tiffiles'

    # Delete old results if any 
    if os.path.exists('Balanced_Trimmed_tiffiles') and os.path.isdir('Balanced_Trimmed_tiffiles'):
        shutil.rmtree('Balanced_Trimmed_tiffiles')

    for district in districts:
        print("\nAnalyzing ",district,'\n')
        per_category_image_stats = {} #dictionary to store the statistics corresponding to each category of labels
        for category in categories:
            cropped_tiffiles_directory = input_groundtruth_directory+'/'+district+'/'+district+'_'+category
            per_category_image_stats[category] = image_statistics(cropped_tiffiles_directory)
        
        print('''---------Original Groundtruth Statistics-----------''')    
        print_groundtruth_statistics(per_category_image_stats)

        crop_size, min_category = crop_dimensions(per_category_image_stats)
        # print("Crop size is: ", crop_size)
        # print("Minimum category is: ", min_category)

        #copy the minimum category as it is in the balanced folder
        input_tiffiles_directory = input_groundtruth_directory+'/'+district+'/'+district+'_'+min_category
        output_balanced_tiffiles_directory = output_groundtruth_directory+'/'+district+'/'+district+'_'+min_category
        
        if os.path.exists(output_balanced_tiffiles_directory):
            shutil.rmtree(output_balanced_tiffiles_directory)    
        shutil.copytree(input_tiffiles_directory, output_balanced_tiffiles_directory)
        
        #for the remaining categories, crop the tiffiles further to balance the dataset
        for key, value in crop_size.items():
            input_tiffiles_directory = input_groundtruth_directory+'/'+district+'/'+district+'_'+key
            output_balanced_tiffiles_directory = output_groundtruth_directory+'/'+district+'/'+district+'_'+key
            crop_images(input_tiffiles_directory, output_balanced_tiffiles_directory, value)
    

    print("\n#### Check ",output_groundtruth_directory," directory for Results ####\n")


if __name__ == '__main__':
        main()	

        
