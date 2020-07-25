# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

import numpy as np
import pandas as pd
from IPython.display import display
from sklearn.preprocessing import minmax_scale
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
import sys, os


'''
This function plots the dendrogram plot of hierarchical clusters
Inputs:
1) feature_vectors: feature vector of grids belonging to a particular cluster
2) title: title of the plot
3) save_filename: complete path where the image is to be stored
'''
def Plot_dendrogram(feature_vectors, title, save_filename):
    plt.figure(figsize = (15,8))  
    plt.title(title)
    plt.xlabel('Grid')
    plt.ylabel('distance')
    dendrogram = shc.dendrogram(shc.linkage(feature_vectors, method='ward'), 
                            leaf_rotation = 90.,  # rotates the x axis labels
                            leaf_font_size = 8.,  # font size for the x axis labels
                            )
    plt.savefig(save_filename)
    # plt.show()


'''
This function makes the boxplot of cluster using the feature vector of grids belonging to it
Inputs:
1) cluster_feature_vectors = feature vectors of the grids belonging to the cluster
2) title = title of the boxplot
'''
def Plot_boxplot(cluster_feature_vectors, title, save_filename):
    figure, axis = plt.subplots()
    axis.set_title(title)
    axis.set_ylim(-0.1, 1.1)
    axis.boxplot(cluster_feature_vectors, labels = ['#3-ways', '#4-ways', 'WR', 'Urb_footprint'])
    axis.tick_params(labelsize = 14)
    plt.savefig(save_filename, bbox_inches = 'tight', pad_inches = 0)


'''
This function creates a combined file for each district storing road indicators, urban indicators, and class labels
Inputs:
1) districts = list of all districts
2) class_information_dataframe = A dataframe of combined districts having columns ['District_name','Grid_number','Class_label']
3) year = The year for which data of district is stored
Outputs:
1) Separate file is written for each district and each year holding all urban and road indicators at grid level along with class label
Rejected grids (non-urbanized grids) are assigned class label 0
ClassI-ClassV grids (selected urbanized grids) are assigned integer values from 1-5 respectively
'''
def Save_grid_level_indicators(districts, class_information_dataframe, year):
    final_directory = 'Grid_wise_all_indicators'
    grouped_dataframe_class_labels = class_information_dataframe.groupby(class_information_dataframe.District_name)

    for district in districts:
        os.makedirs(final_directory+'/'+district, exist_ok = True)

        road_indicators_filename =  'Grid_wise_road_indicators/'+district+'_road_indicators.csv'
        road_indicators_df = pd.read_csv(road_indicators_filename)
        urban_indicators_filename =  'Grid_wise_urban_indicators/'+district+'/'+district+'_urban_indicators_'+year+'.csv'
        urban_indicators_df = pd.read_csv(urban_indicators_filename)
        # merge both road and urban indicators in a common dataframe
        merged_dataframe = pd.merge(road_indicators_df, urban_indicators_df, left_on='Grid_number', right_on='Grid_number', how='inner')

        dataframe_class_labels = grouped_dataframe_class_labels.get_group(district)
        final_dataframe = pd.merge(merged_dataframe, dataframe_class_labels, left_on=['Grid_number','District_name'], right_on=['Grid_number','District_name'], how='left')
        final_dataframe.sort_values(by=['Grid_number'], inplace=True)
        final_dataframe['Class_label'] = final_dataframe['Class_label'].fillna(0)
        final_dataframe.to_csv(final_directory+'/'+district+'/'+district+'_'+year+'_all_indicators.csv', index=False)

    #print("\n Grid-level indicators successfully written to file")


'''
Driver code begins here for the year 2019
'''
#print("\n *********** Categorizing Urbanized Grids ***********\n")
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
year = '2019'

combined_dataframe_all_districts = pd.DataFrame() 
for district in districts:
    road_indicators_filename =  'Grid_wise_road_indicators/'+district+'_road_indicators.csv'
    road_indicators_df = pd.read_csv(road_indicators_filename)
    urban_indicators_filename =  'Grid_wise_urban_indicators/'+district+'/'+district+'_urban_indicators_'+year+'.csv'
    urban_indicators_df = pd.read_csv(urban_indicators_filename)
    # merge both road and urban indicators in a common dataframe
    merged_dataframe = pd.merge(road_indicators_df, urban_indicators_df, left_on='Grid_number', right_on='Grid_number', how='inner')
    combined_dataframe_all_districts = combined_dataframe_all_districts.append(merged_dataframe)

# Find only sufficiently urbanized grids for further analysis (i.e. urban and periurban)
selected_grid_types = ['Urban','PeriUrban']
selected_grids_dataframe = combined_dataframe_all_districts.loc[combined_dataframe_all_districts['Grid_type'].isin(selected_grid_types)].copy() 

# select only those columns of dataframe on which clustering is to implemented
clustering_dataframe = selected_grids_dataframe[['Three_ways','Four_ways','Walkability_ratio','Urban_percentage']].copy()

