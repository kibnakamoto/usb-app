"""
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 8, 2023
"""

from PyQt5.QtWidgets import QMainWindow, QApplication

# Setup the Microcontoller for hacking (hacking usb) or default mode (Normal MicroController)
class Setup(QMainWindow):
    """ Default Class Initializer """
    def __init__(self):
        super().__init__()
        self.hack_mode = True
    
    # enable hacking mode
    def enable_h(self) -> None:
        self.hack_mode = True

        # upload the files onto the microcontoller
        # TODO: ^

    # disable hacking mode
    def disable_h(self) -> None:
        pass


app = QApplication([])
w = Setup()
w.show()
app.exec_()
