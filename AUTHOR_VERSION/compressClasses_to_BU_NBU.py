# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

from PIL import Image
import numpy as np
import pandas as pd
import os, sys

print("\n ************* Compressing Land-cover Classes to BU/NBU Category **************\n")

# define color coding used in prediction images
Background = 0
Green = 1
Water = 2
Builtup = 3
Barrenland = 4

districts=['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
years = ['2016', '2017', '2018', '2019']

destination_directory = 'BU_NBU_maps'
os.makedirs( destination_directory, exist_ok = True )

for district in districts:
    for year in years:
        image_filename = 'Landcover_Predictions_Using_IndiaSat/'+district+'/'+district+'_prediction_'+year+'.png'
        image = np.array( Image.open(image_filename) )
         
        # keep built-up pixels as it is i.e. BU with color code (1 * 65)
        image[ image == 3 ] = 65
        # keep green, water, and barrenland pixels as non-built-up i.e. NBU with color code (2 x 65)
        image[ image == 1 ] = 130
        image[ image == 2 ] = 130
        image[ image == 4 ] = 130

        os.makedirs( destination_directory+'/'+district, exist_ok = True )

        image = ( Image.fromarray(image) ).convert("L")
        image.save(destination_directory+'/'+district+'/'+district+'_BU_NBU_'+year+'.png')

print("Conversion Successful !!")