clustering_feature_vectors = np.array(clustering_dataframe)
# normalize the feature vector of each grid
norm_feature_vectors = minmax_scale(clustering_feature_vectors, feature_range=(0,1), axis=0)

# add 1 and take log of columns with huge difference in the their minimum and maximum value
norm_feature_vectors[:, 0:2] = norm_feature_vectors[:, 0:2] + 1
norm_feature_vectors[:, 0:2] = np.log2(norm_feature_vectors[:, 0:2])

global_mean = norm_feature_vectors.mean(axis=0)
print("\nThe global mean in order #3way | #4way | WR | UF \n",global_mean,"\n")

save_fig_directory = "Visualization_Results/Clustering_figures_2019"
os.makedirs(save_fig_directory, exist_ok=True)
# plot the dendogram plot of the hierarchical clustering
title = 'Dendrogram of hierarchical clustering of all selected grids '+year
Plot_dendrogram(norm_feature_vectors, title, save_fig_directory+"/Dendrogram_all_grids_2019")





'''
This is where manual interpretation will start working!
'''
# We can visually see that the longest vertical line is the blue one 
# and we cut at that line to get 2 clusters. Now we assign all our data points to these 2 clusters first
number_of_clusters = 5
agglomerative_clusters = AgglomerativeClustering(n_clusters = number_of_clusters, affinity = 'euclidean', linkage = 'ward')
cluster_grid_mapping = agglomerative_clusters.fit_predict(norm_feature_vectors)

clusters_feature_vectors = [] # this list stores the feature vector of all grids belongs to all clusters
clusters_grid_info = [] # this list stores complete information of all grids belongs to all clusters
for i in range(number_of_clusters):
    clusters_feature_vectors.append( norm_feature_vectors[ cluster_grid_mapping == i ] )
    clusters_grid_info.append( selected_grids_dataframe[ cluster_grid_mapping == i ].copy() )

# at this point, clusters_feature_vectors[i] contains the list of feature vector of all grids belonging to cluster i
# at this point, clusters_grid_info[i] contains the list of information of all grids belonging to cluster i

# create boxplots of each of the clusters
for cluster_id in range(len(clusters_feature_vectors)):
    title = year+' Cluster-'+str(cluster_id)+' size: '+str(clusters_feature_vectors[cluster_id].shape[0])
    save_filename = save_fig_directory+"/Boxplot_Major_cluster"+str(cluster_id)+"_2019"
    Plot_boxplot(clusters_feature_vectors[cluster_id], title, save_filename)
#plt.show()

# plot the dendogram plot of each of the major clusters
for cluster_id in range(len(clusters_feature_vectors)):
    title = 'Dendrogram of hierarchical clustering of major cluster-'+str(cluster_id)+' '+year
    save_filename = save_fig_directory+"/Dendrogram_Major_cluster"+str(cluster_id)+"_2019"
    Plot_dendrogram(clusters_feature_vectors[cluster_id], title, save_filename)    

# Print average values of each major cluster
for cluster_id in range(len(clusters_feature_vectors)):
   print("\n**********Major Cluster ",cluster_id,": ***********")
   print(clusters_feature_vectors[cluster_id].mean(axis=0))
   print("\n")

'''
Based on manual interpretation, we will assign class 1-5 as labels to all urbanized grids.
Some clusters will be merged and others will be re-labelled
Major cluster 0:
    sub-cluster 0 = Class-I (1)
    sub-cluster 1 = Class-V (5)
    sub-cluster 2 = Class-III (3)
    sub-cluster 3 = Class-IV (4)
    sub-cluster 4 = Class-II (2)
'''
# assigning class labels to major clusters
for i in range(len(clusters_feature_vectors)):
   if i == 0:
       clusters_grid_info[i]["Class_label"] = [1] * len(clusters_grid_info[i])
   elif i == 1:
       clusters_grid_info[i]["Class_label"] = [5] * len(clusters_grid_info[i])
   elif i == 2:
       clusters_grid_info[i]["Class_label"] = [3] * len(clusters_grid_info[i])
   elif i == 3:
       clusters_grid_info[i]["Class_label"] = [4] * len(clusters_grid_info[i])
   elif i == 4:
       clusters_grid_info[i]["Class_label"] = [2] * len(clusters_grid_info[i])


# Merge desired clusters as per their labels
final_clusters = []
# Class 1
final_clusters.append( clusters_feature_vectors[0].copy() )
# Class 2
final_clusters.append( clusters_feature_vectors[4].copy() )
# Class 3
final_clusters.append( clusters_feature_vectors[2].copy() )
# Class 4
final_clusters.append( clusters_feature_vectors[3].copy() )
# Class 5
final_clusters.append( clusters_feature_vectors[1].copy() )


# make boxplots of final clusters
for cluster_id in range(len(final_clusters)):
    title = year+' Class-'+str(cluster_id+1)+' size: '+str(final_clusters[cluster_id].shape[0])
    save_filename = save_fig_directory+"/Final_Boxplot_class"+str(cluster_id+1)+"_2019"
    Plot_boxplot(final_clusters[cluster_id], title, save_filename)


