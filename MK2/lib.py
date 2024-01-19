#!/usr/bin/env python
# coding: utf-8


import cv2
import tkinter
import os

# get screen dimensions
root = tkinter.Tk()
displayDimensions = (root.winfo_screenwidth(),root.winfo_screenheight())
root.destroy()

class IO:
    @staticmethod
    def openWithCV2(path):
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        resizedImage = cv2.resize(image, displayDimensions)

        _, threshold = cv2.threshold(resizedImage, 110, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            approx = cv2.approxPolyDP(c, 1, True)
            n = approx.ravel()
        return n

    @staticmethod
    def openJson(path):
        pass

    @staticmethod
    def pathFiddler(
        dir: list,
    ):  # this function takes the current working directory of the file and adds the specified folders and file to it,
        temp = ""  # then modifies the resulting string to double any slashes or backslashes, so that string interpretation is correct
        result = ""
        for element in dir:
            temp = os.path.join(temp, element)
        for n in os.path.join(os.getcwd(), temp):
            if n == ("\\" or "/"):
                result += n
            result += n
        return result