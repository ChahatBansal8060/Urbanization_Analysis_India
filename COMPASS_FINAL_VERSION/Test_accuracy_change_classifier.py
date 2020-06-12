from PIL import Image
from scipy import misc
from scipy import ndimage
import numpy as np
import pandas as pd
import unittest
import math
from sklearn.metrics import classification_report

predicted_CBU_CNBU_Changing_map = np.array(Image.open("CBU_CNBU_Changing_Maps/Gurgaon_CBU_CNBU_Changing.png"))
# bringing background, CBU, CNBU, and changing labels to 0, 1, 2, 3 respectively
predicted_CBU_CNBU_Changing_map = predicted_CBU_CNBU_Changing_map//65
number_of_columns, number_of_rows = predicted_CBU_CNBU_Changing_map.shape

# convert image to list to access labels as integers
predicted_CBU_CNBU_Changing_map = predicted_CBU_CNBU_Changing_map.tolist()

groundtruth_dataframe = pd.read_csv("change_classifier_groundtruth_gurgaon.csv")

record_numbers = groundtruth_dataframe['record_number'].values
row_indices = groundtruth_dataframe['row_index'].values
column_indices = groundtruth_dataframe['column_index'].values
pixel_longitudes = groundtruth_dataframe['longitude'].values
pixel_latitudes = groundtruth_dataframe['latitude'].values
class_labels = groundtruth_dataframe['class_label'].values

# defining minimum and maximum values of latitudes and longitudes for Gurgaon
lat_min = 76.63648223876953
lat_max = 77.23221588134766
long_min = 28.204980850219727
long_max = 28.54277992248535

xd = (lat_max - lat_min) / number_of_rows
yd = (long_max - long_min)/ number_of_columns

# List of predicted labels against the groundtruth pixels
y_predicted = []

for i in range(len(record_numbers)):
	row_index = row_indices[i]
	column_index = column_indices[i]
	longitude = pixel_longitudes[i]
	latitude = pixel_latitudes[i]
	
	y_predicted.append(predicted_CBU_CNBU_Changing_map[row_index][column_index])
	# assertions.assertAlmostEqual(longitude, (column_index * xd) + lat_min, 8, "longitude doesn't match: "+str(record_numbers[i]))
	# assertions.assertAlmostEqual(latitude, long_max - (row_index * yd), 8, "latitude doesn't match: "+str(record_numbers[i]))

print(classification_report(class_labels, y_predicted))



