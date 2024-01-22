import pygame
import numpy as np


# parent class. contains all shared attributes of all 3 classes
class Mirror:
    def __init__(self, startPos: tuple, endPos: tuple, color):
        self.startPos = startPos
        self.endPos = endPos
        self.color = color


class segmentMirror(Mirror):
    def __init__(self, startPos, endPos):
        super().__init__(
            startPos, endPos, color="white"
        )  # init super class with variables
        self.vector = pygame.Vector2(
            self.endPos[0] - self.startPos[0], self.endPos[1] - self.startPos[1]
        )

    def draw(self, screen: pygame.surface):
        pygame.draw.line(screen, self.color, self.startPos, self.endPos, 2)

    def rayIntersect(self, rayArr):
        # set variables from rayArr
        rayOrigin = rayArr[:1]
        rayVector = rayArr[2:]

        # move vector to start at origin (creates new fictional position?)
        rayVector = rayOrigin + rayVector

    def normal(self):
        normal = (self.endPos[1] - self.startPos[1], self.endPos[0] - self.startPos[0])
        return normal

def checkIntersections():
    pass


# ray-segment intersection. needs to be as precise as possible
def raySegmentIntersection(rayArr, mirror):
    pass
