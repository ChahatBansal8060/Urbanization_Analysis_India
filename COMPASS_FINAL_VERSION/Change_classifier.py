import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os, sys

'''
This function calculates the threshold for the cost value which determines if a pixel is constant (BU/NBU) or changing
Input:
a) distict: name of the district under analysis (string)
b) cost_array: list of cost (mean squared error) against the linear regression applied on each pixel 
'''
def calculate_thresholds(district, cost_array):    
    unique_cost_values, cost_frequencies = np.unique(cost_array, return_counts=True)
    total_cost_values = (float)(cost_frequencies.sum())
    cost_probabilities = cost_frequencies/total_cost_values
    cdf = np.cumsum(cost_probabilities) # calculate cumulative sum

    # draw a smooth spline over the cost values (x) and their cdf values (y)
    y_spline = UnivariateSpline(unique_cost_values, cdf, s=0, k=1)
    x_range = np.linspace(unique_cost_values[0], unique_cost_values[-1], 100)

    # Applying convolution filter for a smooth curve
    kernel_size = 5
    kernel = [1/kernel_size]*(kernel_size) # this is a list of [1/5, 1/5..., 1/5] 5 times
    smooth_spline = np.convolve(y_spline(x_range), kernel, 'same')

    # removing last 20 points and using only first 80 points because threshold is expected to be found in the very beginning
    smooth_spline = smooth_spline[:80]
    x_range = x_range[:80]

    # plot the spline points
    plt.figure()
    plt.plot(unique_cost_values, cdf, 'ro', label='data')
    plt.plot(x_range, smooth_spline)
    plt.title(district+': smooth spline over CDF')
    # plt.show()

    # finding threshold value using 1st and 2nd derivative 

    # 1st derivative
    dy = np.diff(smooth_spline, 1)	#storing subtractions of each point with previous point
    dx = np.diff(x_range,1)
    y_first_derivative = dy/dx			#finding first derivative curve
    middle_x_first_derivative = 0.5 * (x_range[:-1] + x_range[1:]) #finding middle point where the derivative is calculated
    
    # 2nd derivative
    dy_first_derivative = np.diff(y_first_derivative,1)
    dx_first_derivative = np.diff(middle_x_first_derivative,1)
    y_second_derivative = dy_first_derivative / dx_first_derivative
    middle_x_second_derivative = 0.5*(middle_x_first_derivative[:-1] + middle_x_first_derivative[1:])
    
    # plotting the 2nd derivative curve to find the threshold point
    plt.figure()
    plt.plot(middle_x_first_derivative, y_first_derivative)
    plt.title(district+': 1st derivative')
    # plt.show()

    plt.figure()
    plt.plot(middle_x_second_derivative, y_second_derivative)
    plt.title(district+': 2nd derivative')
    # plt.show()

    # find minima for the second derivative plot
    minima_index = np.argmin(y_second_derivative)
    threshold = 2 + x_range[minima_index]	# adding 2 to the point of minima is experimental
    
    return threshold
    
   

'''
Driver code starts here
'''
districts = ['Bangalore', 'Chennai', 'Delhi', 'Gurgaon', 'Hyderabad', 'Kolkata', 'Mumbai']
years = ['2016', '2017', '2018', '2019']
for district in districts:
    print(district)
    main_folder = 'Cost_results_from_Regression/'+district
    cost_array = np.loadtxt(main_folder+'/'+district+'_regression_cost_array.txt')
    
    #divide cost array by 1000 because we multiplied 1000 during storage of file
    cost_array = cost_array/1000  
    
    threshold = calculate_thresholds(district, cost_array)
    print('threshold for ',district,' is: ',threshold)
    
    district_image_base_year = np.array(Image.open('BU_NBU_maps/'+district+'/'+district+'_BU_NBU_'+years[0]+'.png'))
    # bring images to label 0 for background pixels, 1 for BU, and 2 for NBU
    district_image_base_year = district_image_base_year//65
    image_dimensions = district_image_base_year.shape

    background_vs_non_background_image = np.sign(district_image_base_year)
    boundary_identifying_kernel = np.array([[1,1,1],[1,1,1],[1,1,1]]) 
    boundary_vs_non_boundary_mask = ndimage.convolve(background_vs_non_background_image, boundary_identifying_kernel, mode='constant', cval=0.0)

    '''
    For creating the CBU/CNBU/Changing maps, 
    we assign label 0 to background pixels
    label 65 (1x65) to CBU pixels
    label 130 (2x65) to CNBU pixels, and
    label 195 (3x65) to Changing pixels
    '''
    current_pixel = 0
    CBU_pixel_count = 0
    CNBU_pixel_count = 0
    Changing_pixel_count = 0
    CBU_CNBU_Changing_map = district_image_base_year 

    for j in range(image_dimensions[0]):
        for k in range(image_dimensions[1]):
            if (boundary_vs_non_boundary_mask[j][k] == 9):
                if (cost_array[current_pixel] <= threshold):
                    if (district_image_base_year[j][k] == 1):
                        CBU_CNBU_Changing_map[j][k] = 65
                        CBU_pixel_count += 1
                    else:
                        CBU_CNBU_Changing_map[j][k] = 130
                        CNBU_pixel_count += 1
                
                else:
                    CBU_CNBU_Changing_map[j][k] = 195
                    Changing_pixel_count += 1
                current_pixel += 1
            else:
                CBU_CNBU_Changing_map[j][k] = 0

    # save the CBU_CNBU_Changing map
    os.makedirs("CBU_CNBU_Changing_Maps", exist_ok=True)
    CBU_CNBU_Changing_map = ( Image.fromarray(CBU_CNBU_Changing_map) ).convert("L")
    CBU_CNBU_Changing_map.save('CBU_CNBU_Changing_Maps/'+district+'_CBU_CNBU_Changing.png')

    total_pixels = CBU_pixel_count + CNBU_pixel_count + Changing_pixel_count
    print("Percentage of CBU pixels: ", (CBU_pixel_count*100)/total_pixels,'%')
    print("Percentage of CNBU pixels: ", (CNBU_pixel_count*100)/total_pixels,'%')
    print("Percentage of Changing pixels: ", (Changing_pixel_count*100)/total_pixels,'%')
    
