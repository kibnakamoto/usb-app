import ducky

# raise error when language is not supported
class LanguageNotFoundError(ModuleNotFoundError):
    pass

LANGUAGES_MAC = ("us", "fr")
LANGUAGES_WIN = ('us', 'cz', 'cz1', 'da', 'de', 'es', 'fr', 'hu', 'it', 'po', 'sw', 'tr', 'uk', 'br')

try:
    with open("choices", "r") as f:
        class Target:
            def __init__(self):
                TARGET = f.read().split("|")
                self.OS = TARGET[0]
                self.LANG = TARGET[1]
except FileNotFoundError:
    print("no choices selected\ndefault OS: \"win\"\ndefault LANGUAGE: \"us\"")
    class Target:
        def __init__(self):
            self.OS = "win"
            self.LANG = "us"
TARGET = Target()

def set_lang(target_os:str, keyboard_lang:str) -> None:
    if target_os == "mac":
        if keyboard_lang == "fr":
           from keyboard_layout_mac_fr import KeyboardLayout
           from keycode_mac_fr import Keycode
        elif keyboard_lang == "us":
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
            from adafruit_hid.keycode import Keycode
        else:
            raise LanguageNotFoundError("No other languages supported for mac")
    elif target_os == "windows":
        if keyboard_lang == "uk":
           from keyboard_layout_win_uk import KeyboardLayout
           from keycode_win_uk import Keycode
        elif keyboard_lang == "us":
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
            from adafruit_hid.keycode import Keycode
        elif keyboard_lang == "br":
            from keyboard_layout_win_br import KeyboardLayout
            from keycode_win_br import Keycode
        elif keyboard_lang == "cz":
            from keyboard_layout_win_cz import KeyboardLayout
            from keycode_win_cz import Keycode
        elif keyboard_lang == "cz1":
            from keyboard_layout_win_cz1 import KeyboardLayout
            from keycode_win_cz1 import Keycode
        elif keyboard_lang == "da":
            from keyboard_layout_win_da import KeyboardLayout
            from keycode_win_da import Keycode
        elif keyboard_lang == "de":
            from keyboard_layout_win_de import KeyboardLayout
            from keycode_win_de import Keycode
        elif keyboard_lang == "es":
            from keyboard_layout_win_es import KeyboardLayout
            from keycode_win_es import Keycode
        elif keyboard_lang == "fr":
            from keyboard_layout_win_fr import KeyboardLayout
            from keycode_win_fr import Keycode
        elif keyboard_lang == "hu":
            from keyboard_layout_win_hu import KeyboardLayout
            from keycode_win_hu import Keycode
        elif keyboard_lang == "it":
            from keyboard_layout_win_it import KeyboardLayout
            from keycode_win_it import Keycode
        elif keyboard_lang == "po":
            from keyboard_layout_win_po import KeyboardLayout
            from keycode_win_po import Keycode
        elif keyboard_lang == "sw":
            from keyboard_layout_win_sw import KeyboardLayout
            from keycode_win_sw import Keycode
        elif keyboard_lang == "tr":
            from keyboard_layout_win_tr import KeyboardLayout
            from keycode_win_tr import Keycode
        else:
            raise LanguageNotFoundError("No other languages supported for windows")
    else: # unix/linux not supported
        raise OSError("operating system not supported")
    
