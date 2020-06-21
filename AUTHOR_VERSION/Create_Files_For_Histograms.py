import numpy as np
import pandas as pd 
from PIL import Image
import os, sys


'''
This function computes the density of Urban, Periurban, and Rural pixels in each district
Input:
1) districts = List of all districts for which the density is to be computed
2) year = The year for which the density is to be computed
Output:
1) District_results_df = The dataframe with each pixel-type density reported against the district name 
'''
def Find_percentage_U_PU_R_pixels(districts, year):
    print("**********************Finding Density of Urban/Rural/Periurban Pixels**********************")
    Urban_percent_list = []
    Periurban_percent_list = []
    Rural_percent_list = []

    for district in districts:
        print('Processing ',district,' in year ',year)
        U_PU_R_imagepath = 'Visualization_Results/U_PU_R_maps/'+district+'/'+district+'_U_PU_R_colored_prediction_'+year+'.png'
        U_PU_R_map = np.array( Image.open(U_PU_R_imagepath).convert("RGB") )
        
        u_count = 0
        pu_count = 0
        r_count = 0
        for i in range(U_PU_R_map.shape[0]):
            for j in range(U_PU_R_map.shape[1]):
                if (U_PU_R_map[i][j] == np.array([150, 40, 27])).all() == True:
                    u_count += 1
                elif (U_PU_R_map[i][j] == np.array([255, 140, 0])).all() == True:
                    pu_count += 1
                elif (U_PU_R_map[i][j] == np.array([255, 255, 255])).all() == True:
                    r_count += 1
                
        total_count = u_count + pu_count + r_count

        Urban_percent_list.append(float( u_count / total_count )*100)
        Periurban_percent_list.append(float( pu_count / total_count )*100)
        Rural_percent_list.append(float( r_count / total_count )*100)
        
    Zipped_results =  list(zip(districts, Urban_percent_list, Periurban_percent_list, Rural_percent_list))
    District_results_df = pd.DataFrame(Zipped_results, columns=['District_name','%Urban_pixels_'+year,'%Periurban_pixels_'+year, '%Rural_pixels_'+year])
    return District_results_df


'''
This function computes the density of C1-C5 grids in percentages for each district
Inputs:
1) districts = list of all districts under consideration
2) year = the year for which the class densities are computed
Outputs:
1) result_dataframe = It stores the percent density of each class against each district for a particular year 
'''
def Find_percentage_grid_classes(districts, year):
    print(year,": ******************* Finding density of C1-C5 urban grids**********************")
    result_dataframe = pd.DataFrame()
    result_dataframe['District_name'] = districts
    
    class_label_list = [1,2,3,4,5]
    for class_label in class_label_list:
        print('Processing class label-',class_label)
        density_list = []
        for district in districts:
            all_indicator_df = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_"+str(year)+"_all_indicators.csv")
            grid_classes = all_indicator_df['Class_label'].values.astype(int)
            #remove all 0 class labels as they belong to rejected grids
            grid_classes = grid_classes[ grid_classes != 0 ]
            
            if class_label in grid_classes:
                density = ( np.count_nonzero(grid_classes == class_label) )/ np.sum(grid_classes)
                density_list.append(density * 100) #for percentages 
            else:
                density_list.append(0.0)
        
        result_dataframe['%C'+str(class_label)+' Grids '+str(year)] = density_list        
    return result_dataframe


'''
This function is used to plot transition matrix 
'''
def Get_Class_Transition_Matrix(districts):
    for district in districts:
        print('Processing ',district)
        all_indicator_df_2016 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2016_all_indicators.csv")
        all_indicator_df_2019 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2019_all_indicators.csv")

        grid_classes_2016 = all_indicator_df_2016['Class_label'].values.astype(int)
        grid_classes_2019 = all_indicator_df_2019['Class_label'].values.astype(int)

        label_list = np.array([0,1,2,3,4,5])
        missing_label_in_2016 = np.setdiff1d(label_list, np.unique(grid_classes_2016))
        
        # manually induced error to ensure each label is present atleast once in 2016
        for i in range(len(missing_label_in_2016)):
            grid_classes_2016[i] = missing_label_in_2016[i] 

        df_confusion = pd.crosstab(grid_classes_2016, grid_classes_2019)
        #df_confusion = df_confusion / df_confusion.sum(axis=1)[:,None]
        #df_confusion = df_confusion * 100.0
        #df_confusion = np.round(df_confusion,2)
        print(df_confusion,"\n\n")
        

'''
This function computes the number of grids which change from Rural grids to Urban or Periurban grids
Input:
1) districts = list of all districts
'''
def Compute_Rural_To_Urban_Grids(districts):
    print("**********************Finding Number of Rural--->Urbanized Pixels**********************")    
    for district in districts:
        print('Processing ',district)
        imagepath_2016 = 'Visualization_Results/U_PU_R_maps/'+district+'/'+district+'_U_PU_R_colored_prediction_2016.png'
        imagepath_2019 = 'Visualization_Results/U_PU_R_maps/'+district+'/'+district+'_U_PU_R_colored_prediction_2019.png'
        
        map_2016 = np.array( Image.open(imagepath_2016).convert("RGB") )
        map_2019 = np.array( Image.open(imagepath_2019).convert("RGB") )
        
        transition_count = 0
        for i in range(map_2016.shape[0]):
            for j in range(map_2016.shape[1]):
                if (map_2016[i][j] == np.array([255, 255, 255])).all() == True:
                    if (map_2019[i][j] == np.array([255, 255, 255])).all() == False and (map_2019[i][j] == np.array([0, 0, 0])).all() == False:
                        transition_count += 1
        print("Number of rural to urbanized pixels are: ",transition_count)


