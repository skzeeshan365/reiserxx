import urllib.request
import string
import numpy as np
from PIL import Image
import cv2
from django.shortcuts import redirect

width = 50
height = 0
newwidth = 0
arr = string.ascii_letters
arr = arr + string.digits + "+,.-? "
letss = "image"


def getimg(case, col):
    global width, height, back
    try:
        url = "https://raw.githubusercontent.com/Ankit404butfound/HomeworkMachine/master/Image/%s.png" % case
        imglink = urllib.request.urlopen(url)
    except:
        url = "https://raw.githubusercontent.com/Ankit404butfound/HomeworkMachine/master/Image/%s.PNG" % case
        imglink = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imglink.read()))
    img = cv2.imdecode(imgNp, -1)
    cv2.imwrite(r"static/images/%s.png" % case, img)
    img = cv2.imread(r"static/images/%s.png" % case)
    img[np.where((img != [255, 255, 255]).all(axis=2))] = col
    cv2.imwrite("static/images/chr.png", img)
    cases = Image.open(r"static/images/chr.png")
    back.paste(cases, (width, height))
    newwidth = cases.width
    width = width + newwidth


def text_to_handwriting(string, rgb=[0, 0, 138]):
    """Convert the texts passed into handwritten characters"""
    save_path = letss

    global arr, width, height, back
    # rgb.reverse() not working, IDK why.
    try:
        back = Image.open(r"static/images/zback.png")
    except:
        url = "https://raw.githubusercontent.com/Ankit404butfound/HomeworkMachine/master/Image/zback.png"
        imglink = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imglink.read()))
        img = cv2.imdecode(imgNp, -1)
        cv2.imwrite(r"static/images/zback.png", img)
        back = Image.open(r"static/images/zback.png")
    rgb = [rgb[2], rgb[1], rgb[0]]
    count = -1
    lst = string.split()
    for letter in string:
        if width + 150 >= back.width or ord(letter) == 10:
            height = height + 227
            width = 50
        if letter in arr:
            if letter == " ":
                count += 1
                letter = "zspace"
                wrdlen = len(lst[count + 1])
                if wrdlen * 110 >= back.width - width:
                    width = 50
                    height = height + 227

            elif letter.isupper():
                letter = "c" + letter.lower()
            elif letter == ",":
                letter = "coma"
            elif letter == ".":
                letter = "fs"
            elif letter == "?":
                letter = "que"

            getimg(letter, rgb)

    # back.show()
    back.save(f"static/images/{save_path}.png")
    back.close()
    back = Image.open(r"static/images/zback.png")
    # rgb = [0,0,138]
    width = 50
    height = 0
    newwidth = 0
    return save_path


def api(rgb, text):
    if rgb:
        path = text_to_handwriting(str(text), str(rgb).split(","))
    else:
        path = text_to_handwriting(str(text))
    return redirect(f"http://reiserx.com/{path}.png")


def api(text):
    path = text_to_handwriting(str(text))
    return redirect(f"http://reiserx.com/{path}.png")