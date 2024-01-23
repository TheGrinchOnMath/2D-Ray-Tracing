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

        self.startpos = startpos
        self.endpos = endpos

        self.length = np.sqrt(
            np.square(endpos[1] - startpos[1]) + np.square(endpos[0] - startpos[0])
        )

        self.color = color

    def checkCollision(self, ray):
        pass


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
        rectStartPos:tuple,
        rectEndPos:tuple,
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


    def checkCollision():
        pass

    def draw(self, surface, color="white"):
        # calculate the rect somehow, for now it should be a function of the angles
        # the rect needs the max height of the ellipse. use eccentricity.
        # for topleft pos, use soe
        pygame.draw.arc(surface, color, self.rect, self.startAngle, self.endAngle, width=3)


pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE, pygame.DOUBLEBUF)
screenDimensions = screen.get_size()
        
ellipse = Ellipse((100, 100), (400, 200), 0.5, np.pi, 100, 200, (100, 100), (400, 200))

ellipse.draw()
pygame.display.update()
time.sleep(5)
"""
def testPygameArcs(surface, color, boundingRect, startAngle, endAngle):
    screen.fill("black")
    pygame.draw.arc(surface, color, boundingRect, startAngle, endAngle)
    pygame.display.update()
    time.sleep(100)
    print("done!")

pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE, pygame.DOUBLEBUF)


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
    testPygameArcs(screen, "white", pygame.Rect(100, 100, 300, 100), 0, np.pi)
    """
