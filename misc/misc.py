"""
miscallanious indipendant functions
Author: Taha Canturk
Github: Kibnakamoto
Date: Apr 16, 2023
"""

# RGB to hex, accepts either one RGB tuple or r,g,b as seperate parameters
def rgbtohex(r:tuple, g:int=None,b:int=None) -> str:
    value = 0
    if isinstance(r, int):
        value<<=8
        value|=r
        value<<=8
        value|=g
        value<<=8
        value|=b
    else:
        for i in r:
            value<<=8
            value|=i
    return hex(value)[2:].zfill(6)

# hex to RGB, accepts string value starting with # or not
def hextorgb(h:str) -> tuple:
    if h[0] == '#':
        value = h[1:]
    else:
        value = h
    rgb = (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))
    return rgb

