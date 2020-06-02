import numpy as np
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import sys, os
from PIL import Image
from math import ceil, floor

'''
Getting the latitude and longitude bounding box of the district
'''
def Get_district_bounding_box( district_coordinates_filepath, district ):        
    bounding_box_dataframe = pd.read_csv(district_coordinates_filepath)
    district_index = np.where( bounding_box_dataframe["District_Name"].values == district )
    min_lat = float( (bounding_box_dataframe["MinLat"].values)[district_index] )
    max_lat = float( (bounding_box_dataframe["MaxLat"].values)[district_index] )
    min_lon = float( (bounding_box_dataframe["MinLong"].values)[district_index] )
    max_lon = float( (bounding_box_dataframe["MaxLong"].values)[district_index] )
    return min_lat, max_lat, min_lon, max_lon


'''
This function pads the image on all 4 sides to accommodate the difference in actual and rounded value
The padded pixels have the value of background pixels i.e 0
Inputs:
1) BU_NBU_map: The BU and NBU mapping of a district for a particular year
2) min_lat, max_lat, min_lon, max_lon: Original tight bounding box
3) rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon: Rounded off bounding box
'''
def Pad_image(BU_NBU_map, min_lat, max_lat, min_lon, max_lon, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon):
    # since (max_coordinate - min_coordinate) = #row/column pixels, thus using unitary method
    top_rows = ceil( BU_NBU_map.shape[0] * ( (rounded_max_lat - max_lat) / (max_lat - min_lat) ) )
    bottom_rows = ceil( BU_NBU_map.shape[0] * ( (min_lat - rounded_min_lat) / (max_lat - min_lat) ) )
    left_columns = ceil( BU_NBU_map.shape[1] * ( (min_lon - rounded_min_lon) / (max_lon - min_lon) ) )
    right_columns = ceil( BU_NBU_map.shape[1] * ( (rounded_max_lon - max_lon) / (max_lon - min_lon) ) )

    for row in range(top_rows):
        BU_NBU_map = np.insert(BU_NBU_map, 0, np.zeros( (BU_NBU_map.shape[1],), dtype=int), axis=0)
    for row in range(bottom_rows):
        BU_NBU_map = np.insert(BU_NBU_map, len(BU_NBU_map), np.zeros( (BU_NBU_map.shape[1],), dtype=int), axis=0)
    for column in range(left_columns):
        BU_NBU_map = np.c_[ np.zeros( (BU_NBU_map.shape[0],), dtype=int ), BU_NBU_map ]
    for column in range(right_columns):
        BU_NBU_map = np.c_[ BU_NBU_map, np.zeros( (BU_NBU_map.shape[0],), dtype=int ) ]

    return BU_NBU_map


'''
This function plots the district image with C1-C5 grid visualization
'''
def Plot_grid_classes(district, sample_image, min_lat, max_lat, min_lon, max_lon, indicators_dataframe, year):
    # designate RGB color to each grid class    
    background_color = [0,0,0]
    rejected_color = [255,255,255]
    c1_color = [255,215,0] # Yellow
    c2_color = [178,255,102] # Light_Green
    c3_color = [0,204,0] # Green
    c4_color = [0,102,0] # Dark_Green
    c5_color = [255,0,0] # Red
        
    final_image = np.zeros([sample_image.shape[0], sample_image.shape[1], 3], dtype=np.uint8) 
    
    # Create dictionary of grid number to class label mapping from dataframe
    grid_class_mapping = indicators_dataframe.set_index("Grid_number").to_dict()["Class_label"]

    # image dimensions in number of grids (of size 0.01 x 0.01 deg)
    img_height_grids = round( (max_lat - min_lat) * 100.0 ) 
    img_width_grids = round( (max_lon - min_lon) * 100.0 )

    # grid dimensions in number of pixels
    grid_height_pix = sample_image.shape[0] / img_height_grids
    grid_width_pix = sample_image.shape[1] / img_width_grids    

    # Allocating the grid number to each pixel
    for i in range(final_image.shape[0]):
        for j in range(final_image.shape[1]):
            if sample_image[i][j] == 0: # if this pixel is a background pixel
                final_image[i][j] = background_color
            else:
                grid_row = floor( i / grid_height_pix )
                grid_col = floor( j / grid_width_pix )
                grid_number = ( grid_col * img_height_grids ) + ( img_height_grids - grid_row -1 )
                class_label = grid_class_mapping[grid_number]
                if class_label == 0:
                    final_image[i][j] = rejected_color
                elif class_label == 1:
                    final_image[i][j] = c1_color
                elif class_label == 2:
                    final_image[i][j] = c2_color
                elif class_label == 3:
                    final_image[i][j] = c3_color
                elif class_label == 4:
                    final_image[i][j] = c4_color
                elif class_label == 5:
                    final_image[i][j] = c5_color
                
    final_image = Image.fromarray(final_image)
    
    target_directory = 'Visualization_Results/Class_wise_grid_maps/'+district
    os.makedirs(target_directory, exist_ok = True)
    final_image.save(target_directory+'/'+district+'_grid_classes_'+year+'.png')
    print('Done plotting grid-classes for ',district,' ',year)
 

