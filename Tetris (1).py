#=========================================================================
# Pygame based Tetris v0.1
#
# Copyright 2018 by Daehyuk Ahn
#
# Released under GPL
#=========================================================================
import sys
import time
import random
import pygame
import math

# define Helper class

class Rect:
    def __init__(self, x, y, w, h):
        self.left = x
        self.top = y
        self.right = x + w
        self.bottom = y + h

    def contains(self, x, y):
        # Return true if a point is inside the rectangle.
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

#
# Init global variables
#
TetrisSize = 24
TetrisWidth = 10
TetrisHeight = 24

# Board Map area [TetrisWidth][TetrisHeight] Max
tetrisBoard = [[0] * TetrisHeight for i in range(TetrisWidth)]

# Play Surface
init_status = pygame.init()
pygame.display.set_caption("Tetris")

TetrisWindow = width, height = TetrisWidth * TetrisSize * 2,  TetrisHeight * TetrisSize + 64
TetrisScreen = pygame.display.set_mode(TetrisWindow)

# Define Color
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0, 0, 255)
CYAN = pygame.Color(0, 255, 255)
BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(211, 211, 211)
WHITE = pygame.Color(255, 255, 255)
DARKGRAY = pygame.Color(128, 128, 128)

shapeChar = ["I", "J", "L", "O", "S", "T", "Z"]
shapeColors = [
    (0,   255, 255), # I, Cyan
    (0,   0,   255), # J, Blue
    (255, 165, 0  ), # L, Orange
    (255, 255, 0  ), # O, Yellow
    (0,   255, 0  ), # S, Green
    (255, 0,   255), # T, Purple\
    (255, 0,   0  ), # Z, Red
]
shapeAngle = [0, 90, 180, 270]
shapeBlock = [
    [ # I
        [[0,0],[1,0],[2,0],[3,0]],
        [[2,0],[2,1],[2,2],[2,3]],
        [[0,0],[1,0],[2,0],[3,0]],
        [[1,0],[1,1],[1,2],[1,3]]
    ],
    [ # J
        [[0,0],[1,0],[2,0],[2,1]],
        [[1,0],[1,1],[1,2],[0,2]],
        [[0,0],[0,1],[1,1],[2,1]],
        [[1,0],[2,0],[1,1],[1,2]]
    ],
    [ # L
        [[0,0],[1,0],[2,0],[0,1]],
        [[0,0],[1,0],[1,1],[1,2]],
        [[0,1],[1,1],[2,1],[2,0]],
        [[1,0],[1,1],[1,2],[2,2]]
    ],
    [ # O
        [[0,0],[1,0],[0,1],[1,1]],
        [[0,0],[1,0],[0,1],[1,1]],
        [[0,0],[1,0],[0,1],[1,1]],
        [[0,0],[1,0],[0,1],[1,1]]
    ],
    [ # S
        [[1,0],[2,0],[0,1],[1,1]],
        [[1,0],[1,1],[2,1],[2,2]],
        [[1,0],[2,0],[0,1],[1,1]],
        [[0,0],[0,1],[1,1],[1,2]],
    ],
    [ # T
        [[0,0],[1,0],[2,0],[1,1]],
        [[0,1],[1,0],[1,1],[1,2]],
        [[1,0],[0,1],[1,1],[2,1]],
        [[1,0],[1,1],[1,2],[2,1]]
    ],
    [ # Z
        [[0,0],[1,0],[1,1],[2,1]],
        [[0,1],[0,2],[1,0],[1,1]],
        [[0,0],[1,0],[1,1],[2,1]],
        [[2,0],[2,1],[1,1],[1,2]],
    ]
]

shapeConfig = [[0, 0, 0, 0] * 4 for i in range(7)] #[7][4][0,1,2,3]

# Draw Screen
TetrisScreen.fill(BLACK)

pygame.display.flip()

def makeShapeConfig():
    for s in range(len(shapeBlock)): # 7
        for a in range(len(shapeBlock[s])): # 4
            f, w, h = 3, 0, 0
            for i in range(len(shapeBlock[s][a])): #4
                x, y = shapeBlock[s][a][i]
                if f > x: f = x
                if w < x: w = x
                if h < y: h = y
                #print("[{}, {}],".format(x, y), end="")
            w = w + 1 - f
            h = h + 1
            shapeConfig[s][a] = [f, w, h]
            #print(" = ", shapeConfig[s][a])
    return


def drawTetrisBoard():
    for y in range(TetrisHeight + 1):
        px = 16 + TetrisSize * TetrisWidth
        py = 16 + TetrisSize * y
        pygame.draw.line(TetrisScreen, DARKGRAY, [16, py], [px, py], 1)

    for x in range(TetrisWidth + 1):
        px = 16 + TetrisSize * x
        py = 16 + TetrisSize * TetrisHeight
        pygame.draw.line(TetrisScreen, DARKGRAY, [px, 16], [px, py], 1)

    for y in range(TetrisHeight):
        for x in range(TetrisWidth):
            s = tetrisBoard[x][y]
            if s >= 0:
                drawTetrisBlock(x, y, shapeColors[s])
    return