'''
Find number of new selected grids from 2016 to 2019
'''
def Get_New_Selected_Grids(districts):
    for district in districts:
        print('Processing ',district)
        all_indicator_df_2016 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2016_all_indicators.csv")
        all_indicator_df_2019 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2019_all_indicators.csv")

        grid_classes_2016 = all_indicator_df_2016['Class_label'].values.astype(int)
        grid_classes_2019 = all_indicator_df_2019['Class_label'].values.astype(int)

        grid_classes_2016 = grid_classes_2016[ grid_classes_2016 != 0 ]
        grid_classes_2019 = grid_classes_2019[ grid_classes_2019 != 0 ]

        print("Selected grids in 2016: ", len(grid_classes_2016))
        print("Selected grids in 2019: ", len(grid_classes_2019))

        increase_count = (len(grid_classes_2019) - len(grid_classes_2016)) / len(grid_classes_2016)
        print("Increase in density of selected grids from 2016 to 2019: ", increase_count) 


'''
This function computes the increased density in C1-C5 grids.
Note- It is increased density and not increase in density
'''
def Get_Increased_Grid_Class_Density(districts):
    result_dataframe = pd.DataFrame()
    result_dataframe['District_name'] = districts

    class_labels = [1, 2, 3, 4, 5]
    for class_label in class_labels:
        print('Processing Class',class_label)
        current_densities = []
        for district in districts:
            all_indicator_df_2016 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2016_all_indicators.csv")
            all_indicator_df_2019 = pd.read_csv("Grid_wise_all_indicators/"+district+"/"+district+"_2019_all_indicators.csv")

            grid_classes_2016 = all_indicator_df_2016['Class_label'].values.astype(int)
            grid_classes_2019 = all_indicator_df_2019['Class_label'].values.astype(int)
            grid_classes_2016 = grid_classes_2016[ grid_classes_2016 != 0 ]
            grid_classes_2019 = grid_classes_2019[ grid_classes_2019 != 0 ]

            if class_label in grid_classes_2016:
                unique_labels_2016, frequencies_2016 = np.unique(grid_classes_2016, return_counts=True)
                unique_labels_2019, frequencies_2019 = np.unique(grid_classes_2019, return_counts=True)
                count_2016 = int(frequencies_2016[ np.where(unique_labels_2016 == class_label) ])
                
                if class_label in unique_labels_2019:
                    count_2019 = int(frequencies_2019[ np.where(unique_labels_2019 == class_label) ])
                else:
                    count_2019 = 0
                
                density_2016 = count_2016 / np.sum(frequencies_2016)
                density_2019 = count_2019 / np.sum(frequencies_2019)
                percentage_increased_density = ( (density_2019 - density_2016) / density_2016 )*100
                current_densities.append(percentage_increased_density)
            else:
                current_densities.append(0.0)

        result_dataframe['%Increase C'+str(class_label)+' Grid Density'] = current_densities
    return result_dataframe


'''
Driver code begins here
'''
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
years = ['2016', '2019']

final_result_folder = "Visualization_Results/Files_for_histograms"
os.makedirs(final_result_folder, exist_ok=True)

# Print the increase in the count of selected grids from 2016->2019
Get_New_Selected_Grids(districts)

# Calculating density of urban/periurban/rural pixels
U_PU_R_df = pd.DataFrame()
for year in years:
   curr_dataframe = Find_percentage_U_PU_R_pixels(districts, year)
   if U_PU_R_df.empty:
       U_PU_R_df = curr_dataframe.copy()
   else:
       U_PU_R_df = pd.merge(U_PU_R_df, curr_dataframe, left_on='District_name', right_on='District_name', how='inner')
U_PU_R_df.to_csv(final_result_folder+"/District_level_urban_densities.csv", index=False)

# Check what size of rural area converted to urban/periurban
Compute_Rural_To_Urban_Grids(districts)

# Calculating density of C1-C5 grids 
grid_class_df = pd.DataFrame()
for year in years:
   curr_dataframe = Find_percentage_grid_classes(districts, year)
   if grid_class_df.empty:
       grid_class_df = curr_dataframe.copy()
   else:
       grid_class_df = pd.merge(grid_class_df, curr_dataframe, left_on='District_name', right_on='District_name', how='inner')
grid_class_df.to_csv(final_result_folder+"/District_level_grid_class_densities.csv", index=False)

# Computing transition matrices of C1->C5 grids
Get_Class_Transition_Matrix(districts)

# Find the increase in the density of C1-C5 classes from 2016->2019
result_dataframe = Get_Increased_Grid_Class_Density(districts)
result_dataframe.to_csv(final_result_folder+"/Increase_In_Class_Density.csv",index=False)


