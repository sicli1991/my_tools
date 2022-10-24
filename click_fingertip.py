import os
import sys
import numpy as np
import struct
import keyboard
import matplotlib.pyplot as plt
import cv2
import multiprocessing
import time
import json 
import pickle
#from multiprocessing import Process, Value, Array
global globVar
globVar = []

folder_mo    = "data_pickle\\data_only1000" # output file dir for image readin only
read_pickle = True

def init_processes(gVar):
    global globVar
    globVar.append(gVar)

def click_event( result, img):
	cv2.namedWindow("main", cv2.WINDOW_NORMAL)
	cv2.resizeWindow("main", 300, 300)
	cv2.imshow("main", img)
	cv2.setMouseCallback("main", sub_click_event, result)
	while cv2.waitKey(0) != 32: pass    #13: enter, 27:esc, 32:space, delete:127

def sub_click_event(event, x, y, flags, params):
 
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates on the Shell
        #print(x, ' ', y)
        params.append((x,y))
        print(params)
        # displaying the coordinates
        # on the image window
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(img, '.', (x,y), font,
        #            1, (255, 0, 0), 2)
        #cv2.imshow('image', img)
    """
    if event == cv2.EVENT_RBUTTONDOWN:
    	print("None None")
    	params.append((9999,9999))
    """


def onkeypress(event):
	#global result
	if event.name == 'x':
		result.append((9999,9999))


def keyboard_event(result):
	while True:
		if keyboard.is_pressed('ctrl'):
			result.append((9999,9999))
			print(result)
			time.sleep(0.2)
		elif keyboard.is_pressed('Backspace'):		
			del result[-1]
			print("Delete, update as: ", result)
			time.sleep(0.2)
		elif keyboard.is_pressed('enter'):
			break
		elif keyboard.is_pressed('space'):
			break
	#keyboard.on_press(onkeypress)
	"""
	if array == ord('x'):
		for i in range(len(result)):
			result[i] = 9999
		#result.append((9999,9999))
		print(result)
	else:
		print("wrong key passed!!!!")
	"""


if __name__ == '__main__':
	# path_surf = os.getcwd()
	readin_file_name = sys.argv[1]
	path_surf = os.path.dirname(os.path.realpath(__file__))
	pickle_path = os.path.abspath(os.path.join(path_surf, readin_file_name))
	
	if read_pickle == True:
		with (open(pickle_path, "rb")) as openfile:
			while True:
				try:
					X = pickle.load(openfile)
				except EOFError:
					break
		for i in range(X.shape[0]):
			a1 = X[i]
			while True:
				manager = multiprocessing.Manager()
				shared_list = manager.list()
				
				p1 = multiprocessing.Process(target=click_event, args=[shared_list, a1])
				p2 = multiprocessing.Process(target=keyboard_event, args=[shared_list])
					
				p1.start()
				p2.start()
				p1.join()
				p2.join()
				print("#########################")
				print ("Final: ", shared_list)
				#cv2.waitKey(0)
				cv2.destroyAllWindows()
			
				if len(shared_list)!=7:
					print("None enough point selected")
					continue
				else:
					dir_store = os.path.join(path_surf, "fingertips")
					os.makedirs(dir_store, exist_ok=True)
					os.chdir(dir_store)
					new_name = readin_file_name.split(".")[0] + "_#" + str(i) + ".txt"
					with open(new_name, 'w') as f:
						f.write(str(shared_list))
					break	

	else:				
		dir_files = os.path.join(folder_mo, "data")	
		files = os.listdir(dir_files)

		for file in files:
			print("read in: ", file)
			file_P = os.path.join(dir_files, file)
			a1 = cv2.imread(file_P, cv2.IMREAD_GRAYSCALE) #image read in

			while True:
				manager = multiprocessing.Manager()
				shared_list = manager.list()
				
				p1 = multiprocessing.Process(target=click_event, args=[shared_list, a1])
				p2 = multiprocessing.Process(target=keyboard_event, args=[shared_list])
					
				p1.start()
				p2.start()
				p1.join()
				p2.join()
				print("#########################")
				print ("Final: ", shared_list)
				#cv2.waitKey(0)
				cv2.destroyAllWindows()
			
				if len(shared_list)!=7:
					print("None enough point selected")
					continue
				else:
					dir_store = os.path.join(folder_mo, "label")
					os.makedirs(dir_store, exist_ok=True)
					os.chdir(dir_store)
					new_name = file.split(".")[0] + ".txt"
					with open(new_name, 'w') as f:
						f.write(str(shared_list))
					break
				