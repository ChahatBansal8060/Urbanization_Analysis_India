# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

import json
import rasterio
from rasterio.mask import mask
from json import loads
import os
from os import listdir
import kml2geojson

print("******** Cutting Predicted Tiffiles into smaller shapes according to groundtruth***********")
'''
The ground truth is manually created for 4 districts for the year 2018
'''
districts = ['Bangalore', 'Chennai', 'Delhi', 'Mumbai']

for district in districts:
    # print(district)
    
    folder_containing_tifffiles = "CBU_CNBU_Changing_Maps/tifs"
    tiff_file_name = district+'_CBU_CNBU_Changing.tif'
    
    folder_containing_groundtruth_shapefiles = 'CBU_CNBU_Changing_Groundtruth/'+district
    
    for shapefile in listdir(folder_containing_groundtruth_shapefiles):
        if shapefile[-3:] == 'kml':
            kml2geojson.main.convert(folder_containing_groundtruth_shapefiles+'/'+shapefile, folder_containing_groundtruth_shapefiles)
            
            json_filepath = folder_containing_groundtruth_shapefiles+'/'+shapefile[:-3]+'geojson'
            json_data = json.loads( open(json_filepath).read() )
            
            output_directory = 'Trimmed_tiffiles/'+district+'/'+shapefile[:-4]
            os.makedirs(output_directory, exist_ok=True)
            
            i = 0            
            for currFeature in json_data["features"]:
                i += 1
                try:
                    geoms = [currFeature["geometry"]]

                    with rasterio.open(folder_containing_tifffiles+'/'+tiff_file_name) as src:
                        out_image, out_transform = mask(src, geoms, crop = True)
                        out_meta = src.meta

                        # save the resulting raster
                        out_meta.update({ "driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

                        saveFileName = output_directory+"/"+str(i)+".tif"
                        with rasterio.open(saveFileName, "w", **out_meta) as dest:
                            dest.write(out_image)
                except:
                    continue
                           
print('done\n')    





