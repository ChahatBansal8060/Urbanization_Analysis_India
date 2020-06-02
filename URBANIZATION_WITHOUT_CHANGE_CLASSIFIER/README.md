# Analysis of urbanization patterns in India

## Project Overview
With growing urbanization, being able to track urban change is important to plan cities better. Land-use classification of satellite data has been actively used for this purpose. We augment this analysis through the use of crowd-sourced data about the road network in cities, obtained through the Open Street Maps platform. We develop several indicators to quantify the spatial layout of cities and how different localities have changed over time. We apply our methods to study seven Indian cities (Bangalore, Chennai, Delhi, Gurgaon, Hyderabad, Kolkata, and Mumbai). Our contribution lies in synthesizing two freely available datasets of satellite imagery and road information to develop a series of standardized indicators for different aspects of urbanization, which can serve to compare various cities with one another and to track change happening in the cities over time.   

## Prerequisites
* Open Street Maps(OSM) to download the road network of specified areas
* Following python libraries to run the python scripts
    * PIL (Pillow)
    * scipy
    * numpy
    * pandas
    * matplotlib
* QGIS and Google Earth Pro for visualization of results

## Dataset
1) The dataset of 4 land-cover classes generated using the classifier of IndiaSat project for each of the desired cities. It is kept in the folder named **Landcover\_Predictions\_Using\_IndiaSat**. Each year's prediction is stored as &lt;DistrictName&gt;\<DistrictName&gt;\_prediction\_&lt;Year&gt;.png

## Scripts
A detailed step-wise description of the implementation is present in the wiki pages of this repository. The following scripts are used for the project in order of execution-
1) **compressClasses_to_BU_NBU.py-**  The per-pixel final results from IndiaSat project are of 4 land-cover classes- green, water, builtup, and barren land. Using this script, these 4 classes are compressed into 2 classes: built-up (BU), and non-built-up (NBU).
2) **Download_OSM_data.py-** It downloads the OSM data for each district.
3) **Extract_Roads_From_OSM.py-** It extracts the nodes and ways associated with roads of a district.
4) **Generate_grid_road_parameters.py-** It uses the OSM data to compute different road-based indicators at grid-level in a district.
5) **Generate_grid_urban_parameters.py-** It uses BU/NBU maps to compute urban indicators for each district at both pixel-level and grid-level.
6) **Cluster_urbanized_grids.py-** It uses agglomerative clustering to cluster the urbanized grids of all districts together and define appropriate class-labels based on manual interpretation.
7) **Visualize_indicators.py-** It is used to visualize the districts with different grid-level indicators.
8) **Create_Files_For_Histograms.py-** It is used create datafiles which can be used to create histograms making results more interpretable.


## Contact
If you have problems, questions, ideas or suggestions, please contact us by posting to this mailing list-
* Chahat Bansal- chahat.bansal@cse.iitd.ac.in


