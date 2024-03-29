#!/usr/bin/env python
# coding: utf-8
import os, pygame, sys, cv2


def read_file(path:str, type:str): # returns either the json data or the contour coords list from the image processing
    if type == "json":
        with read_file(path, "r") as fi:
            try:
                print(fi)
            except:
                print("something went wrong when accessing:", path)
    elif type == "image":
        with cv2.imread(path, cv2.IMREAD_GRAYSCALE) as img:
            try:
                _, thresh = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
                cont, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in cont:
                    approx = cv2.approxPolyDP(cnt, 3, True)
                    n = approx.ravel()
                    print(n)
                    return n
            except:
                print("something went wrong with the image")
    else:
        raise SyntaxError("wrong file type specified, please specify either [image] or [json]")
    

def write_file(path):
    try:
        if os.path.exists(path):
            print("this file already exists. Overwrite?\n")
            if str(input()) == ("y" or "yes" or "Y" or "Yes"):
                print("ok, attempting to overwrite file...")
                with open(path, "w") as write_file:
                    pass
                    #add code here to write data to file. This could be a config file, the OG data file, the bit where the GUI does the saving


                # add here a way to make sure the code is allowed to actually delete the file (check the path and file type, do not write outside of saves folder maybe)
    except PermissionError:
        print("could not write file due to lack of permissions, aborting...")
        
            
def path_fiddler(dirs:list): # dirs has to be all folders leading from current working directory to the end file, so that the path can be used for file operations
    CWD = os.getcwd()
    out = CWD
    for element in dirs:
        os.path.join(out, element)
    temp = ""
    for i in out:
        if i == "\\":
            temp += i
        temp += i
    return temp



# OOP: rethink program structure, and start porting over some of the code from the experiments file
class Render:
    @staticmethod
    def reset(): # this function resets the screen (aka paints the whole thing black and removes the rays)
        #wipe the ray data, includes main array(s) and counter var
        #blacken the screen, add the walls back in, this could be where you could choose to change the walls
        #means calling a read and data interpret function to get json data or the cv2 reader function to get new wall data
        pass

    @staticmethod
    def render(ray_data_arr, walls): # this boi here takes data from the copy of the array and paints the rays onto the screen
        pass

class Physics:
    @staticmethod
    def line_line_collision(): # checks for line-line collision and maybe outputs collision coords as well as the walls/rays that are intersecting? idk yet
        pass

    @staticmethod
    def line_circle_collision(): # checks for if the ray actually is supposed to collide with this circle and then does the position and reflected vector calculations
        pass

        # this needs the equation for x and y, given a set of predetermined parameters


    @staticmethod
    def line_ellipse_collision(): # checks for if the ray hit the existing bit of the ellipse (use line-line-collision for this) and then does the calculations for a new vector and the intersection point
        pass

        """
        this bit needs to first check collisions between the ray and the line connecting the extremities of the arc (cut off ellipse), then check if it is supposed to collide, then save the intersection spot
        a line-line intersection can be used for this
        """

        # think about modularity extensiveness, how phat should any given function be to optimize exection time and task-switching-related strains?

"""

what variables do i want to use?
I need:
> ray origin and directing vector
> Line_Wall start and end, normal vector
> Ellipse_Wall start, end, line_wall for step 1 collision checking. Some kind of variables for step 2 collision checking
that define the curvature of the ellipses. when creating, first determine the A, B coordinates and 
the sum of distances ||AP|| + ||BP||
>Circle_Wall start, end, radius, offset, line that defines which bit exists


I need to figure out the best way to convert one definition of line/circle/ellipse into another.
mainly vector + point notation to explicit cartesian notation.
I need the equation for the line tangent to the point(s) of intersection of an ellipse


"""