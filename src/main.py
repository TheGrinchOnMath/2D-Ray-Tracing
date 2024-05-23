import pygame as pg
import numpy as np
import time
import sys
import os
from concurrent.futures import ProcessPoolExecutor

CORE_COUNT = os.cpu_count()


pg.init()
display = pg.display.set_mode((0, 0), pg.HWSURFACE | pg.FULLSCREEN)
screenx, screeny = display.get_size()
screen = pg.Surface((screenx, screeny), pg.SRCALPHA)
mousePos = (screenx / 2, screeny / 2)

mirrors = []
RAYS = 25000
REFLECTIONS = 10
RAY_COLOR = (255, 255, 50, 5)
frame_counter = 0
# this variable is to avoid inaccuracy errors
prec = 10**-10


class Mirror:
    def __init__(self, type, **kwargs):
        self.type = type
        if type == "line":
            self.startPos = kwargs["startpos"]
            self.endPos = kwargs["endpos"]
            self.size = 3
        elif type == "ellipse":
            self.center = kwargs["center"]
            self.eccentricity = kwargs["offset"]

    def intersect(self, startPos, Vect):
        global check_count
        p1, p2 = startPos
        v1, v2 = Vect

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

        elif self.type == "ellipse":
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
                collidepos_1 = (x, y)
                return collidepos_1
            else:
                # this works since m2 is smaller than m1. this logic covers
                # the case where the origin is outside the ellipse.
                x = o1 + c1 + m2 * v1
                y = o2 + c2 + m2 * v2
                collidepos = (x, y)
                pg.draw.circle(screen, "blue", (x, y), 3)
                return collidepos

    def draw(self, color, screen):
        if self.type == "line":
            pg.draw.aaline(screen, color, self.startPos, self.endPos, self.size)

        elif self.type == "ellipse":
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
            pg.draw.ellipse(screen, color, rect, 5)

    def normal(self, intersect):
        if self.type == "line":
            return pg.Vector2(
                self.endPos[1] - self.startPos[1], self.startPos[0] - self.endPos[0]
            )
        if self.type == "ellipse":
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
        newVector = vect.reflect(normal)
        # pg.draw.line(screen, (100, 100, 255), closest, closest + normal.normalize() * 50, 2)
        output = [
            startPos[0],
            startPos[1],
            closest[0],
            closest[1],
            newVector[0],
            newVector[1],
        ]
    return output


def distributor(option, rayMatrix):
    output = np.empty((RAYS, 6))
    errors = 0
    if option:
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


def render(rayMatrix, reset):
    global counter, frame_counter
    BGCOLOR = (10, 10, 10)
    output = np.empty((RAYS, 4))
    if reset is True:
        counter = 0
        screen.fill(BGCOLOR)
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
        newMatrix = distributor(True, rayMatrix)

        # color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        for i in range(RAYS):
            startPos_x, startPos_y, intersect_x, intersect_y, vector_x, vector_y = (
                newMatrix[i]
            )
            pg.draw.aaline(
                screen,
                RAY_COLOR,
                (startPos_x, startPos_y),
                (intersect_x, intersect_y),
            1)
            output[i] = [intersect_x, intersect_y, vector_x, vector_y]

        display.blit(screen, (0, 0))
    pg.draw.circle(display, "orange", mousePos, 5)
    pg.display.flip()
    counter += 1
    frame_counter += 1
    return output


def generateMirrors():
    global mirrors

    mirrors.append(Mirror("line", startpos=(0, 0), endpos=(screenx, 0)))
    mirrors.append(Mirror("line", startpos=(0, 0), endpos=(0, screeny)))
    mirrors.append(Mirror("line", startpos=(screenx, 0), endpos=(screenx, screeny)))
    mirrors.append(Mirror("line", startpos=(0, screeny), endpos=(screenx, screeny)))
    mirrors.append(
        Mirror(
            "ellipse",
            center=(screenx / 2, screeny / 2),
            offset=(screenx * 3 / 7, screeny * 2 / 5),
        )
    )


def main():
    global mousePos
    generateMirrors()
    time_current = time.perf_counter()
    rayMatrix = render(np.empty((RAYS, 4)), True)
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
                    rayMatrix = render(np.empty((RAYS, 4)), True)
        if counter <= REFLECTIONS:
            rayMatrix = render(rayMatrix, False)

        time_new = time.perf_counter()
        # print(
        #    f"Time for frame({frame_counter}): {time_new - time_current:0.4f} seconds"
        # )
        time_current = time_new

    sys.exit()


if __name__ == "__main__":
    main()
