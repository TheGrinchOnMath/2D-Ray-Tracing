import pygame as pg
import numpy as np
import time
import sys
import os
import json
import cv2
from concurrent.futures import ProcessPoolExecutor

CORE_COUNT = os.cpu_count()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# change the values in the tuple for manual display size setting
screenx, screeny = (0, 0)
args = pg.HWSURFACE | pg.FULLSCREEN if screenx == 0 and screeny == 0 else pg.HWSURFACE
pg.init()
display = pg.display.set_mode((screenx, screeny), args)
screenx, screeny = display.get_size()
screen = pg.Surface((screenx, screeny), pg.SRCALPHA)
mousePos = (screenx / 2, screeny / 2)

"""
THE ASPECT RATIO HAS TO BE 16:9 FOR THE JSON FILES
if necessary just set screenx and screeny manually
THE JSON FILES CONTAIN FRACTIONS OF SCREENX AND SCREENY
"""

mirrors = []
RAYS = 100
REFLECTIONS = 2
RAY_COLOR = (255, 255, 50, 100)
frame_counter = 0
# this variable is to avoid inaccuracy errors
prec = 10**-12
ANGLE_REF_VEC = pg.Vector2(1, 0)
# avoid on windows for now
multiprocessing = False
antialiasing = False


class Mirror:
    def __init__(self, type, **kwargs):
        self.type = type
        if type == "line":
            self.startPos = kwargs["startpos"]
            self.endPos = kwargs["endpos"]
            self.size = 3
        elif type == "EllipticArc":
            self.center = kwargs["center"]
            self.eccentricity = kwargs["eccentricity"]
            self.startAngle = kwargs["startAngle"]
            self.endAngle = kwargs["endAngle"]

    def intersect(self, startPos, Vect):
        p1, p2 = startPos
        v1, v2 = Vect
        collidePos = None

        if self.type == "line":
            a1, a2 = self.startPos
            b1, b2 = self.endPos

            denominator = v2 * (b1 - a1) - v1 * (b2 - a2)
            if denominator == 0:
                return None

            m = ((b2 - a2) * (p1 - a1) - (b1 - a1) * (p2 - a2)) / denominator
            n = (v2 * (p1 - a1) - v1 * (p2 - a2)) / denominator

            if 1 > n > 0 and m > 0:
                x = a1 + n * (b1 - a1)
                y = a2 + n * (b2 - a2)
                collidePos = (x, y)
                return collidePos
            else:
                return None

        elif self.type == "EllipticArc":
            a, b = self.eccentricity
            c1, c2 = self.center
            o1, o2 = (p1 - c1, p2 - c2)

            ## try except is to attempt to catch errors without crashing the code
            try:
                q1 = pow(a * v2, 2) + pow(b * v1, 2)
                q4 = pow(v1 * o2 - v2 * o1, 2)
                if q1 < q4:
                    return None
                else:
                    q3 = np.sqrt(q1 - q4)
                    m1 = (-(a * a * v2 * o2) - (b * b * v1 * o1) + a * b * q3) / q1
                    m2 = (-(a * a * v2 * o2) - (b * b * v1 * o1) - a * b * q3) / q1
            except ZeroDivisionError:
                print(q1)
            except TypeError:
                print(q3)
            # add more checks here when using elliptic arcs
            # bug: when ray origin is inside ellipse, rays escape. when ray origin is outside ellipse, all fine

            if m1 > prec and m2 < prec:
                x = o1 + c1 + m1 * v1
                y = o2 + c2 + m1 * v2
                collidePos = (x, y)
            # could implement search with small steps to compare when steps find something and intersect finds none
            elif m2 > prec and m1 < prec:
                x = o1 + c1 + m2 * v1
                y = o2 + c2 + m2 * v2
                collidePos = (x, y)

            elif m1 > prec and m2 > prec:
                # this works since m2 is smaller than m1. this logic covers
                # the case where the origin is outside the ellipse.
                x = o1 + c1 + m2 * v1
                y = o2 + c2 + m2 * v2
                collidePos = (x, y)

            # once collision has been calculated, compare the angle of CP to the angle that was set in variable
            if collidePos is not None:
                angleVec = pg.Vector2(
                    self.center[0] - collidePos[0], self.center[1] - collidePos[1]
                )
                collisionAngle = angleVec.angle_to(ANGLE_REF_VEC)
                # convert the collisionAngle to a positive one, since angles are on a circle and therefore modulus is appropriate
                collisionAngle = (collisionAngle + 360) % 360

                return (
                    collidePos
                    if (
                        collisionAngle <= self.endAngle
                        and collisionAngle >= self.startAngle
                    )
                    else None
                )

    def draw(self, color, screen):
        if self.type == "line":
            pg.draw.aaline(screen, color, self.startPos, self.endPos, self.size)

        elif self.type == "EllipticArc":
            pg.draw.circle(
                screen,
                "white",
                (
                    self.center[0] + (self.eccentricity[0] + self.eccentricity[1]) / 2,
                    self.center[1],
                ),
                7,
            )
            topleft = pg.Vector2(self.center) - pg.Vector2(self.eccentricity)
            rect = pg.Rect(
                topleft[0],
                topleft[1],
                2 * self.eccentricity[0],
                2 * self.eccentricity[1],
            )
            pg.draw.arc(
                screen,
                color,
                rect,
                (self.startAngle + 180) * 2 * np.pi / 360,
                (self.endAngle + 180) * 2 * np.pi / 360,
                4,
            )

    def normal(self, intersect):
        if self.type == "line":
            return pg.Vector2(
                self.endPos[1] - self.startPos[1], self.startPos[0] - self.endPos[0]
            )
        if self.type == "EllipticArc":
            # the key here is to adjust the intersections for an ellipse placed at origin
            vect = pg.Vector2(
                2 * (intersect[0] - self.center[0]) / (self.eccentricity[0] ** 2),
                2 * (intersect[1] - self.center[1]) / (self.eccentricity[1] ** 2),
            )
            return vect


