from PIL import Image
from scipy import misc
from scipy import ndimage
import numpy as np
import pandas as pd
import unittest
import os, sys

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
    print (district)
    
    #read all images to be compressed
    dataset = [ np.array( Image.open( 'Landcover_Predictions_Using_IndiaSat/'+district+'/'+district+'_prediction_'+year+'.png')) for year in years] 	
    image_dimensions = dataset[0].shape

    for i in range( image_dimensions[0] ):
        for j in range( image_dimensions[1] ):
            for k in range(len(dataset)):
                # keep background pixels unchanged
                if ( dataset[k][i][j] == 0 ):
                    continue
                # keep green, water, and barrenland pixels as non-built-up i.e. NBU with color code (2 x 65)
                if ( dataset[k][i][j] in [Green, Water, Barrenland] ):
                    dataset[k][i][j] = 130
                # keep built-up pixels as it is i.e. BU with color code (1 * 65)
                else:
                    dataset[k][i][j] = 65

    for k in range(len(years)):
            # create a folder against this district 
            os.makedirs( destination_directory+'/'+district, exist_ok = True )

            dataset[k] = Image.fromarray(dataset[k])
            dataset[k].save(destination_directory+'/'+district+'/'+district+'_BU_NBU_'+years[k]+'.png')

	  



