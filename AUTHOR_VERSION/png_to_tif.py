# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

from osgeo import gdal
import gdal, ogr, os, osr
import numpy as np
import sys
import numpy as np
from PIL import Image

'''
This function creates the tiff file from the png file
Inputs:
1) reference_tif_image_path: Complete path to the tif file of district which is used as a reference to gather lat/lon information
2) out_image_path: Complete path where the output tiff file will be stored
3) input_png_image_path: Complete path of the input png image
'''
def array2raster(reference_tif_image_path, out_image_path, input_png_image_path):
    png_array  = np.array(Image.open(input_png_image_path))
    tif_raster = gdal.Open(reference_tif_image_path)
    
    geotransform = tif_raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = tif_raster.RasterXSize
    rows = tif_raster.RasterYSize

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(out_image_path, cols, rows, 1, gdal.GDT_Int16)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(png_array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(tif_raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


'''
This function holds the driver code
'''
def main():
    # districts for which ground truth is available
    districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
    png_images_directory = "CBU_CNBU_Changing_Maps"
    
    output_directory = png_images_directory+'/tifs'
    os.makedirs(output_directory, exist_ok=True)

    for district in districts:
        #print("Processing ",district)    
        png_image_filepath = png_images_directory +'/'+district+"_CBU_CNBU_Changing.png"
        reference_tif_image_path = 'Reference_district_tiffiles/'+district+'.tif'
        
        out_image_path =  output_directory+'/'+district+"_CBU_CNBU_Changing.tif"   

        array2raster(reference_tif_image_path, out_image_path, png_image_filepath)
        
        # Validating the output tiff file
        tiffImage = np.asarray( Image.open(out_image_path) )
        input_image = np.asarray( Image.open(png_image_filepath) )
        # print("The unique labels in tiff image are: ", np.unique(tiffImage) )
        # print("The unique labels in png image are: ", np.unique(input_image) )
        # print("The shape of tiff image is: ", tiffImage.shape )
        print("Processed ",district)
    print("\n#### Check CBU_CNBU_Changing_Maps/tifs/ directory for output ####\n")


if __name__ == '__main__':
        main()    

  
