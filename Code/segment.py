import os
import sys
import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt
import os
import skimage
from skimage.segmentation import clear_border
import os
from pathlib import Path

path = Path(os.getcwd())

threshold = 0.25

scans_path = str(path.parent) + '/LGG_Scans/'
print (scans_path)

def getStudy():
    players = os.listdir(scans_path)
    return players

def normalizeSlice(slice_arr):
    norm_arr = np.float32(slice_arr) / np.float32(np.max(slice_arr))
    return norm_arr

def convertToHU(rawimg):
    RS = ds.RescaleSlope
    RI = ds.RescaleIntercept
    HU_img = rawimg*RS + np.ones((ds.Rows,ds.Columns))*RI
    return HU_img

def printMenu(options_list):
    print ("Scans Menu\n\n")
    print ("Enter a number to view that scan: ")
    for i, player in enumerate(options_list):
        print ('{}. {}'.format(i+1, player))
    print ("Enter a letter to perform one of the following operations.") 
    print ("A. Sort Scans")
    print ("B. Search Scans")
    print ("C. Exit")
    response = input()

    if response == 'C' or response == 'c':
        return 0

    elif response == 'A' or response == 'a':
        return printMenu(sorted(options_list))

    elif response == 'B' or response == 'b':
        search_str = input("Enter a search string: ")
        new_options = [elem for elem in options_list if search_str in elem]
        return printMenu(new_options)

    choice = options_list[int(response)-1]
    print (choice)

    return choice

def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)

def multi_slice_viewer(volume):
    remove_keymap_conflicts({'j', 'k'})
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = len(volume)-1
    ax.imshow(volume[ax.index], cmap='viridis')
    fig.canvas.mpl_connect('key_press_event', process_key)

def process_key(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    if event.key == 'j':
        previous_slice(ax)
    elif event.key == 'k':
        next_slice(ax)
    fig.canvas.draw()

def previous_slice(ax):
    volume = ax.volume
    ax.index = (ax.index - 1) % len(volume)
    ax.images[0].set_array(volume[ax.index])

def next_slice(ax):
    volume = ax.volume
    ax.index = (ax.index + 1) % len(volume)
    ax.images[0].set_array(volume[ax.index])

def study2volume(study_path):
    slice_proxy_list = []
    slice_map = {}
    volumes = []

    slice_paths = os.listdir(study_path)

    for s in slice_paths:
        slice_path = os.path.join(study_path,s)
        ds=dicom.read_file(slice_path)
        slice_proxy_list.append(ds.SliceLocation)
        slice_map[ds.SliceLocation] = s
        slice_proxy_list.sort()
    
    for i in range(len(slice_proxy_list)):
        slice_proxy = slice_proxy_list[-i]
        slice_path = os.path.join(study_path,slice_map[slice_proxy])
        ds=dicom.read_file(slice_path)
        rawimg = ds.pixel_array
        volumes.append(np.array(rawimg))
    
    volumes_arr = np.array(volumes)
    
    normed_slices = []

    for slice_arr in volumes_arr:
        normed = normalizeSlice(slice_arr)
        normed_slices.append(normed)

    return np.array(normed_slices)

def applyThreshold(slice_):
    thresh = threshold
    g_indices = slice_ < thresh
    l_indices = slice_ >= thresh
    slice_[g_indices] = 1
    slice_[l_indices] = 0
    return slice_

def isolateTumor(slice_):
    slice_ = applyThreshold(slice_)
    slice_ = slice_
    label_image = skimage.measure.label(clear_border(slice_))
    clear_image = label_image
    g_indices = clear_image >= 1
    l_indices = clear_image < 1
    clear_image[g_indices] = 1
    clear_image[l_indices] = 0
    return clear_image

def studyMenu():
    loop = True
    studies = getStudy()
    studies.remove('.DS_Store')
    while loop:
        study = printMenu(studies)
        if study == 0:
            loop = False
        else:
            # Manage showing the dicom files
            volume = study2volume(scans_path + study + '/')
            print (volume.shape)
            thresh = input("Would you like to apply a threshold filter to isolate a tumor? (y/n) ")
            if thresh == 'y' or thresh == 'Y':
                custom = input("A custom threshold? (y/n) ")
                if custom == 'y' or custom == 'Y':
                    threshold = float(input("New threshold: "))
                    tumor_isolated = []
                    for s in volume:
                        isolated = isolateTumor(s)
                        tumor_isolated.append(isolated)
                    volume = tumor_isolated
            crop = input("Would you like to apply a crop? (y/n) ")
            if crop == 'y' or crop == 'Y':
                slide_crop = input("Would you like to narrow the slides? (y/n) ")
                if slide_crop == 'y' or slide_crop == 'Y':
                    start_slide = input("Starting slide: ")
                    end_slide = input("Ending slide: ")
                    volume = volume[start_slide:end_slide]
                img_crop = input("Would you like to narrow the X and Y coordinates? (y/n) ")
                if img_crop == 'y' or img_crop == 'Y':
                    start_x = int(input("Starting X: "))
                    end_x = int(input("Ending X: "))
                    start_y = int(input("Starting Y: "))
                    end_y = int(input("Ending Y: "))
                    volume = volume[:, start_y:end_y, start_x:end_x]
                    print (volume)
            multi_slice_viewer(volume)
            plt.show()
    return

    print(studies)


def main():
    studyMenu()
    return

main()