def drawTetrisBlock(x, y, c):
    # Check range is valid
    if (-1 < x < TetrisWidth) and (-1 < y < TetrisHeight):
        px = 17 + TetrisSize * x
        py = 17 + TetrisSize * y
        pygame.draw.rect(TetrisScreen, c, [px, py, 23, 23], 0)

    return

def drawTetrisNext(x, y, c):
    # Check range is valid
    if (-1 < x < 20) and (-1 < y < TetrisHeight):
        px = 17 + TetrisSize * x
        py = 17 + TetrisSize * y
        pygame.draw.rect(TetrisScreen, c, [px, py, 23, 23], 0)

    return

def drawTetrisOutline(x, y, c):
    # Check range is valid
    if (-1 < x < TetrisWidth) and (-1 < y < TetrisHeight):
        px = 17 + TetrisSize * x
        py = 17 + TetrisSize * y
        pygame.draw.rect(TetrisScreen, c, [px, py, 23, 23], 1)

    return

def isConflict(x, y):
    if x < 0 or x >= TetrisWidth: return -1
    if y < 0 or y >= TetrisHeight: return -1
    return tetrisBoard[x][y]

def drawTetris(x, y, shape, angle):
    global gYmax
    global gGame

    drawTetrisBoard()

    # select current brick
    b = shapeBlock[shape][angle]
    f, w, h = shapeConfig[shape][angle]

    # check fallen tetris conflict
    for i in range(len(b)):
        nx, ny = b[i]
        if isConflict(x + nx, y + ny) != -1:
            dispStart()
            gGame = False
            #pygame.time.set_timer(pygame.USEREVENT, 0)
            return

    # drawing fallen tetris
    for i in range(len(b)):
        nx, ny = b[i]
        drawTetrisBlock(x + nx, y + ny, shapeColors[shape])

    # drawing fallen tetris
    for by in range(y, TetrisHeight - h + 1):
        conflict = False
        for i in range(len(b)):
            nx, ny = b[i]
            if isConflict(x + nx, by + ny) != -1:
                conflict = True
                gYmax = by - 1
                break
        if conflict: break
        gYmax = by

    for i in range(len(b)):
        nx, ny = b[i]
        drawTetrisOutline(x + nx, gYmax + ny, shapeColors[shape])

    # select preview brick
    b = shapeBlock[gNext][0]
    f, w, h = shapeConfig[gNext][0]

    # drawing preview tetris
    for i in range(len(b)):
        nx, ny = b[i]
        drawTetrisNext(13 + nx, 0 + ny, shapeColors[gNext])

    return

def dispScore():
    global gScore, gLines, gLevel

    px = 17 + TetrisSize * 11
    py = 17 + TetrisSize * 20
    pygame.draw.rect(TetrisScreen, BLUE, [px, py, 24 * 7, 24 * 4], 1)

    font = pygame.font.Font(None, 30)
    text = font.render("Lines " + str(gLines), True, WHITE)
    TetrisScreen.blit(text, [px + 12, py + 28 * 0 + 12])
    text = font.render("Level " + str(gLevel), True, WHITE)
    TetrisScreen.blit(text, [px + 12, py + 28 * 1 + 12])
    text = font.render("Score " + str(gScore), True, WHITE)
    TetrisScreen.blit(text, [px + 12, py + 28 * 2 + 12])

    return

def dispStart():
    global gScore, gLines, gLevel

    px = 17 + TetrisSize * 2
    py = 17 + TetrisSize * 10
    pygame.draw.rect(TetrisScreen, BLUE, [px, py, 24 * 15, 24 * 3], 0)

    font = pygame.font.Font(None, 30)
    if not gGame:
        text = font.render("Game Ready!", True, WHITE)
    else:
        text = font.render("Game Over!", True, WHITE)

    TetrisScreen.blit(text, [px + 12, py + 28 * 0 + 12])
    text = font.render("Press 'N' key to start new game!", True, WHITE)
    TetrisScreen.blit(text, [px + 12, py + 28 * 1 + 12])

    return

def processTimer(event):
    global gChar, gAngle, gNext
    global gXpos, gYpos
    global gYmax
    global gGame

    if not gGame: return

    gYpos = gYpos + 1

    f, w, h = shapeConfig[gChar][gAngle]

    if gYpos >= gYmax:
        addTetris(gXpos, gYpos, gChar, gAngle)
        gXpos, gYpos, gAngle = 3, 0, 0
        gChar = gNext
        gNext = random.randint(0, len(shapeChar) - 1)

    TetrisScreen.fill(BLACK)
    drawTetris(gXpos, gYpos, gChar, gAngle)
    pygame.display.flip()

    return

