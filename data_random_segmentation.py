import cv2
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import random
import imutils

# data segmentaion: random pickle 200 sample from each gesture
avaliable_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
choose_number = 200

with (open(r"test_gesture_label_dict_2022.pickle", "rb")) as openfile:
	while True:
		try:
			G_dict = pickle.load(openfile)
		except EOFError:
			break

with (open(r"test_X_Sep_2022.pickle", "rb")) as openfile:
	while True:
		try:
			X = pickle.load(openfile)
		except EOFError:
			break

with (open(r"test_X_3_Sep_2022.pickle", "rb")) as openfile:
	while True:
		try:
			X_3 = pickle.load(openfile)
		except EOFError:
			break

with (open(r"test_Y_gesture_Sep_2022.pickle", "rb")) as openfile:
	while True:
		try:
			Y_gest = pickle.load(openfile)
		except EOFError:
			break

X_project200 = np.empty([0,100,100])
X3_project200=np.empty([0,100,100,3])
Y_gest_project200=np.empty([0,10])

# iterate dic 找那些非empty的 ####################################################################
for key, value in G_dict.items():
	if value:
		print(len(value))
		random.shuffle(value)
		G_candidate = value[:200]
		X_project200  = np.vstack([X_project200, X[G_candidate]])
		X3_project200 = np.vstack([X3_project200, X_3[G_candidate]])
		Y_gest_project200 = np.vstack([Y_gest_project200, Y_gest[G_candidate]])

# X_project200 = np.array(X_project200)
# X3_project200 = np.array(X3_project200)
# Y_gest_project200 = np.array(Y_gest_project200)

print(X_project200.shape)
print(X3_project200.shape)
print(Y_gest_project200.shape)


pickle_out = open(r"test_X_Sep_2022_only1000.pickle", "wb")
pickle.dump(X_project200, pickle_out)
pickle_out.close()

pickle_out = open(r"test_X_3_Sep_2022_only1000.pickle", "wb")
pickle.dump(X3_project200, pickle_out)
pickle_out.close()

pickle_out = open(r"test_Y_gesture_Sep_2022_only1000.pickle", "wb")
pickle.dump(Y_gest_project200, pickle_out)
pickle_out.close()
