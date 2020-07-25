#!/bin/bash

## ----------------------------------
# Step #1: Define variables
# ----------------------------------
EDITOR=vim
PASSWD=/etc/passwd
RED='\033[0;41;30m'
STD='\033[0;0;39m'
columns="$(tput cols)"
 
# ----------------------------------
# Step #2: User defined function
# ----------------------------------
pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}

#This functions prints the text in the center of the screen
print_center(){
	printf "%*s\n" $(( (${#1} + $columns) / 2)) "$1"
}

#This function executes the change classifier
run_change_classifier(){		
	echo
        print_center "**** EXECUTING THE CHANGE CLASSIFIER ****"
	echo 
	echo
	print_center "Step 1) Converting Landcover Images to BU/NBU maps"
	python3 compressClasses_to_BU_NBU.py
	echo	
	print_center "Step 2) Executing Builtup Change Detection"
        python3 Change_classifier.py
	python3 Create_Colored_Change_Maps.py 
        pause
}
 
#This function evaluates the performance of change classifier
test_change_classifier_accuracy (){
	echo
        print_center "**** TESTING THE ACCURACY OF THE CHANGE CLASSIFIER ****"
	echo 
	echo
	print_center "Step 1) Converting PNG Images of CBU/CNBU/Changing Maps into TIFF files"
	python3 png_to_tif.py
	echo
	print_center "Step 2) Cutting The Tiffiles Using Groundtruth Shapefiles"
	python3 Cut_tifffile_using_groundtruth_shapefiles.py
	echo	
	print_center "Step 3) Balancing The Groundtruth For Better Accuracy Testing"
	python3 groundtruth_preprocessing.py
	echo	
	print_center "Step 4) Compute Accuracy"
	python3 Compute_accuracies_change_classifier.py > result_change_classifier_accuracies.txt
	echo "#### Check result_change_classifier_accuracies.txt file for the accuracy results ####\n"
        pause
}

#This function creates spatial urban indicators
compute_urban_indicators (){
	echo
        print_center "**** COMPUTING SPATIAL URBAN INDICATORS ****"
	echo 
	echo
	echo "--- This script takes time to execute. Please keep patience. --"
	python3 Generate_grid_urban_parameters.py
	pause
}

#This function computes road-based indicators at grid-level
compute_road_indicatos (){
	echo
        print_center "**** COMPUTING ROAD-BASED INDICATORS ****"
	echo 
	echo
	
	print_center "Step 1) Downloading the OSM Data"
	echo "****************************************"
	echo "Do you want to download the OSM data ??"
	echo "****************************************"
	echo "1. YES"
	echo "2. NO"
	local choice
	read -p "Enter choice [ 1 or 2] " choice
	case $choice in
		1) echo "--- This script takes time to execute. Please keep patience. --"
		   python3 Download_OSM_data.py ;;
		2) echo "\n#### Make sure that you have the OSM data in the Raw_OSM_data directory ####\n" ;;		
		*) echo "${RED}Error...Wrong Choice!! Wait for 4 seconds and enter the new choice! ${STD}" && sleep 4
	esac

	echo
	print_center "Step 2) Extracting Road Information From The Raw OSM Data"
	echo "**********************************************************************"
	echo "Do you want to process the raw OSM data or have you done it already ??"
	echo "**********************************************************************"
	echo "1. YES"
	echo "2. NO"
	local choice
	read -p "Enter choice [ 1 or 2] " choice
	case $choice in
		1) echo "--- This script takes time and a high computational power to execute. Execute this script 1 city at a time and Please keep patience. --"
		   python3 Extract_Roads_From_OSM.py ;;
		2) echo "\n#### Make sure that you have the Processed OSM data in the Processed_OSM_data directory ####\n" ;;		
		*) echo "${RED}Error...Wrong Choice!! Wait for 4 seconds and enter the new choice! ${STD}" && sleep 4
	esac

	echo
	print_center "Step 3) Computing Grid-wise Road-based Indicators"
	echo "--- This script takes time to execute. Please keep patience. --"
	python3 Generate_grid_road_parameters.py
	pause
}


#This function clusters the urbanized grids
cluster_urbanized_grids (){
	echo
        print_center "**** CLUSTER URBANIZED GRIDS ****"
	echo 
	echo
	echo "--- This script involves manual interpretation of clusters and some hit and trial. Not every human instinct can be automated! ---"
	python3 Cluster_urbanized_grids.py
	pause
}

#This function creates datafiles for the final histograms
create_result_files (){
	echo
        print_center "**** CREATE VISUALIZATIONS & DIFFERENT DATAFILES FOR HISTOGRAMS ****"
	echo 
	echo
	print_center "Step 1) Create Visualizations at pixel and grid level"
	python3 Visualize_indicators.py
	echo	
	print_center "Step 2) Create Datafiles For Histograms"
	python3 Create_Files_For_Histograms.py
	echo
	print_center "-------------------------------------------------------------"
	print_center "HERE WE COME TO AN END OF THE PROJECT!! THANK YOU!!"
	print_center "-------------------------------------------------------------"
	pause
}
 
# function to display menus
show_menus() {
	echo 	
	echo "~~~~~~~~~~~~~~~~~~~~~"	
	echo " M A I N - M E N U"
	echo "~~~~~~~~~~~~~~~~~~~~~"
	echo "1. Run Change Classifier"
	echo "2. Test Accuracy of Change Classifier"
	echo "3. Compute Spatial Urban Indicators"
	echo "4. Compute Road-based Indicators"
	echo "5. Cluster Urbanized Grids"
	echo "6. Prepare Visualizations and Result Datafiles For Histograms"
	echo "7. Exit"
}

# read input from the keyboard and take a action
# Exit when user the user select 7 form the menu option.
read_options(){
	local choice
	read -p "Enter choice [ 1 - 7] " choice
	case $choice in
		1) run_change_classifier ;;
		2) test_change_classifier_accuracy ;;
		3) compute_urban_indicators ;;
		4) compute_road_indicatos ;;
		5) cluster_urbanized_grids ;;
		6) create_result_files ;;
		7) exit 0;;
		*) echo "${RED}Error...Wrong Choice!! Wait for 4 seconds and enter the new choice! ${STD}" && sleep 4
	esac
}
 
 
# -----------------------------------
# Step #4: Main logic - infinite loop
# ------------------------------------
while true
do
 
	show_menus
	read_options
done