def rayPhysicsHandler(matrix):
    output = []
    mark = 100000
    closest = None
    result = None
    data = matrix
    startPos = (data[0], data[1])
    vect = pg.Vector2(data[2], data[3])
    for mirror in mirrors:
        result = mirror.intersect(startPos, vect)
        if result is not None:
            collision = result
            dist = np.sqrt(
                (startPos[0] - collision[0]) ** 2 + (startPos[1] - collision[1]) ** 2
            )
            if dist < mark and dist > 10**-6:
                mark = dist
                closest = collision
                normal = mirror.normal(result)

    if closest is not None:

        pg.draw.circle(screen, "blue", closest, 5, 5)
        newVector = vect.reflect(normal)
        #pg.draw.line(screen, (100, 100, 255), closest, closest + normal.normalize() * 50, 2)
        output = [
            startPos[0],
            startPos[1],
            closest[0],
            closest[1],
            newVector[0],
            newVector[1],
        ]
    return output


def distributor(multiprocessing, rayMatrix):
    output = np.empty((RAYS, 6))
    errors = 0
    if multiprocessing:
        with ProcessPoolExecutor(max_workers=CORE_COUNT) as executor:
            _out = executor.map(rayPhysicsHandler, rayMatrix)

        for i in enumerate(_out):
            try:
                output[i[0]] = i[1]
            except ValueError:
                errors += 1
    else:
        for i in range(RAYS):
            out = rayPhysicsHandler(rayMatrix[i])
            try:
                output[i] = out
            except ValueError:
                errors += 1

    print(
        f"error count for frame no ({frame_counter}): {errors}"
    ) if errors > 0 else None
    return output


def render(rayMatrix, reset, layers, antialiasing, multiprocessing):
    global counter, frame_counter
    BGCOLOR = (10, 10, 10)
    output = np.empty((RAYS, 4))
    if reset is True:
        clear()
        counter = 0
        screen.fill(BGCOLOR)
        layers.fill(BGCOLOR)
        for i in range(RAYS):
            # find angle in radians using fraction of 2pi
            angle = 2 * np.pi * (i / RAYS)
            vect = pg.Vector2(np.cos(angle), np.sin(angle))
            startPos = mousePos
            if i < RAYS:
                output[i : i + 1] = [startPos[0], startPos[1], vect[0], vect[1]]
            else:
                output[i] = [startPos[0], startPos[1], vect[0], vect[1]]

    else:
        for mirror in mirrors:
            mirror.draw("white", screen)
        print(f"calculating intersections for {RAYS} rays...")
        newMatrix = distributor(multiprocessing, rayMatrix)
        print("done!")

        # color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        print(f"rendering set {counter}...")
        for i in range(RAYS):
            startPos_x, startPos_y, intersect_x, intersect_y, vector_x, vector_y = (
                newMatrix[i]
            )
            pg.draw.aaline(
                screen,
                RAY_COLOR,
                (startPos_x, startPos_y),
                (intersect_x, intersect_y),
                1,
            ) if antialiasing else (
                pg.draw.line(
                    screen,
                    RAY_COLOR,
                    (startPos_x, startPos_y),
                    (intersect_x, intersect_y),
                    1,
                )
            )
            output[i] = [intersect_x, intersect_y, vector_x, vector_y]
        layers.blit(screen, (0, 0))

        display.blit(layers, (0, 0))

        print("done!\n")
    pg.draw.circle(display, "orange", mousePos, 5)
    pg.display.flip()
    counter += 1
    frame_counter += 1
    return output


