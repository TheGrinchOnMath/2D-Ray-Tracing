import os, json, sys, pathlib
import numpy as np

def read(path):
    with open(path, "r") as file_temp:
        try:
            # add code here that reads the file contents differently if it is an image or a json
            # add call to opencv function, or add the code into this function
            file = file_temp
            return file
        except FileNotFoundError:
            print("Error: File Not Found.")


def write(data, path):
    with data as write_file:
        try:
            if os.path.exists(path):
                overwrite = str(input("file exists, overwrite? \n\n WARNING, THIS WILL DELETE THE FILE"))
                if overwrite == "yes" or "y" or "Y":
                    pass
            else:
                with open(path, "w") as file:
                    file.write(write_file, path)
        except:
            pass

def path_fiddler(dirs):
    CWD = os.getcwd()
    for dir in dirs:
        try:
            if type(dir) != "string":
                raise TypeError("not a string")
        except TypeError:
            print("Error: not a string")
        

def init_rays(mpos:tuple, n_rays:int):
    arr = np.empty((n_rays, 4))
    for i in range(0, n_rays):
        angle = 2 * np.pi * (i / n_rays)
        v_x = np.cos(angle)
        v_y = np.sin(angle)

        mx, my = mpos
        if i < n_rays:
            arr[i:i+1] = [v_x, v_y, mx, my]
        else:
            arr[i] = [v_x, v_y, mx, my] 

    return arr
        

# find out how to make the code not be able to write outside of the main folder (add .. to the path or give full path)