#!/usr/bin/env python
# coding: utf-8
import os, pygame, sys


def read(path):
    pass

def write(path):
    try:
        if os.path.exists(path):
            str(input("file exists, take"))
            

def file_fiddler():
    pass


class Render:
    @staticmethod
    def reset(): # this function resets the screen (aka paints the whole thing black and removes the rays)
        #wipe the ray data, includes main array(s) and counter var
        #blacken the screen, add the walls back in, this could be where you could choose to change the walls
        #means calling a read and data interpret function to get json data or the cv2 reader function to get new wall data
        pass

    @staticmethod
    def render(): # this boi here takes data from the copy of the array and paints the rays onto the screen
        pass

class Physics:
    @staticmethod
    def line_line_collision(): # checks for line-line collision and maybe outputs collision coords as well as the walls/rays that are intersecting? idk yet
        pass

    @staticmethod
    def line_circle_collision(): # checks for if the ray actually is supposed to collide with this circle and then does the position and reflected vector calculations
        pass

    @staticmethod
    def line_ellipse_collision(): # checks for if the ray hit the existing bit of the ellipse (use line-line-collision for this) and then does the calculations for a new vector and the intersection point
        pass
