import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, math, cv2, sys, concurrent.futures
import numpy as np
import mpmath as math

class Mirror:
    def __init__(self, type, startpos, endpos, **kwargs): # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = startpos
        self.endpos = endpos
        self.normal = pygame.Vector2(((startpos[1] - endpos[1]), (endpos[0] - startpos[0])))

    def intersect(self, rayData):
        x1 = self.startpos[0]
        x2 = self.endpos[0]
        x3 = rayData[0]
        x4 = rayData[0] + rayData[2]
        y1 = self.startpos[1]
        y2 = self.endpos[1]
        y3 = rayData[1]
        y4 = rayData[1] + rayData[3]

        denominator = math.fsub(math.fmul(math.fsub(x1,x2), math.fsub(y3,y4)),math.fmul(math.fsub(y1,y2),math.fsub(x3,x4)))
        numerator = math.fsub(math.fmul(math.fsub(x1,x3), math.fsub(y3,y4)),math.fmul(math.fsub(y1,y3),math.fsub(x3,x4)))
        if denominator == 0:
            return None
        u = math.fdiv(math.fneg(math.fmul(math.fsub(x1,x2), math.fsub(y1,y3)), math.fmul(math.fsub(y1,y2), math.fsub(x1,x3))), denominator)
        t = math.fdiv(numerator, denominator)
        if 1 > t > 0 and u > 0:
            x = math.fadd(x1, math.fmul(t, math.fsub(x2, x1)))
            y = math.fadd(y1, math.fmul(t, math.fsub(y2, y1)))
            collidePos = (x, y)
            return collidePos
                           
    def draw(self, color): # this needs work. the line is easy, but the ellipses might be a little harder. need to rethink the structure of this one
        if self.type == "Line":
            pygame.draw.line(screen, color, self.startpos, self.endpos, 3)

def intersectFunction(rayData):
    mark = 100000
    collision = None
    for mirror in mirrors:
        collision = mirror.intersect(rayData)
        if collision is not None:
            result = collision
            dist = math.hypot(math.fsub(collision[0], rayData[0]), math.fsub(collision[1], rayData[1]))
            if dist < mark:
                mark = dist
                intersect = result
                ID = id(mirror)
    if collision is not None:
        for mirror in mirrors:
            if ID == id(mirror):
                newVector = ()

def reflect(incidentVector, normalVector):
    var1 = math.fmul(2, math.fdot((incidentVector[0], normalVector[0]), (incidentVector[1], normalVector[1])))
    