# remove one line from top to bottom
def removeLine(y):
    # pull down lines
    for by in range(y, 0, -1):
        for bx in range(0, TetrisWidth):
            tetrisBoard[bx][by] = tetrisBoard[bx][by - 1]
    # erase top line
    for bx in range(0, TetrisWidth):
        tetrisBoard[bx][0] = -1
    return

# Add fallen tetris into board
def addTetris(x, y, shape, angle):
    global gScore, gLines, gLevel, gTime
    scores = [0, 40, 100, 300, 120]

    b = shapeBlock[shape][angle]

    for i in range(len(b)):
        nx, ny = b[i]
        tetrisBoard[x + nx][y + ny] = shape

    # check if line is full
    cLines = gLines
    for by in range(TetrisHeight - 1, 0, -1):
        full = True
        for bx in range(0, TetrisWidth):
            if tetrisBoard[bx][by] == -1:
                full = False
                break
        # flash effect should be add
        if full:
            removeLine(by)
            gLines += 1

    # Calc Score
    cLines = gLines - cLines
    gScore += scores[cLines]
    #calc level and drop timer
    cLevel = int(gLines / 10) + 1
    if gLevel != cLevel:
        gLevel = cLevel
        # level 1 = 500 ms, level 50 and above = 50 ms
        gTime = gLevel if gLevel < 50 else 50
        gTime = int(math.cos(math.pi / 100.0 * gTime)* 500)
        print("Level = {}, Timer = {}ms".format(gLevel, gTime))
        pygame.time.set_timer(pygame.USEREVENT, gTime)


    return

#shapeChar = ["I", "J", "L", "O", "S", "T", "Z"]
shapeChar = ["T", "S", "Z", "J", "L", "I", "O"]
shapeAngle = [0, 90, 180, 270]
gChar, gAngle = 0, 0
gXpos, gYpos, gYmax = 3, 0, 0
gScore, gLines, gLevel, gNext = 0, 0, 1, 0
gGame = False
gTime = 0
def keyDown(event):
    global gChar, gAngle
    global gXpos, gYpos
    global gGame

    if not gGame:
        if event.key == pygame.K_n:
            gGame = True
            newGame()
        return

    if event.key == pygame.K_RETURN:
        if (gChar + 1) < len(shapeChar):
            gChar += 1
        else:
            gChar = 0
    elif event.key == pygame.K_UP:
        if (gAngle + 1) < len(shapeAngle):
            gAngle += 1
        else:
            gAngle = 0
        # Get new shape
        f, w, h = shapeConfig[gChar][gAngle]
        # Adjust left side
        if gXpos < 0: gXpos = 0
        # Adjust right side
        if gXpos > (TetrisWidth - (w + f)):
            gXpos = TetrisWidth - (w + f)

    elif event.key == pygame.K_DOWN:
        processTimer(event)

    elif event.key == pygame.K_SPACE:
        gYpos = gYmax - 1
        processTimer(event)

    elif event.key == pygame.K_LEFT:
        #shape = shapeBlock[gChar][gAngle]
        f, w, h = shapeConfig[gChar][gAngle]
        #print(f, w, h)
        if gXpos > (-f): gXpos -= 1

    elif event.key == pygame.K_RIGHT:
        f, w, h = shapeConfig[gChar][gAngle]
        if gXpos < (TetrisWidth - (w + f)): gXpos += 1


    TetrisScreen.fill(BLACK)
    drawTetris(gXpos, gYpos, gChar, gAngle)

    return

def newGame():
    global gChar, gAngle, gNext
    global gScore, gLines, gLevel
    global gGame, gTime

    print("newGame called!")

    # Clean up Tetris values
    gScore, gLines, gLevel = 0, 0, 1
    gAngle = 0

    if not gGame:
        gChar = random.randint(0, len(shapeChar) - 1)
        gNext = random.randint(0, len(shapeChar) - 1)

    # Clean up Tetris board
    for y in range(TetrisHeight):
        for x in range(TetrisWidth):
            tetrisBoard[x][y] = -1

    drawTetris(gXpos, gYpos, gChar, gAngle)
    dispScore()
    pygame.display.flip()

    gTime = gLevel if gLevel < 50 else 50
    print("Level = {}, Timer = {}ms".format(gLevel, gTime))
    gTime = int(math.cos(math.pi / 100.0 * gTime)* 500)
    pygame.time.set_timer(pygame.USEREVENT, gTime)
    return

#--------------------------------------------------------------------------
# Main program
#--------------------------------------------------------------------------
def main():
    global shapeChar, shapeAngle
    global gChar, gAngle
    global gXpos, gYpos
    global gTime

    makeShapeConfig()
    newGame()
    dispStart()


    #pygame.time.set_timer(pygame.USEREVENT, 500)

    # main game loop
    while True:

        # Get Keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                keyDown(event)
                dispScore()
                pygame.display.flip()
            elif event.type == pygame.USEREVENT:
                processTimer(event)
                dispScore()
                pygame.display.flip()

# run code
if __name__ == '__main__':
    main()