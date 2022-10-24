import cv2
import numpy as np
import os
import pickle
from sklearn.utils import shuffle

file_name_x = "test_X_Sep_2022_only1000.pickle"
file_name_x_3 = "test_X_Sep_2022_only1000.pickle"
file_name_y_gest = "test_Y_gesture_Sep_2022_only1000.pickle"

data_pickle_path = "data_pickle\\data_only1000"
current_path = os.path.dirname(os.path.realpath(__file__))
pickle_path = os.path.abspath(os.path.join(current_path, data_pickle_path))


open_x = os.path.join(pickle_path, file_name_x)
with (open(open_x, "rb")) as openfile:
	while True:
		try:
			X_test = pickle.load(openfile)
		except EOFError:
			break

open_x_3 = os.path.join(pickle_path, file_name_x_3)
with (open(open_x_3, "rb")) as openfile:
	while True:
		try:
			X_3 = pickle.load(openfile)
		except EOFError:
			break

open_y = os.path.join(pickle_path, file_name_y_gest)
with (open(open_y, "rb")) as openfile:
	while True:
		try:
			Y_Gest = pickle.load(openfile)
		except EOFError:
			break

im,im3,la= shuffle(X_test, X_3, Y_Gest)
print(im.shape)


pickle_out = open(r"test_X_Sep_2022_only1000_shuffle.pickle", "wb")
pickle.dump(im, pickle_out)
pickle_out.close()

pickle_out = open(r"test_X_3_Sep_2022_only1000_shuffle.pickle", "wb")
pickle.dump(im3, pickle_out)
pickle_out.close()

pickle_out = open(r"test_Y_gesture_Sep_2022_only1000_shuffle.pickle", "wb")
pickle.dump(la, pickle_out)
pickle_out.close()



segment1 = im[0:100]
segment2 = im[100:200]
segment3 = im[200:300]
segment4 = im[300:400]
segment5 = im[400:500]
segment6 = im[500:600]
segment7 = im[600:700]
segment8 = im[700:800]
segment9 = im[800:900]
segment10 = im[900:1000]

pickle_out = open(r"segment1.pickle", "wb")
pickle.dump(segment1, pickle_out)
pickle_out.close()
pickle_out = open(r"segment2.pickle", "wb")
pickle.dump(segment2, pickle_out)
pickle_out.close()
pickle_out = open(r"segment3.pickle", "wb")
pickle.dump(segment3, pickle_out)
pickle_out.close()
pickle_out = open(r"segment4.pickle", "wb")
pickle.dump(segment4, pickle_out)
pickle_out.close()
pickle_out = open(r"segment5.pickle", "wb")
pickle.dump(segment5, pickle_out)
pickle_out.close()
pickle_out = open(r"segment6.pickle", "wb")
pickle.dump(segment6, pickle_out)
pickle_out.close()
pickle_out = open(r"segment7.pickle", "wb")
pickle.dump(segment7, pickle_out)
pickle_out.close()
pickle_out = open(r"segment8.pickle", "wb")
pickle.dump(segment8, pickle_out)
pickle_out.close()
pickle_out = open(r"segment9.pickle", "wb")
pickle.dump(segment9, pickle_out)
pickle_out.close()
pickle_out = open(r"segment10.pickle", "wb")
pickle.dump(segment10, pickle_out)
pickle_out.close()

print(segment1.shape, segment10.shape)