'''
This function plots the district image with grid types- Urban, Periurban, and Rural
'''
def Plot_grid_types(district, sample_image, min_lat, max_lat, min_lon, max_lon, indicators_dataframe, year):
    # designate RGB color to each grid class    
    background_color = [0,0,0] #black
    rejected_color = [255,255,255] #white
    urban_color = [150, 40, 27] # Maroon
    periurban_color = [255, 140, 0] # Dark orange
        
    final_image = np.zeros([sample_image.shape[0], sample_image.shape[1], 3], dtype=np.uint8) 
    
    # Create dictionary of grid number to class label mapping from dataframe
    grid_type_mapping = indicators_dataframe.set_index("Grid_number").to_dict()["Grid_type"]

    # image dimensions in number of grids (of size 0.01 x 0.01 deg)
    img_height_grids = round( (max_lat - min_lat) * 100.0 ) 
    img_width_grids = round( (max_lon - min_lon) * 100.0 )

    # grid dimensions in number of pixels
    grid_height_pix = sample_image.shape[0] / img_height_grids
    grid_width_pix = sample_image.shape[1] / img_width_grids    

    # Allocating the grid number to each pixel
    for i in range(final_image.shape[0]):
        for j in range(final_image.shape[1]):
            if sample_image[i][j] == 0: # if this pixel is a background pixel
                final_image[i][j] = background_color
            else:
                grid_row = floor( i / grid_height_pix )
                grid_col = floor( j / grid_width_pix )
                grid_number = ( grid_col * img_height_grids ) + ( img_height_grids - grid_row -1 )
                class_label = grid_type_mapping[grid_number]
                if class_label == 'Urban':
                    final_image[i][j] = urban_color
                elif class_label == 'PeriUrban':
                    final_image[i][j] = periurban_color
                else:
                    final_image[i][j] = rejected_color
                
    final_image = Image.fromarray(final_image)
    
    target_directory = 'Visualization_Results/Grid_type_maps/'+district
    os.makedirs(target_directory, exist_ok = True)
    final_image.save(target_directory+'/'+district+'_grid_types_'+year+'.png')
    print('Done plotting grid-types for ',district,' ',year)


'''
Driver code begins here for the year 2019
'''
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
years = ['2016', '2019']

for district in districts:
    print(district)
    min_lat, max_lat, min_lon, max_lon = Get_district_bounding_box( 'district_coordinates.csv', district )

    # Since the grid size (0.01) is of precision 2, round off the image bounding box to fit all the grids
    rounded_min_lat = floor(100.0 * min_lat) / 100.0
    rounded_max_lat = ceil(100.0 * max_lat) / 100.0
    rounded_min_lon = floor(100.0 * min_lon) / 100.0
    rounded_max_lon = ceil(100.0 * max_lon) / 100.0 

    # take a sample image of district to find background and non-background pixels. Pad image to fit the grid size
    sample_image = np.array( Image.open('BU_NBU_maps/'+district+'/'+district+'_BU_NBU_2016.png') )
    padded_image = Pad_image(sample_image, min_lat, max_lat, min_lon, max_lon, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon)

    for year in years:
        indicators_filename =  'Grid_wise_all_indicators/'+district+'/'+district+'_'+year+'_all_indicators.csv'
        indicators_dataframe = pd.read_csv(indicators_filename)
        # plot the graph of C1-C5 classes
        Plot_grid_classes(district, padded_image, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon, indicators_dataframe, year)
        # plot the graph of grid types- urban. periurban, and rural
        Plot_grid_types(district, padded_image, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon, indicators_dataframe, year)
    
