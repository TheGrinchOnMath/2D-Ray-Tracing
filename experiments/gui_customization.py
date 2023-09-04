import pygame, os, sys

pygame.init()

def path_fiddler(dir):
    result = ""
    for element in (os.path.join(os.getcwd(), dir)):
        if element == "\\" or element == "/":
            result += element
        result += element
    return result

print(path_fiddler("assets"))