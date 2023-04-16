"""
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 16, 2023
"""

import os
import shutil
from time import sleep
from PyQt5.QtWidgets import QMainWindow, QApplication

# Setup the Microcontoller for hacking (hacking usb) or default mode (Normal MicroController)
class Setup(QMainWindow):
    """ Default Class Initializer """
    def __init__(self, pico_path):
        super().__init__()
        self.hack_mode = True
        self.path = os.path.dirname(os.path.realpath(__file__)) # get path of the application folder
        self.add_path = self.path + "/add_to_pico/"
        self.pico_path = pico_path
    
    # enable hacking mode
    def enable_h(self) -> None:
        # upload the files onto the microcontoller
        self.hack_mode = True

        # copy the uf2.uf2 file to the microcontroller and wait for it to reboot
        shutil.copy("{self.add_path}/uf2.uf2", self.pico_path) # copy file to pico
        sleep(2.0) # wait for the uf2 file to be uploaded and microcontroller to reboot

        # add all the lib files
        lib_files = os.listdir(f"{self.add_path}lib")
        for file in lib_files:
            shutil.copy(f"{self.add_path}{file}", self.pico_path+"/lib") # copy file to pico

        # add all the root files
        root_files = os.listdir(f"{self.add_path}root")
        for file in root_files:
            shutil.copy(f"{self.add_path}{file}", self.pico_path) # copy file to pico

    # disable hacking mode
    def disable_h(self) -> None:
        # remove the uploaded files from the microcontroller
        self.hack_mode = False
        

app = QApplication([])
w = Setup("/media/kibnakamoto/RPI-RP2")
w.show()
app.exec_()