'''
Saving the centroids of each cluster to map the grids of year 2016
'''
Class1_mean_2019 = final_clusters[0].mean(axis=0)
Class2_mean_2019 = final_clusters[1].mean(axis=0)
Class3_mean_2019 = final_clusters[2].mean(axis=0)
Class4_mean_2019 = final_clusters[3].mean(axis=0)
Class5_mean_2019 = final_clusters[4].mean(axis=0)

print("\n\n********** The Mean Values Of Final Clusters **********")
print("\n Class 1: ", Class1_mean_2019)
print("\n Class 2: ", Class2_mean_2019)
print("\n Class 3: ", Class3_mean_2019)
print("\n Class 4: ", Class4_mean_2019)
print("\n Class 5: ", Class5_mean_2019)

'''
Writing the class labels to the file of urban indicators for each district
'''
final_dataframe = pd.DataFrame()
final_column_list = ['District_name','Grid_number','Class_label']

for cluster_id in range(len(clusters_grid_info)):
   curr_dataframe = clusters_grid_info[cluster_id][final_column_list].copy()
   final_dataframe = final_dataframe.append( curr_dataframe )

Save_grid_level_indicators(districts, final_dataframe, year)
print("\n**** Clustering complete for year: ",year," ****\n")


'''
Driver code begins here for the year 2016. 
It uses the centers of 2019 clusters to assign each grid in 2016 an appropriate class label
'''
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
year = '2016'

combined_dataframe_all_districts = pd.DataFrame() 
for district in districts:
    road_indicators_filename =  'Grid_wise_road_indicators/'+district+'_road_indicators.csv'
    road_indicators_df = pd.read_csv(road_indicators_filename)
    urban_indicators_filename =  'Grid_wise_urban_indicators/'+district+'/'+district+'_urban_indicators_'+year+'.csv'
    urban_indicators_df = pd.read_csv(urban_indicators_filename)
    # merge both road and urban indicators in a common dataframe
    merged_dataframe = pd.merge(road_indicators_df, urban_indicators_df, left_on='Grid_number', right_on='Grid_number', how='inner')
    combined_dataframe_all_districts = combined_dataframe_all_districts.append(merged_dataframe)

# Find only sufficiently urbanized grids for further analysis (i.e. urban and periurban)
selected_grid_types = ['Urban','PeriUrban']
selected_grids_dataframe = combined_dataframe_all_districts.loc[combined_dataframe_all_districts['Grid_type'].isin(selected_grid_types)].copy() 

# select only those columns of dataframe on which clustering is to implemented
clustering_dataframe = selected_grids_dataframe[['Three_ways','Four_ways','Walkability_ratio','Urban_percentage']].copy()

clustering_feature_vectors = np.array(clustering_dataframe)
# normalize the feature vector of each grid
norm_feature_vectors = minmax_scale(clustering_feature_vectors, feature_range=(0,1), axis=0)

# add 1 and take log of columns with huge difference in the their minimum and maximum value
norm_feature_vectors[:, 0:2] = norm_feature_vectors[:, 0:2] + 1
norm_feature_vectors[:, 0:2] = np.log2(norm_feature_vectors[:, 0:2])

# Class1_mean_2019
# Class2_mean_2019
# Class3_mean_2019
# Class4_mean_2019
# Class5_mean_2019

final_labels_2016 = []
for grid_id in range(len(norm_feature_vectors)):
    dist_class1 = np.linalg.norm(norm_feature_vectors[grid_id] - Class1_mean_2019)
    dist_class2 = np.linalg.norm(norm_feature_vectors[grid_id] - Class2_mean_2019)
    dist_class3 = np.linalg.norm(norm_feature_vectors[grid_id] - Class3_mean_2019)
    dist_class4 = np.linalg.norm(norm_feature_vectors[grid_id] - Class4_mean_2019)
    dist_class5 = np.linalg.norm(norm_feature_vectors[grid_id] - Class5_mean_2019)

    Min_distance = min( dist_class1, dist_class2, dist_class3, dist_class4, dist_class5 )
    if(Min_distance == dist_class1):
        final_labels_2016.append(1)
    elif(Min_distance == dist_class2):
        final_labels_2016.append(2)
    elif(Min_distance == dist_class3):
        final_labels_2016.append(3)
    elif(Min_distance == dist_class4):
        final_labels_2016.append(4)
    elif(Min_distance == dist_class5):
        final_labels_2016.append(5)

selected_grids_dataframe['Class_label'] = final_labels_2016

final_column_list = ['District_name','Grid_number','Class_label']
final_dataframe = selected_grids_dataframe[final_column_list].copy()
    
Save_grid_level_indicators(districts, final_dataframe, year)
print("**** Clustering complete for year: ",year," ****\n")

print("\n#### Check Grid_wise_all_indicators directory for the results!! ####\n")


