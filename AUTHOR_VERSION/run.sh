#!/bin/bash

# Creating CBU/CNBU/Changing maps using change classifier
python3 compressClasses_to_BU_NBU.py
python3 Linear_regression_on_pixels.py
python3 Change_classifier.py

# Checking the accuracy of CBU/CNBU/Changing maps over a balanced groundtruth
python3 png_to_tif.py
python3 Cut_tifffile_using_groundtruth_shapefiles.py
python3 groundtruth_preprocessing.py
python3 Compute_accuracies_change_classifier.py > Results_Accuracy_CBU_CNBU_Changing_Maps.txt

#Predicting urban indicators
python3 Generate_grid_urban_parameters.py

#Predicting road-based indicators
python3 Download_OSM_data.py
python3 Extract_Roads_From_OSM.py
python3 Generate_grid_road_parameters.py

#Categorization of Urbanized Grids
python3 Cluster_urbanized_grids.py

#Visualizing the results
python3 Visualize_indicators.py
python3 Create_Files_For_Histograms.py


