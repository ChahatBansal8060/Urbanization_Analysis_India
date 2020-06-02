from PIL import Image
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt, floor, ceil
import os, sys


'''
This function converts the CBU/CNBU/Changing map of a district into BU_NBU maps of 
a first year and the last year under change analysis.
In the CBU_CNBU_Changing maps, Background is stored as 0, CBU as 65, CNBU as 130, and Changing as 195
Output:
The BU_NBU maps corresponding to the first and last year. Background(0), BU(1), NBU(2)
'''
def Get_BU_NBU_maps(CBU_CNBU_Changing_map):
    BU_NBU_first_year = np.copy(CBU_CNBU_Changing_map) 
    BU_NBU_first_year[ CBU_CNBU_Changing_map == 65 ] = 1 # CBU is BU in both years
    BU_NBU_first_year[ CBU_CNBU_Changing_map == 130 ] = 2 # CNBU is NBU in both years
    BU_NBU_first_year[ CBU_CNBU_Changing_map == 195 ] = 2 # Changing is NBU in first year
    
    BU_NBU_last_year = np.copy(CBU_CNBU_Changing_map)
    BU_NBU_last_year[ CBU_CNBU_Changing_map == 65 ] = 1 # CBU is BU in both years
    BU_NBU_last_year[ CBU_CNBU_Changing_map == 130 ] = 2 # CNBU is NBU in both years
    BU_NBU_last_year[ CBU_CNBU_Changing_map == 195 ] = 1 # Changing is BU in last year
    
    return BU_NBU_first_year, BU_NBU_last_year


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
    top_rows = floor( BU_NBU_map.shape[0] * ( (rounded_max_lat - max_lat) / (max_lat - min_lat) ) )
    bottom_rows = floor( BU_NBU_map.shape[0] * ( (min_lat - rounded_min_lat) / (max_lat - min_lat) ) )
    left_columns = floor( BU_NBU_map.shape[1] * ( (min_lon - rounded_min_lon) / (max_lon - min_lon) ) )
    right_columns = floor( BU_NBU_map.shape[1] * ( (rounded_max_lon - max_lon) / (max_lon - min_lon) ) )

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
This function is used to find the distance between two coordinates on earth using Haversine formula
'''
def Get_distance(source_lat, source_lon, dest_lat, dest_lon):
    # convert all coordinates from degrees to radians
    source_lat = radians(source_lat)
    source_lon = radians(source_lon)
    dest_lat = radians(dest_lat)
    dest_lon = radians(dest_lon)
    
    # Applying Haversine formula
    difference_lat = dest_lat - source_lat
    difference_lon = dest_lon - source_lon
    a = sin(difference_lat/2)**2 + cos(source_lat) * cos(dest_lat) * sin(difference_lon / 2)**2
    c = 2 * asin(sqrt(a))
    earth_radius = 6378100.0 # Radius of earth in meters. Use 3956 for miles
    
    return c * earth_radius


'''
This function re-labels each pixel as rural, peri-urban or urban based on spatial correctness.
This is based on the percentage of BU pixels within the walking distance circle of a pixel.
Inputs:
1) BU_NBU_map: This is the BU/NBU map with Background (0), BU (1), NBU (2)
2) min_lat, max_lat, min_lon, max_lon: Bounding box coordinates of the district
Output:
1) Urban_Periurban_Rural_map: This is the re-labeled pixel map with Background (0), Urban (1), Peri-urban (2), Rural (3) 
'''
def Compute_single_year_urban_extent(BU_NBU_map, min_lat, max_lat, min_lon, max_lon):
    WDC_radius = 564 # this is radius of walking_distance_circle (WDC) in meters
    image_rows = BU_NBU_map.shape[0] #These are same for both first and last year
    image_cols = BU_NBU_map.shape[1] #These are same for both first and last year

    # Since the distribution of pixels about x-axis and y-axis is not same, 
    # walking_distance_circle will actually be an ellipse in both directions

    # Computing the number of pixels along the radius of major(a) and minor(b) axis of ellipse
    ellipse_a = floor( (WDC_radius * image_rows) / Get_distance(min_lat, min_lon, max_lat, min_lon) )
    ellipse_b = floor( (WDC_radius * image_cols) / Get_distance(min_lat, min_lon, min_lat, max_lon) )
    
    Urban_Periurban_Rural_map = np.copy(BU_NBU_map)
    urban_threshold = 0.50 # pixels with more than 50% BU pixels in WDC are urban
    periurban_threshold = 0.25 # pixels with >=25% and <50% BU pixels in WDC are peri-urban
    
    for row_id in range(image_rows):
        for col_id in range(image_cols):
            if BU_NBU_map[row_id][col_id] == 0:
                continue # do no changes to background pixels            
            BU_pixels_WDC = 0
            total_pixels_WDC = 0
            for u in range( row_id-ellipse_a, row_id+ellipse_a +1, 1):
                for v in range( col_id-ellipse_b, col_id+ellipse_b +1, 1):
                    if u < 0 or u >= image_rows or v < 0 or v >= image_cols: # if pixel outside bounding box
                        continue
                    # if the pixel is within the boundary of ellipse ((x-i)^2 b^2)+((y-j)^2 a^2)-(a^2 b^2) <= 0
                    if ((u-row_id)**2 * ellipse_b**2) + ((v-col_id)**2 * ellipse_a**2) - (ellipse_a**2 * ellipse_b**2) <= 0:
                        if BU_NBU_map[u][v] == 1:
                            BU_pixels_WDC += 1    
                    total_pixels_WDC += 1
                    
            # the calculation of total BU pixels and total pixels in WDC is complete
            BU_percentage = BU_pixels_WDC / total_pixels_WDC
            
            if BU_percentage >= urban_threshold:
                Urban_Periurban_Rural_map[row_id][col_id] = 1 #pixel is urban
            elif BU_percentage >= periurban_threshold:
                Urban_Periurban_Rural_map[row_id][col_id] = 2 #pixel is peri-urban
            else:
                Urban_Periurban_Rural_map[row_id][col_id] = 3 #pixel is rural
                
    return Urban_Periurban_Rural_map

'''
This function re-labels each pixel as rural, peri-urban or urban based on spatial correctness.
This is based on the percentage of BU pixels within the walking distance circle of a pixel.
Inputs:
1) BU_NBU_map1: This is the BU/NBU map of first year with Background (0), BU (1), NBU (2)
2) BU_NBU_map2: This is the BU/NBU map of last year with Background (0), BU (1), NBU (2)
3) min_lat, max_lat, min_lon, max_lon: Bounding box coordinates of the district
Output:
1) Urban_Periurban_Rural_map1, Urban_Periurban_Rural_map2: This is the re-labeled pixel map with Background (0), Urban (1), Peri-urban (2), Rural (3) 
'''
def Compute_urban_extent(BU_NBU_map1, BU_NBU_map2, min_lat, max_lat, min_lon, max_lon):
    WDC_radius = 564 # this is radius of walking_distance_circle (WDC) in meters
    image_rows = BU_NBU_map1.shape[0] #These are same for both first and last year
    image_cols = BU_NBU_map1.shape[1] #These are same for both first and last year

    # Since the distribution of pixels about x-axis and y-axis is not same, 
    # walking_distance_circle will actually be an ellipse in both directions

    # Computing the number of pixels along the radius of major(a) and minor(b) axis of ellipse
    ellipse_a = floor( (WDC_radius * image_rows) / Get_distance(min_lat, min_lon, max_lat, min_lon) )
    ellipse_b = floor( (WDC_radius * image_cols) / Get_distance(min_lat, min_lon, min_lat, max_lon) )
    
    Urban_Periurban_Rural_map1 = np.copy(BU_NBU_map1)
    Urban_Periurban_Rural_map2 = np.copy(BU_NBU_map2)
    urban_threshold = 0.50 # pixels with more than 50% BU pixels in WDC are urban
    periurban_threshold = 0.25 # pixels with >=25% and <50% BU pixels in WDC are peri-urban
    
    for row_id in range(image_rows):
        for col_id in range(image_cols):
            if BU_NBU_map1[row_id][col_id] == 0 and BU_NBU_map2[row_id][col_id] == 0:
                continue # do no changes to background pixels            
            
            BU_pixels_WDC1 = 0
            total_pixels_WDC1 = 0
            BU_pixels_WDC2 = 0
            total_pixels_WDC2 = 0
            
            for u in range( row_id-ellipse_a, row_id+ellipse_a +1, 1):
                for v in range( col_id-ellipse_b, col_id+ellipse_b +1, 1):
                    if u < 0 or u >= image_rows or v < 0 or v >= image_cols: # if pixel outside bounding box
                        continue
                    # if the pixel is within the boundary of ellipse ((x-i)^2 b^2)+((y-j)^2 a^2)-(a^2 b^2) <= 0
                    if ((u-row_id)**2 * ellipse_b**2) + ((v-col_id)**2 * ellipse_a**2) - (ellipse_a**2 * ellipse_b**2) <= 0:
                        if BU_NBU_map1[u][v] == 1:
                            BU_pixels_WDC1 += 1
                        if BU_NBU_map2[u][v] == 1:
                            BU_pixels_WDC2 += 1
                    
                    total_pixels_WDC1 += 1
                    total_pixels_WDC2 += 1
                    
            # calculate the percentage of BU pixels in the WDC of this pixel
            BU_percentage1 = BU_pixels_WDC1 / total_pixels_WDC1
            BU_percentage2 = BU_pixels_WDC2 / total_pixels_WDC2
            
            if BU_percentage1 >= urban_threshold:
                Urban_Periurban_Rural_map1[row_id][col_id] = 1 #pixel is urban
            elif BU_percentage1 >= periurban_threshold:
                Urban_Periurban_Rural_map1[row_id][col_id] = 2 #pixel is peri-urban
            else:
                Urban_Periurban_Rural_map1[row_id][col_id] = 3 #pixel is rural
                
            if BU_percentage2 >= urban_threshold:
                Urban_Periurban_Rural_map2[row_id][col_id] = 1 #pixel is urban
            elif BU_percentage2 >= periurban_threshold:
                Urban_Periurban_Rural_map2[row_id][col_id] = 2 #pixel is peri-urban
            else:
                Urban_Periurban_Rural_map2[row_id][col_id] = 3 #pixel is rural
                
    return Urban_Periurban_Rural_map1, Urban_Periurban_Rural_map2



'''
This function returns grid-level urban parameterss 
Inputs:
1) U_PU_R_map: Urban/periurban/Rural mapping of a particular district. Urban(1), Periurban(2), Rural(3)
2) min_lat, max_lat, min_lon, max_lon: bounding box coordinates of the district
'''
def Get_grid_urban_indicators(U_PU_R_map, min_lat, max_lat, min_lon, max_lon):
    # create grids of the district of size 0.01 deg. These grids divide image into rows and columns
    # value of grid_columns and grid_rows is opposite because the image matrix has been rotated
    grid_cols = round( (max_lat - min_lat) * 100.0 )
    grid_rows = round( (max_lon - min_lon) * 100.0 )
    
    rows = U_PU_R_map.shape[0]
    cols = U_PU_R_map.shape[1]
    
    result_grid_numbers = []
    result_grid_types = []
    result_urban_percentages = []
    result_periurban_percentages = []
    result_rural_percentages = []
    
    grid_selection_threshold = 0.50 # grids with more that 50% urban/periurban grids are selected for further analysis
    for grid_i in np.arange(0, grid_rows, 1.0):
        for grid_j in np.arange(0, grid_cols, 1.0):
            grid_number = round( (grid_i * grid_cols) + grid_j )
            total_pixels = 0
            background_pixels = 0
            urban_pixels = 0
            periurban_pixels = 0
            rural_pixels = 0
            
            for pixel_i in range( floor((rows*grid_i)/grid_rows), floor( (rows*(grid_i+1.0))/grid_rows), 1 ):
                for pixel_j in range( floor((cols*grid_j)/grid_cols), floor((cols*(grid_j+1.0))/grid_cols), 1 ):
                    # for every pixel (pixel_i, pixel_j) within the grid
                    if (pixel_i >= 0 and pixel_i < rows and pixel_j >= 0 and pixel_j < cols):
                        total_pixels += 1
                        if U_PU_R_map[pixel_i][pixel_j] == 0: # background pixel
                            background_pixels += 1
                        elif U_PU_R_map[pixel_i][pixel_j] == 1: # urban pixel
                            urban_pixels += 1
                        elif U_PU_R_map[pixel_i][pixel_j] == 2: # periurban pixel
                            periurban_pixels += 1
                        elif U_PU_R_map[pixel_i][pixel_j] == 3: # rural pixel
                            rural_pixels += 1
            
            percentage_background = round(background_pixels/total_pixels, 6)
            percentage_urban = round(urban_pixels/total_pixels, 6)
            percentage_periurban = round(periurban_pixels/total_pixels, 6)
            percentage_rural = round(rural_pixels/total_pixels, 6)
            
            result_grid_numbers.append( grid_number )
            result_urban_percentages.append( percentage_urban )
            result_periurban_percentages.append( percentage_periurban )
            result_rural_percentages.append( percentage_rural )                         
            
            # Finding the type of grid -> Urban, Periurban, Rural, or Rejected 
            U_PU_percentage = percentage_urban + percentage_periurban
            
            if round(U_PU_percentage,2) >= grid_selection_threshold: # selected urbanized grid
                if (urban_pixels > periurban_pixels):
                    result_grid_types.append('Urban')
                else:
                    result_grid_types.append('PeriUrban')
            elif round(percentage_background,2) < 0.50: # for non-urbanized grids with less than 50% background pixels
                result_grid_types.append('Rural')
            else:
                result_grid_types.append('Rejected')                     
                    
    Zipped_results =  list(zip(result_grid_numbers, result_grid_types, result_urban_percentages, result_periurban_percentages, result_rural_percentages))
    Results_dataframe = pd.DataFrame(Zipped_results, columns = ['Grid_number', 'Grid_type', 'Urban_percentage', 'Periurban_percentage', 'Rural_percentage'])
    return Results_dataframe


'''
This function plots the visual image of district with Urban/Periurban/Rural mapping
'''
def Plot_U_PU_R_map(district, U_PU_R_mapping, year, target_filepath):
    # RGBA code for each of the label
    background_color = [0, 0, 0] # black color
    urban_color = [150, 40, 27] # maroon color
    periurban_color = [255, 140, 0] # darkorange color
    rural_color = [255, 255, 255] # white color

    U_PU_R_image = np.zeros([U_PU_R_mapping.shape[0], U_PU_R_mapping.shape[1], 3], dtype=np.uint8)
    
    for y in range(U_PU_R_image.shape[1]):
        for x in range(U_PU_R_image.shape[0]):
            if U_PU_R_mapping[x][y] == 0:      # background 
                U_PU_R_image[x][y] = background_color            
            elif U_PU_R_mapping[x][y] == 1:    # urban pixel
                U_PU_R_image[x][y] = urban_color      
            elif U_PU_R_mapping[x][y] == 2:    # peri-urban pixel
                U_PU_R_image[x][y] = periurban_color      
            elif U_PU_R_mapping[x][y] == 3:    # rural pixel 
                U_PU_R_image[x][y] = rural_color  
            
    U_PU_R_image = Image.fromarray(U_PU_R_image)
    U_PU_R_image.save(target_filepath+'/'+district+'_U_PU_R_colored_prediction_'+year+'.png')
    print("Done plotting ",district)


'''
Driver code begins here
'''
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
#districts = ['Chennai']

for district in districts:
    print(district)

    CBU_CNBU_Chaning_map_filepath = 'CBU_CNBU_Changing_Maps/'+district+'_CBU_CNBU_Changing.png'
    CBU_CNBU_Changing_map = np.array( Image.open(CBU_CNBU_Chaning_map_filepath) )
    # print( np.unique(CBU_CNBU_Changing_map, return_counts=True) )

    min_lat, max_lat, min_lon, max_lon = Get_district_bounding_box( 'district_coordinates.csv', district )
    # Since the grid size (0.01) is of precision 2, round off the image bounding box to fit all the grids
    rounded_min_lat = floor(100.0 * min_lat) / 100.0
    rounded_max_lat = ceil(100.0 * max_lat) / 100.0
    rounded_min_lon = floor(100.0 * min_lon) / 100.0
    rounded_max_lon = ceil(100.0 * max_lon) / 100.0

    # Pad the image to fill gap between tight bounds and rounded bounds
    padded_CBU_CNBU_Changing_map = Pad_image(CBU_CNBU_Changing_map, min_lat, max_lat, min_lon, max_lon, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon)

    # The years under analysis, first_year = 2016, last_year = 2019
    padded_BU_NBU_first_year, padded_BU_NBU_last_year = Get_BU_NBU_maps(padded_CBU_CNBU_Changing_map)
    print("padded first year: ", np.unique(padded_BU_NBU_first_year, return_counts=True) )
    print("padded last year: ", np.unique(padded_BU_NBU_last_year, return_counts=True) )

    # find the Urban/Periurban/Rural i.e U_PU_R pixel-level mapping
    U_PU_R_first_year, U_PU_R_last_year = Compute_urban_extent(padded_BU_NBU_first_year, padded_BU_NBU_last_year, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon)
    print('U_PU_R 2016: \t', np.unique(U_PU_R_first_year, return_counts=True) )
    print('U_PU_R 2019: \t', np.unique(U_PU_R_last_year, return_counts=True) )

    save_image_directory = 'Visualization_Results/U_PU_R_maps/'+district
    os.makedirs(save_image_directory, exist_ok = True)
    Plot_U_PU_R_map(district, U_PU_R_first_year, '2016', save_image_directory)
    Plot_U_PU_R_map(district, U_PU_R_last_year, '2019', save_image_directory)

    #we rotate the matrix by 90deg in clockwise direction. 
    #This is done to traverse the matrix by grid number 0---n 
    #because grids are numbered from bottom left to top in computing road indicators
    rotated_U_PU_R_first = np.rot90(U_PU_R_first_year, 1, (1,0)) 
    rotated_U_PU_R_last = np.rot90(U_PU_R_last_year, 1, (1,0))
    
    Results_dataframe_first = Get_grid_urban_indicators(rotated_U_PU_R_first, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon)
    Results_dataframe_last = Get_grid_urban_indicators(rotated_U_PU_R_last, rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon)

    Results_dataframe_first.insert(0, "District_name", np.full(len(Results_dataframe_first), district))
    Results_dataframe_last.insert(0, "District_name", np.full(len(Results_dataframe_last), district))
    results_directory = "Grid_wise_urban_indicators/"+district
    os.makedirs(results_directory, exist_ok = True)

    first_year = '2016'
    last_year = '2019'
    result_filename_first = district+"_urban_indicators_"+first_year+".csv"
    result_filename_last = district+"_urban_indicators_"+last_year+".csv"

    Results_dataframe_first.to_csv(results_directory+'/'+result_filename_first, index=False)
    Results_dataframe_last.to_csv(results_directory+'/'+result_filename_last, index=False)

    print(district," Complete!")

print("Execution Complete!")



