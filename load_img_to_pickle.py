import cv2
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import random
import imutils
import math
#from PIL import Image
shuffle_flag = False
folder1 = r"data\test"
one_hot = [[1,0,0,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,1,0,0,0],[0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,0,1]]
ang = 180-45

def img_sc(img, img3):
    a,b = img.shape[0], img.shape[1]
    new = img
    new3 = img3
    for i in range(a):
        for j in range(b):
            if new[i][j] > 0:
                new[i][j] = 1
                new3[i][j] = np.ones(3)
    return new, new3

def zoom_img(img, ratio=0.9):
    #zoom in image
    Y_ax, X_ax = img.shape[0], img.shape[1]
    
    Y_compensate, X_compensate = math.floor(Y_ax * (1 - ratio) / 2), math.floor(X_ax * (1 - ratio) / 2)
    cropped_image = img[Y_compensate:Y_ax-Y_compensate, X_compensate:X_ax-X_compensate]
    return cropped_image

def image_process(img_path, resize_dim=(100,100), rotate_angle=205, zoom_flag=True):
    rotate_angle = random.randint(200, 210)
    img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    rotate_image = imutils.rotate_bound(img_gray, rotate_angle)
    (thresh, img_bw) = cv2.threshold(rotate_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    if zoom_flag:
        center_img = zoom_img(img_bw)
    else:
        center_img = img_bw
    img_resize = cv2.resize(center_img, resize_dim, interpolation = cv2.INTER_NEAREST)
    img= img_resize.astype('float32')/255.0
    img3 = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img, img3

def load_images_from_folder(folder):
    dim = (100,100)
    counter = 0
    images, img_3, label = [], [], []
    gesture_label_dict = {"0":[], "1":[], "2":[], "3":[], "4":[], "5":[], "6":[],
                            "7":[], "8":[], "9":[]}
    data_sep=[0,0,0,0,0,0,0,0,0,0]
    for subfolder in os.listdir(folder):
        # l = filename.split('.')[0][-1]
        #print(filename, l)
        if subfolder =="fist":
            new_folder = os.path.join(folder, subfolder)
            for filename in os.listdir(new_folder):
                img, img3 = image_process(os.path.join(new_folder,filename))
                if img is not None:
                    images.append(img)
                    img_3.append(img3)
                    label.append(one_hot[0])
                    data_sep[0]+=1
                    gesture_label_dict["0"].append(counter)
                    counter+=1

        elif subfolder =="thumbs":
            new_folder = os.path.join(folder, subfolder)
            for filename in os.listdir(new_folder):
                img, img3 = image_process(os.path.join(new_folder,filename))
                if img is not None:
                    images.append(img)
                    img_3.append(img3)
                    label.append(one_hot[2])
                    data_sep[2]+=1
                    gesture_label_dict["2"].append(counter)
                    counter+=1

        elif subfolder =="peace":
            new_folder = os.path.join(folder, subfolder)
            for filename in os.listdir(new_folder):
                img, img3 = image_process(os.path.join(new_folder,filename))
                if img is not None:
                    images.append(img)
                    img_3.append(img3)
                    label.append(one_hot[3])
                    data_sep[3]+=1
                    gesture_label_dict["3"].append(counter)
                    counter+=1

        elif subfolder =="five":
            new_folder = os.path.join(folder, subfolder)
            for filename in os.listdir(new_folder):
                img, img3 = image_process(os.path.join(new_folder,filename))
                if img is not None:
                    images.append(img)
                    img_3.append(img3)
                    label.append(one_hot[4])
                    data_sep[4]+=1
                    gesture_label_dict["4"].append(counter)
                    counter+=1

        elif subfolder =="rad":
            new_folder = os.path.join(folder, subfolder)
            for filename in os.listdir(new_folder):
                img, img3 = image_process(os.path.join(new_folder,filename))
                if img is not None:
                    images.append(img)
                    img_3.append(img3)
                    label.append(one_hot[7])
                    data_sep[7]+=1
                    gesture_label_dict["7"].append(counter)
                    counter+=1

    return np.array(images), np.array(label), np.array(img_3), data_sep, gesture_label_dict

im,la,im3,da, G_dict = load_images_from_folder(folder1)

if shuffle_flag:
    from sklearn.utils import shuffle
    im,im3,la= shuffle(im,im3,la)

print(im.shape, la.shape, im3.shape, da)

rind = random.randint(0, la.shape[0])
plt.imshow(im[rind], cmap="gray")
plt.show()
print(la[rind])



pickle_out = open(r"test_X_Sep_2022.pickle", "wb")
pickle.dump(im, pickle_out)
pickle_out.close()

pickle_out = open(r"test_X_3_Sep_2022.pickle", "wb")
pickle.dump(im3, pickle_out)
pickle_out.close()

pickle_out = open(r"test_Y_gesture_Sep_2022.pickle", "wb")
pickle.dump(la, pickle_out)
pickle_out.close()

pickle_out = open(r"test_gesture_label_dict_2022.pickle", "wb") # save image index
pickle.dump(G_dict, pickle_out, protocol=pickle.HIGHEST_PROTOCOL)
pickle_out.close()

"""
def visualize(image, prob, key):
    index = 0

    color = [(120, 20, 240), (240, 55, 210), (240, 55, 140), (240, 75, 55), (170, 240, 55)]
    for c, p in enumerate(prob):
        if p > 0.5:
            image = cv2.circle(image, (int(key[index]), int(key[index + 1])),
                               radius=5, color=color[c], thickness=-2)
        index = index + 2

    cv2.imshow("Press 'Esc' to CLOSE", image)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
    return


# train or valid
dataset = 'training_images'


#x = np.load(dataset + '/' + dataset + '_x.npy')


y_prob = np.load( dataset + '/' + '_y_prob.npy')


y_keys = np.load( dataset + '_y_keys.npy')

#print('images:', x.shape)
print('probabilistic labels:', y_prob.shape)
print('keypoints coordinates:', y_keys.shape)

 
total training samples: 25090
total validation samples: 1317

sample_number = 100

#x_sample = x[sample_number]
y_prob_sample = y_prob[sample_number]
y_keys_sample = y_keys[sample_number]

print("pro:", y_prob_sample)
print("key:", y_keys_sample)
"""