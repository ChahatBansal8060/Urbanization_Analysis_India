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

## Understanding the directory structure
This repository contains three directories having the complete code and results of different threads being tested in this project. The following threads have been carried out-
* **COMPASS_FINAL_VERSION-** This directory holds the final project implementation corresponding to the publication in ACM SIGCAS Computing and Sustainable Societies (COMPASS 2020). The README file within the directory holds all the information.
* **URBANIZATION_WITH_NEW_CHANGE_CLASSIFIER-** This directory holds the ongoing changes in the improvement of this project. The README file within the directory holds all the information.
* **URBANIZATION_WITHOUT_CHANGE_CLASSIFIER-** This directory holds the project implementation which eliminates the implementation of Change Classifier in the project. The README file within the directory holds all the information.

> It is to be noted that the WIKI pages of this repository holds a detailed description of all the scripts. It includes the intuition behind the code, the input and output description as well. Do check them out.

## Contact
If you have problems, questions, ideas or suggestions, please contact us by posting to this mailing list-
* Chahat Bansal- chahat.bansal@cse.iitd.ac.in



