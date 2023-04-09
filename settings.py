"""
Settings Module for settings.json
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 6, 2023
"""

import json
from PyQt5.QtWidgets import QMessageBox

from misc.misc import rgbtohex

# read settings json
class Settings:
    """ Default Class Initializer """
    def __init__(self):
        with open("settings.json", "r") as f:
            self.settings = json.load(f)
        self.cf = self.settings["current file"]
        self.theme = self.settings["last color"]
        self.all_themes = list(self.settings["colors"][0].keys()) # name of all themes

    # select theme (has to be already existing)
    def set_theme(self, name:str=None) -> None:
        if name:
            self.theme = name
        self.set_colors()

    # create new theme
    def create_theme(self, bg:str, comment:str, starting_keywords:str, fkeys:str, shortcuts:str, arrows:str,
                     windows:str, chars:str, uncommon:str, numbers:str, text:str, textbubble:str,
                     bg_sidebar:str, color_sidebar:str, name:str=None) -> None:
        if name:
            self.theme = name

        properties = [
           {
                "background": bg,
                "comment": comment,
                "starting keywords": starting_keywords,
                "fkeys": fkeys,
                "shortcut keys": shortcuts,
                "arrows": arrows,
                "windows": windows,
                "chars": chars,
                "uncommon": uncommon,
                "numbers": numbers,
                "text": text,
                "textbubble": textbubble,
           	    "background sidebar": bg_sidebar,
                "color sidebar": color_sidebar
           }
        ]

        # if values rgb
        for k,v in properties[0].items():
            if not isinstance(properties[0][k], str):
                properties[0][k] = rgbtohex(v)

        # check if theme exists
        if not self.theme in self.settings["colors"][0].keys():
            self.settings["colors"][0][self.theme] = properties
            self.set_colors()
        else: # if it doesn't exists
            if properties != self.settings["colors"][0][self.theme]: # if settings don't have the new properties
                __exit = QMessageBox.question(None, 'Theme Creator', "The selected theme exists\nWould you like to ovveride it?", QMessageBox.No|QMessageBox.Yes)
                if __exit == QMessageBox.Yes:
                    self.settings["colors"][0][self.theme] = properties
                    self.set_colors()
                else:
                    theme = len(self.settings["colors"][0])-2 # if theme exists add number to differ from original theme
                    self.settings["colors"][0][self.theme+f"{theme}"] = properties
                    self.set_colors()

    # set property class members of a theme
    def set_colors(self) -> None:
        self.bg = self.settings["colors"][0][self.theme][0]["background"]
        self.comment = self.settings["colors"][0][self.theme][0]["comment"]
        self.starting_keywords = self.settings["colors"][0][self.theme][0]["starting keywords"]
        self.fkeys = self.settings["colors"][0][self.theme][0]["fkeys"]
        self.shortcuts = self.settings["colors"][0][self.theme][0]["shortcut keys"]
        self.arrows = self.settings["colors"][0][self.theme][0]["arrows"]
        self.windows = self.settings["colors"][0][self.theme][0]["windows"]
        self.chars = self.settings["colors"][0][self.theme][0]["chars"]
        self.uncommon = self.settings["colors"][0][self.theme][0]["uncommon"]
        self.numbers = self.settings["colors"][0][self.theme][0]["numbers"]
        self.text = self.settings["colors"][0][self.theme][0]["text"]
        self.textbubble = self.settings["colors"][0][self.theme][0]["textbubble"]
        self.bg_sidebar = self.settings["colors"][0][self.theme][0]["background sidebar"]
        self.color_sidebar = self.settings["colors"][0][self.theme][0]["color sidebar"]

    def save(self, settings:dict=None) -> None:
        if settings:
            self.settings = settings
            self.settings['current file'] = self.cf
        else:
            self.settings["colors"][0][self.theme][0]["background"] = self.bg
            self.settings["colors"][0][self.theme][0]["comment"] = self.comment
            self.settings["colors"][0][self.theme][0]["starting keywords"] = self.starting_keywords
            self.settings["colors"][0][self.theme][0]["fkeys"] = self.fkeys
            self.settings["colors"][0][self.theme][0]["shortcut keys"] = self.shortcuts
            self.settings["colors"][0][self.theme][0]["arrows"] = self.arrows
            self.settings["colors"][0][self.theme][0]["windows"] = self.windows
            self.settings["colors"][0][self.theme][0]["chars"] = self.chars
            self.settings["colors"][0][self.theme][0]["uncommon"] = self.uncommon
            self.settings["colors"][0][self.theme][0]["numbers"] = self.numbers
            self.settings["colors"][0][self.theme][0]["text"] = self.text
            self.settings["colors"][0][self.theme][0]["textbubble"] = self.textbubble
            self.settings["colors"][0][self.theme][0]["background sidebar"] = self.bg_sidebar
            self.settings["colors"][0][self.theme][0]["color sidebar"] = self.color_sidebar
            self.settings["current file"] = self.cf
            self.settings["last color"] = self.theme
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4) # upload modified settings into settings.json
