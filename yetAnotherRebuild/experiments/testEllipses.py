import sys
import cv2
import os
import pygame
import numpy as np
import time


class Line:
    def __init__(self, startpos: tuple, endpos: tuple, color: str = "white"):
        # calculate normal vector, save variable
        self.normalVector = pygame.Vector2(
            startpos[1] - endpos[1], endpos[0] - startpos[0]
        )
        self.vector = pygame.Vector2(endpos[0] - startpos[0], endpos[1] - startpos[1])

        self.startpos = startpos
        self.endpos = endpos

        self.length = np.sqrt(
            np.square(endpos[1] - startpos[1]) + np.square(endpos[0] - startpos[0])
        )

        self.color = color

    def checkCollision(self, rayArr):
        rayVector = pygame.Vector2(rayArr[2], rayArr[3])

        rayStartPos = pygame.Vector2(rayArr[0], rayArr[1])

        # create vectors for dot product
        # AP
        vector1 = rayStartPos - pygame.Vector2(self.startpos)
        # AB
        vector2 = self.vector
        # V
        vector3 = rayVector

        commonDenominator = vector1.dot(vector3)

        # commonDenominator is the dot product of the directing vector
        # of the mirror and the ray. if they are colinear, and therefore have n
        if commonDenominator == 0:
            return None

        else:
            rayFactor = vector1.dot(vector2)
            mirrorFactor = vector1.dot(vector3)

            # check if intersection is valid given restrictions
            if rayFactor > 0 and 1 > mirrorFactor > 0:
                # calculate using vectors. find new point thanks to the vector factor
                # we found earlier
                intersection = rayStartPos + rayFactor * rayVector
                return intersection
            else:
                return None


class Arc:
    def __init__(
        self,
        startpos: tuple,
        endpos: tuple,
        startAngle: float,
        endAngle: float,
        radius: float,
        color: str = "white",
    ):
        # init attributes

        self.color = color

        self.startpos = startpos
        self.endpos = endpos
        self.radius = radius

        # initialize angles for determination of valid area of circumference
        # by getting the angle of the vector from center to intersection
        self.startAngle = startAngle
        self.endAngle = endAngle

    def checkCollision(self):
        pass


class Ellipse:
    def __init__(
        self,
        startpos: tuple,
        endpos: tuple,
        startAngle: float,
        endAngle: float,
        eccentricityA: float,
        eccentricityB: float,
        rectStartPos: tuple,
        rectEndPos: tuple,
        color: str = "white",
    ):
        # calculate normal vector, save variable

        self.color = color

        self.startpos = startpos
        self.endpos = endpos

        # initialize angles for determination of valid area of circumference
        # by getting the angle of the vector from center to intersection
        # shared by pygame draw and collision checks

        self.startAngle = startAngle
        self.endAngle = endAngle

        self.eccentricityA = eccentricityA

        self.eccentricityB = eccentricityB

        self.rect = pygame.Rect(
            rectStartPos,
            (rectEndPos[0] - rectStartPos[0], rectEndPos[1] - rectStartPos[1]),
        )

    def checkCollision():
        pass

    def draw(self, surface, color="white"):
        # calculate the rect somehow, for now it should be a function of the angles
        # the rect needs the max height of the ellipse. use eccentricity.
        # for topleft pos, use soe
        pygame.draw.arc(
            surface, color, self.rect, self.startAngle, self.endAngle, width=3
        )





pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE, pygame.DOUBLEBUF)
screenDimensions = screen.get_size()

ellipse = Ellipse(
    (100, 50),
    (400, 200),
    2 * np.pi,
    np.pi,
    100,
    200,
    (100, 100),
    (screenDimensions[0] - 50, screenDimensions[1] / 1.5),
)


def draw():
    ellipse.draw(screen)
    pygame.display.update()


"""
def testPygameArcs(surface, color, boundingRect, startAngle, endAngle):
    screen.fill("black")
    pygame.draw.arc(surface, color, boundingRect, startAngle, endAngle)
    pygame.display.update()
    time.sleep(100)
    print("done!")

 """

pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE, pygame.DOUBLEBUF)


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
    draw()
    """
    testPygameArcs(screen, "white", pygame.Rect(100, 100, 300, 100), 0, np.pi)
    """
