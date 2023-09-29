import os
import numpy as np
import multiprocessing as mp

print(os.getcwd())

assets_dir = ["assets", "image.png"] #  str(input("type path to image here"))

def path_fiddler(assets_dir):
    CWD = os.getcwd()
    for d in assets_dir:
        newpath = os.path.join(CWD, d)

    return newpath
dir = path_fiddler(assets_dir)

newdir = ""
temp = ""
for i in dir:
    if i == "\\":
        temp = temp + i + i
    else:
        temp = temp + i
print(temp)
"""
def init_rays(mpos:tuple, n_rays:int):
    arr = np.empty((4, n_rays))
    print(arr)
    for i in range(0, n_rays - 1):
        angle = 2 * np.pi * (i / n_rays)
        v_x = np.cos(angle)
        v_y = np.sin(angle)

        mx, my = mpos

        arr[:, i-1] = [v_x, v_y, mx, my]
        # add the bit that adds the position and vector values to the array
        # here

    return arr

    """

def calculate(ray, walls): # ray is the data for the ray, coming from the array, wall is the wall object
    vector = (ray[0], ray[1])
    pos = (ray[2], ray[3])
    # add collision checking function (only intersection and validity checking)
    # with output being the correct wall ID. then calculate position and new vector, plug into new array

"""
def arr_test(dimensions:tuple):
    arr = np.empty(dimensions)
    print(arr)
    lines, columnns = dimensions
    
    for col in range(0, columnns):
        

    return arr
    """

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
arr[1:] = [10, 11, 12]
print(arr)

# to replace an entire columnn, do array[:,i] where i is the value of the collumn minus 1 (make sure that the array is of the right dimensions)