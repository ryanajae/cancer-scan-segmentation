from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import sys
#from database import DataBase
from kivy.uix.scrollview import ScrollView 
  
# Property that represents a string value 
from kivy.properties import StringProperty
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

scans_path = str(path) + '/LGG_Scans/'
print(scans_path)

def getStudy():
    players = os.listdir(scans_path)
    return players

def printMenu(options_list):
	concat_list = ""
	for i, player in enumerate(options_list):
		concat_list + ('{}. {}{}'.format(i+1, player,'\n'))
		print(concat_list)
	return concat_list
# studies = getStudy()
# studies.remove('.DS_Store')
# printMenu(studies)
class ScrollableLabel(ScrollView):
	text = StringProperty('')
class StartWindow(Screen):
    numScans = ObjectProperty(None)
    sortScans = ObjectProperty(None)
    searchScans = ObjectProperty(None)
    exitButton = ObjectProperty(None)
    listedScans = ObjectProperty(None)
    def ListAll(self):
    	studies = getStudy()
    	studies.remove('.DS_Store')
    	listText = printMenu(studies)
    	print(listText)
    	self.listedScans.text = listText
    def CloseProgram(self):
    	sys.exit()

kv = Builder.load_file("project_kivy.kv")

class WindowManager(ScreenManager):
    pass

sm = WindowManager()
#db = DataBase("users.txt")

screens = [StartWindow(name="start")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "start"



class MyMain(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMain().run()