def cv2EdgeFind(PATH):
    # read image with cv2, nize it to fit display
    img_temp = cv2.imread(PATH, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img_temp, (screenx, screeny))

    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx.ravel()
    return n


def pathFiddler(dir: list):
    # this function takes a list of folders and the file to be used
    # as strings, and returns the full path to the file with syntax appropriate for the relevant operating system
    temp = ""  # temporary, for use whilst concatenating the directories in the dir variable
    result = ""  # will contain the final string that is returned by this function
    for element in dir:  # creates a string containing the path from CWD to file
        temp = os.path.join(temp, element)

    for char in os.path.join(os.getcwd(), temp):
        # this loop iterates through the string, and adds an extra backslash to escape the first one
        # this avoids issues with backslashes being interpreted as syntax symbols such as \n or \t
        if char == ("\\" or "/"):
            result += char
        result += char
    return result


def generateMirrors(type: str, abspath: str):
    global mirrors

    LineMirrorCoords = [
        [(0, 0), (screenx, 0)],
        [(0, 0), (0, screeny)],
        [(screenx, 0), (screenx, screeny)],
        [(0, screeny), (screenx, screeny)],
    ]

    for li in LineMirrorCoords:
        mirrors.append(Mirror("line", startpos=li[0], endpos=li[1]))

    if type == "image":
        n = cv2EdgeFind(abspath)
        mirrors.append(Mirror("line", startpos=(n[-2], n[-1]), endpos=(n[0], n[1])))
        mirrors.append(Mirror("line", startpos=(n[-4], n[-3]), endpos=(n[-2], n[-1])))
        for i in range(len(n)):
            if (i % 2 == 0) and len(n) - 4 >= i:
                if n[i] == n[-4]:
                    pass
                else:
                    mirrors.append(
                        Mirror(
                            "line",
                            startpos=(n[i], n[i + 1]),
                            endpos=(n[i + 2], n[i + 3]),
                        )
                    )

    elif type == "json":
        try:
            with open(abspath, "r") as r:
                jsonFile = json.load(r)
        except FileNotFoundError:
            print("File not found. Exiting...")
            sys.exit()

        mirrorList = jsonFile["mirrors"]

        for mirror in mirrorList:
            if mirror["type"] == "Line":
                startpos = (
                    mirror["startPos"][0] * screenx,
                    mirror["startPos"][1] * screeny,
                )
                endpos = (mirror["endPos"][0] * screenx, mirror["endPos"][1] * screeny)
                mirrors.append(Mirror("line", startpos=startpos, endpos=endpos))
            elif mirror["type"] == "EllipticArc":
                c = (mirror["center"][0] * screenx, mirror["center"][1] * screeny)
                e = (
                    mirror["eccentricity"][0] * screenx,
                    mirror["eccentricity"][1] * screeny,
                )
                mirrors.append(
                    Mirror(
                        "EllipticArc",
                        center=c,
                        eccentricity=e,
                        startAngle=mirror["startAngle"],
                        endAngle=mirror["endAngle"],
                    )
                )


# path = pathFiddler(["assets", "img", "penrose_unilluminable_room.png"])
# generateMirrors("image", path)
path = pathFiddler(["assets", "json", "test_1.json"])
generateMirrors("json", path)
def main():
    global mousePos
    layers = screen.copy()
    time_current = time.perf_counter()
    rayMatrix = render(np.empty((RAYS, 4)), True, layers, antialiasing, multiprocessing)
    quit = False
    while not quit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q and event.key == pg.K_LCTRL:
                    quit = True

                if event.key == pg.K_SPACE:
                    mousePos = pg.mouse.get_pos()
                    rayMatrix = render(
                        np.empty((RAYS, 4)), True, layers, antialiasing, multiprocessing
                    )
        if counter <= REFLECTIONS:
            rayMatrix = render(rayMatrix, False, layers, antialiasing, multiprocessing)

        time_new = time.perf_counter()
        print(
            f"Time for frame({frame_counter}): {time_new - time_current:0.4f} seconds"
        ) if counter <= REFLECTIONS else None
        time_current = time_new

    sys.exit()


if __name__ == "__main__":
    main()
