import pygame
import os
import cv2
import sys
import ctypes
import random
import math
import multiprocessing
import numpy as np
import concurrent.futures

pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.FULLSCREEN)
screenx, screeny = screen.get_size()


mirrors = []
cpuCoreCount = 4
RAYS = 500  # <-- this variable sets the amount of rays initially emitted from the cursor's position
REFLECT_CTR = (
    0  # <-- this variable keeps track of how many reflections have been calculated
)
#     (could be used to stop the physics after a set number of reflections)


def path_fiddler(
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


def opencv_image_interpreter(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    resize = cv2.resize(img, (screenx, screeny))
    _, threshold = cv2.threshold(resize, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx.ravel()
    return n


def json_reader():
    # this should hold the data for reading the json file containing
    # the wall data
    pass


def physics_calculator(input):  # input is structured as follows: [originx, originy, vectorx, vectory]
    # consider storing the line equation for the rays in addition to what we already have, cuz i use both line equation parameters and vectors...
    pos = pygame.Vector2(input[0], input[1])
    vect = pygame.Vector2(input[2], input[3])
    slope = input[3] / input[2]
    heightAtOrigin = None  # add formula for finding this based on the inputs
    mark = 1000000
    collisionPos = None
    ray_out, pos_out = None
    for mirror in mirrors:
        # check all mirrors, check intersection, find closest mirror and store ID
        collision = mirror.intersect(pos, vect, slope, heightAtOrigin)
        if collision is not None:
            collisionPos = collision
            dist = math.sqrt(
                pow((collision[0] - pos[0]), 2) + pow((collision[1] - pos[1]), 2)
            )  # start is the origin of the ray at position n of the array (arrays start at 0, mind)
            if dist < mark:
                mark = dist
                mirrorId = id(mirror)
                vect = None  # vect is the directional vector of the incident ray that is being calculated
    for mirror in mirrors:
        # get the right mirror and use its data to determine the reflection
        if id(mirror) == mirrorId:
            normal = mirror.normalVector(collisionPos)
            rVect = pygame.Vector2.reflect(vect, normal)
            ray_out = [collisionPos, rVect]
            pos_out = [pos, collisionPos]

        continue

    return (
        ray_out,
        pos_out,
    )  # ray_out is the ray data from the reflection, pos_out is both ends of the calculated ray


def generateMirrors(
    fileType, filePath
):  # could be improved to check for extensions and act accordingly
    mirrors = []
    path = path_fiddler(filePath)

    mirrors.append(Mirror("Line", (0, 0), (screenx, 0)))
    mirrors.append(Mirror("Line", (0, 0), (0, screeny)))
    mirrors.append(Mirror("Line", (screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror("Line", (0, screeny), (screenx, screeny)))

    if fileType == "JSON":
        pass  # this is not implemented yet, this should call a function that takes a json file and creates the mirrors based on that
    if fileType == "Image":
        result = opencv_image_interpreter(path)
        mirrors.append(Mirror("Type", (result[-2], result[-1]), (result[0], result[1])))
        mirrors.append(
            Mirror("Type", (result[-4], result[-3]), (result[-2], result[-1]))
        )
        i = 0
        for j in result:
            if (i % 2 == 0) and len(result) - 4 >= i:
                if result[i] == result[-4]:
                    pass
                else:
                    mirrors.append(
                        Mirror(
                            "Line",
                            (result[i], result[i + 1]),
                            (result[i + 2], result[i + 3]),
                        )
                    )
            i += 1


class Mirror:
    def __init__(
        self, type, startpos, endpos, **kwargs
    ):  # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = pygame.Vector2(startpos)
        self.endpos = pygame.Vector2(endpos)

        if type == "Line":
            self.normal = pygame.Vector2(
                (endpos[1] - startpos[1]), (startpos[0] - endpos[0])
            )

        if type == "Ellipse":
            for key, value in kwargs.items():
                if key == "offset":
                    self.offset = value  # offset from origin
                if key == "dimensions":
                    self.dimensions = value  # (width, height) the values of a and b

            self.a_squared = pow(self.offset[0], 2)
            self.b_squared = pow(self.offset[1], 2)
            self.ab = self.offset[0] * self.offset[1]
            self.height_squared = pow(self.dimensions[1], 2)
            self.width_squared = pow(self.dimensions[0], 2)
            self.focusA = None
            self.focusB = None  # add calculations here

        if type == "Arc":
            for key, value in kwargs.items():
                if key == "radius":
                    self.radius = value
                if key == "center":
                    self.center = value

    def intersect(self, rayOrigin, rayVector, slope, heightAtOrigin):
        intersect = None
        if self.type == "Line":
            x1, y1 = self.startpos
            x2, y2 = self.endpos
            x3, y3 = rayOrigin
            x4, y4 = rayOrigin + rayVector

            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            numerator = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
            if denominator == 0:
                return None
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
            t = numerator / denominator
            if 1 > t > 0 and u > 0:
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                collidePos = pygame.math.Vector2(x, y)
                return collidePos

        if self.type == "Ellipse":
            condition = False  # add the bit that checks if there is supposed to be an intersection at all, and which intersection to regard as being the case
            if condition is True:
                delta = (
                    self.a_squared * pow(slope, 2)
                    + self.b_squared
                    - pow((self.offset_x * slope + (heightAtOrigin - self.offset_y)), 2)
                )
                if delta > 0:
                    posx_1 = (
                        self.b_squared * self.offset_x
                        - self.a_squared * slope * (heightAtOrigin - self.offset_y)
                        + math.sqrt(delta) / self.a_squared * pow(slope, 2)
                        + self.b_squared
                    )
                    posx_2 = (
                        self.b_squared * self.offset_x
                        - self.a_squared * slope * (heightAtOrigin - self.offset_y)
                        - math.sqrt(delta) / self.a_squared * pow(slope, 2)
                        + self.b_squared
                    )
                    # this calculates the x coordinate of the intersection between the ray and the ellipse
                    posy_1 = slope * posx_1 + heightAtOrigin
                    posy_2 = slope * posx_2 + heightAtOrigin

            # insert condition to check if collision is supposed to happen and which intersection is the correct one
            # a temporary plug could be to set the intersections to be above or below a x or y coordinate
            return intersect  # pygame.Vector2

        if self.type == "Arc":
            delta = pow(self.radius, 2) * (pow(slope, 2) + 1) - pow(
                (2 * slope * self.offset[0] + heightAtOrigin - self.offset[1]), 2
            )
            if delta > 0:
                posx_1 = (
                    self.offset[0]
                    - (slope * (heightAtOrigin - self.offset[1]))
                    + math.sqrt(delta)
                ) / (pow(slope, 2) + 1)
                posx_2 = (
                    self.offset[0]
                    - (slope * (heightAtOrigin - self.offset[1]))
                    - math.sqrt(delta)
                ) / (pow(slope, 2) + 1)

                posy_1 = slope * posx_1 + heightAtOrigin
                posy_2 = slope * posx_2 + heightAtOrigin

            return intersect

    def normalVector(self, intersection):
        if self.type == "Line":
            normal = self.normal

        if self.type == "Ellipse":
            AP = pygame.Vector2(intersection - self.focusA)
            BP = pygame.Vector2(intersection - self.focusB)
            normal = pygame.Vector2.normalize(AP * AP.magnitude() + BP * BP.magnitude())

        if self.type == "Arc":
            normal = -1 * (
                pygame.Vector2(
                    (intersection[0] - self.center[0]),
                    (intersection[1] - self.center[1]),
                )
            )
        return normal

    def draw(
        self, color
    ):  # this needs work. the line is easy, but the ellipses might be a little harder. need to rethink the structure of this one
        if self.type == "Line":
            pygame.draw.line(display, color, self.start_pos, self.end_pos, 3)
        if self.type == "Ellipse":
            pass
        if self.type == "Arc":
            pass


def initRays(mpos: tuple, n_rays: int):
    arr = np.empty((n_rays, 4))
    for i in range(0, n_rays):
        angle = 2 * np.pi * (i / n_rays)
        v_x = np.cos(angle)
        v_y = np.sin(angle)

        mx, my = mpos
        if i < n_rays:
            arr[i : i + 1] = [v_x, v_y, mx, my]
        else:
            arr[i] = [v_x, v_y, mx, my]

    return arr


display = pygame.Surface((screenx, screeny))

generateMirrors("Image", ["MK2", "files", "assets", "penrose_unilluminable_room.png"])


def render():
    pygame.display.update()
    pass


def main():
    running = True
    currentCursorPos = (screenx / 2, screeny / 2)
    mousepos = currentCursorPos
    newArray = initRays(currentCursorPos, RAYS)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    event.size, pygame.RESIZABLE | pygame.HWSURFACE
                )
            if event.type == pygame.MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()
                mousepos = (mx, my)

        if mousepos is not None and mousepos != currentCursorPos:
            currentCursorPos = mousepos
            newArray = initRays(currentCursorPos, RAYS)

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=cpuCoreCount
        ) as executor:
            result = executor.map(physics_calculator, newArray)
            for r in next(result):
                print(r)
        for mirror in mirrors:
            mirror.draw()

        print("frame")


if __name__ == "__main__":
    main()
