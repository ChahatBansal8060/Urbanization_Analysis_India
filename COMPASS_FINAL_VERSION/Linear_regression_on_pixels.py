import numpy as np
import pandas as pd
from pylab import *
from PIL import Image
from scipy import ndimage
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os, sys

districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
years = ['2016', '2017', '2018', '2019']

# defining required functions here
'''
This function is used to prepare district image for the application of smoothing filters. 
The background and builtup pixels are given value 0 and the non-built-up pixels are given value 1.
This is because the filters should perform smoothing over BU and NBU pixels only and not background.

Input:
a) original_image: The BU/NBU maps with background pixels having value 0, BU pixels having value 65, and NBU value 130 

Output:
a) prepped_image: The Background and BU pixels will have value 0 and NBU pixels will have value 1. 
'''
def Prepare_image_for_filters(original_image):
    prepped_image = original_image//130
    return prepped_image


'''
This function removes the background pixels from the 1D array of the smoothed image using original image.
A pixel is retained in the smoothed array only if it's value in original image is either 1 (for BU) or 2 (for NBU)
'''
def Remove_background_pixels(original_1D_image, smoothed_1D_image):    
    smooth_temp = [ smoothed_1D_image[i] for i in range(len(smoothed_1D_image)) if original_1D_image[i] > 0]
    return smooth_temp


'''
Driver code starts here
'''
for district in districts:
    print (district)
    year_to_pixel_matrix = [] # this matrix stores for each year the value of all pixels 
    
    for year in years:
        original_image = np.array( Image.open('BU_NBU_maps/'+district+'/'+district+'_BU_NBU_'+year+'.png') )
        prepped_image_for_filters = Prepare_image_for_filters(original_image)
    
        # Apply Convolution and gaussian filters over prepped image. All filter parameters are hyper-parameters
        
        kernel = np.array([[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]])
        smoothed_image = ndimage.convolve( prepped_image_for_filters, kernel, mode='constant', cval=0.0)
        smoothed_image = ndimage.gaussian_filter(smoothed_image, sigma=0.2, truncate=11.0, output=float) 
        
        # convert the 2D images into 1D arrays for further pixel-wise processing
        original_1D_image = original_image.flatten()
        smoothed_1D_image = smoothed_image.flatten()
        assert(len(original_1D_image) == len(smoothed_1D_image))
        
        smoothed_1D_image = Remove_background_pixels(original_1D_image, smoothed_1D_image)
        year_to_pixel_matrix.append(smoothed_1D_image) 
    
    # transpose is taken to store pixel values in rows against the years in columns
    pixel_to_year_matrix = np.array(year_to_pixel_matrix, copy=False).T

    # Applying linear regression on the values of each pixel over differen years i.e each row of pixel_to_year_matrix
    # For this, the boundary pixels of a district should be avoided as their smooth value is impacted by background pixels
        
    relabelled_original_image = original_image//65  # 0 for background, 1 for BU, and 2 for NBU
    dimensions = relabelled_original_image.shape
    
    background_vs_non_background_image = np.sign(relabelled_original_image) # using signum function, background pixels remain 0 and non-background become 1
    
    # using convolution filter, each non-boundary pixel inside the district will have value 9 in the mask
    boundary_identifying_kernel = np.array([[1,1,1],[1,1,1],[1,1,1]]) # this should be a 5x5 filter but we'll loose out on double boundary pixels 
    boundary_vs_non_boundary_mask = ndimage.convolve(background_vs_non_background_image, boundary_identifying_kernel, mode='constant', cval=0.0)
    
    current_pixel = 0  # refers to current pixel position we check for being boundary pixel or not
    
    # Define variables for applying linear regression 
    year_list_as_input = np.reshape(range(len(years)), (-1,1)) # matrix of type [[1],[2],...,[len(year)]], -1 refers to unspecified no. of rows here
    # following values are found corresponding to each pixel using its value in all years
    slope = []
    intercept = []
    cost_array = []
    
    for j in range(dimensions[0]):
        for k in range(dimensions[1]):
            if (background_vs_non_background_image[j][k]): # if pixel is inside the district
                if (boundary_vs_non_boundary_mask[j][k] == 9): # if pixel is not boundary pixel 
                    linear_model = LinearRegression() 
                    # we predict value of pixel for a given year and find best fit of linear regression on it 
                    # so year_list_as_input is our input variable for linear regression
                    regression = linear_model.fit(year_list_as_input, pixel_to_year_matrix[current_pixel])
                    cost = np.mean((pixel_to_year_matrix[current_pixel] - linear_model.predict(year_list_as_input))**2)
                    cost_array.append(cost)
                    slope.append(round(regression.coef_[0], 4)) #coef.shape is (1,1)
                    intercept.append(round(regression.intercept_, 4)) #intercept.shape is (1)
                current_pixel += 1
                
    cost_array = np.array(cost_array)
    print(cost_array)

    # Save the cost array
    os.makedirs('Cost_results_from_Regression/'+district, exist_ok = True)
    # multiply each cost value by 1000 to overcome data loss from storing small values
    np.savetxt('Cost_results_from_Regression/'+district+'/'+district+'_regression_cost_array.txt', cost_array*1000, fmt='%d')	

    # creating and saving CDFs against the cost values of pixels for each district
    unique_cost_values, cost_frequencies = np.unique(cost_array, return_counts=True)
    total_cost_values = (float) (cost_frequencies.sum())
    cost_frequencies = cost_frequencies/total_cost_values
    cdf = np.cumsum(cost_frequencies)
    plt.plot(unique_cost_values,cdf,label = 'data')
    # check if a CDF file already exists, since matplotlib doesn't overwrite, delete previous file
    if os.path.isfile('Cost_results_from_Regression/'+district+'/'+district+'_linear_regression_cdf'):
        os.remove('Cost_results_from_Regression/'+district+'/'+district+'_linear_regression_cdf')
    savefig('Cost_results_from_Regression/'+district+'/'+district+'_linear_regression_cdf')
    plt.clf()
                
                
print("Done")


