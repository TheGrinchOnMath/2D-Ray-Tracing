import os, pathlib, cv2, pygame, concurrent.futures, math
import numpy as np
import multiprocessing as mp
"""
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




print(init_rays((10, 10), 100))

def calculate(ray, walls): # ray is the data for the ray, coming from the array, wall is the wall object
    vector = (ray[0], ray[1])
    pos = (ray[2], ray[3])
    print(vector, pos)
    # add collision checking function (only intersection and validity checking)
    # with output being the correct wall ID. then calculate position and new vector, plug into new array


# i need to find a way to use multiprocessing to read the array and use the values of each line as data for the calculate function


"""
def arr_test(dimensions:tuple):
    arr = np.empty(dimensions)
    print(arr)
    lines, columnns = dimensions
    
    for col in range(0, columnns):
        

        return arr
    
"""
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr, "\n")
arr[1:-1] = [10, 11, 12]
print(arr, "\n")
arr[2:] = 0
print(arr)

arr = np.empty((10, 4))
arr[1:-8] = 0
print(arr)



arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
for n in range(0, 3):
    if n < 2:
        print(arr[n:n+1], "\n")
    else:
        print(arr[n:], "\n")


# to replace an entire columnn, do array[:,i] where i is the value of the collumn minus 1 (make sure that the array is of the right dimensions)

"""

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
    

def render(ray_data, walls):
    for n in np.shape(ray_data)[0]:
        # add some code here that paints the image to a temp screen using pygame or sth
        continue
    for wall in walls:
        # add some more code here to paint linear and nonlinear walls with pygame
        continue


arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
for a in arr: # iterates through array lines, 3 with the current array
    print(a) # prints every line of the array in turn


def multiProcessor():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(printList, arr)
        # add code that unwraps the numpy array here
        for r in result:
            print(r)


     # this function is to contain code that takes the ray data workload and distributes it on X processes
         # then returns the calculated datasets
         # would inputting the array with the ray data work?
         # it may be necessary to use the old structure to test the current code
         # i also need to work on the gui, to be able to design shapes with ease
arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])

def printList(list):
    out = []
    for i in list:
        i *= 2
        out.append(i)
    return out

def physics_calculator(input, mirrors): #input is structured as follows: [originx, originy, vectorx, vectory]
    # consider storing the line equation for the rays in addition to what we already have, cuz i use both line equation parameters and vectors...
    pos = pygame.Vector2(input[0], input[1])
    vect = pygame.Vector2(input[2], input[3])
    slope = input[3] / input[2]
    heightAtOrigin = None # add formula for finding this based on the inputs
    mark = 1000000
    collisionPos = None
    for mirror in mirrors: # check all mirrors, check intersection, find closest mirror and store ID
        collision = mirror.intersect(pos, vect, slope, heightAtOrigin)
        if collision is not None:
            collisionPos = collision
            dist = math.sqrt(pow((collision[0] - pos[0]), 2) + pow((collision[1] - pos[1]), 2)) # start is the origin of the ray at position n of the array (arrays start at 0, mind)
            if dist < mark:
                mark = dist
                mirrorId = id(mirror)
                vect = None # vect is the directional vector of the incident ray that is being calculated
    for mirror in mirrors: # get the right mirror and use its data to determine the reflection
        if id(mirror) == mirrorId:
            normal = mirror.normalVector(collisionPos)
            rVect = pygame.Vector2.reflect(vect, normal)
        continue
    ray_out = [collisionPos, rVect]
    pos_out = [pos, collisionPos]

    return ray_out, pos_out # ray_out is the ray data from the reflection, pos_out is both ends of the calculated ray

if __name__ == "__main__":
    print(multiProcessor())
    """