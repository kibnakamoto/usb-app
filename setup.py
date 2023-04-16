"""
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 8, 2023
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

        # add uf2 file
        shutil.copy("{self.add_path}/uf2.uf2", self.pico_path) # copy file to Downloads folder
        sleep(2.0) # wait for the uf2 file to be uploaded and microcontroller to reboot
        
        

    # disable hacking mode
    def disable_h(self) -> None:
        # remove the uploaded files from the microcontroller
        self.hack_mode = False


app = QApplication([])
w = Setup("/media/kibnakamoto/RPI-RP2")
w.show()
app.exec_()
