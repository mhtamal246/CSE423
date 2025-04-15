from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
prev_t = time.time()

catcher=0
catcher_speed=25
score=0
endgame= 0
pause= 0
dmd_x= 0
dmd_y= 350
dmd_speed= 2
initial_color= (1, 1, 0)


def show():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glOrtho(-300, 300, -400, 400, 0, 1)
    glColor3f(1.0, 1.0, 1.0)

    if endgame==1:
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(1.0, 1.0, 1.0)

    draw_catcher()
    draw_dmd(dmd_x, dmd_y, initial_color)
    draw_buttons()

    glutSwapBuffers()

def draw_dmd(x, y, col):
    glColor3f(*col)

    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(90, 0, 0, 1)
    glTranslatef(-x, -y, 0)

    top_x    = x
    top_y    = y + 8
    right_x  = x + 15
    right_y  = y
    bottom_x = x
    bottom_y = y - 8
    left_x   = x - 15
    left_y   = y

    mid_algo(left_x,  left_y,  top_x,    top_y)
    mid_algo(top_x,   top_y,   right_x,  right_y)
    mid_algo(right_x, right_y, bottom_x, bottom_y)
    mid_algo(bottom_x,bottom_y,left_x,   left_y)

    glPopMatrix()


def collision():
    catch_left   = -70 + catcher
    catch_right  =  70 + catcher
    catch_top    = -370
    catch_bottom = -390

    d_left   = dmd_x - 13
    d_right  = dmd_x + 13
    d_top    = dmd_y + 13
    d_bottom = dmd_y - 13

    return (catch_left   < d_right  and
            catch_right  > d_left   and
            catch_top    > d_bottom and
            catch_bottom < d_top)

def to_gl(x_pix, y_pix):
    return x_pix - 300, 400 - y_pix


def animate():
    global catcher_speed ,dmd_y, dmd_x, initial_color, dmd_speed, score, endgame, prev_t

    if endgame==1 or pause==1:
        glutPostRedisplay()
        return

    now = time.time()
    delta = now - prev_t
    prev_t = now

    dmd_y -= dmd_speed * delta * 60


    if collision():
        score += 1
        print(f"Score: {score}")
        dmd_speed += 0.5
        dmd_y = 350
        dmd_x = random.randint(-280, 280)
        initial_color = bright_color()
        glutPostRedisplay()
        return


    if dmd_y - 15 < -395:
        endgame = 1
        print(f"Game Over!!! Score: {score}")
        glutPostRedisplay()
        return

    glutPostRedisplay()

def bright_color():
    r = random.random()
    g = random.random()
    b = random.random()

    if r < 0.7 and g < 0.7 and b < 0.7:
        choice = random.choice([0, 1, 2])
        if choice == 0: r = 0.8 + 0.2 * random.random()
        if choice == 1: g = 0.8 + 0.2 * random.random()
        if choice == 2: b = 0.8 + 0.2 * random.random()

    return (r, g, b)

def draw_vertical_bar(x, y_bottom, y_top):
    glBegin(GL_POINTS)
    for y in range(y_bottom, y_top + 1):
        glVertex2f(x, y)
    glEnd()

def draw_buttons():
    glColor3f(0.0, 0.75, 0.78)
    mid_algo(-280, 360, -260, 380)
    mid_algo(-280, 360, -260, 340)
    mid_algo(-260, 360, -220, 360)

    glColor3f(1.0, 0.75, 0.0)

    draw_vertical_bar(-10, 340, 380)
    draw_vertical_bar( 10, 340, 380)

    glColor3f(1.0, 0.0, 0.0)
    mid_algo(220, 380, 260, 340)
    mid_algo(220, 340, 260, 380)


def draw_catcher():
    mid_algo(-70 + catcher, -370, 70 + catcher, -370)
    mid_algo(-70 + catcher, -370, -50 + catcher, -390)
    mid_algo(70 + catcher, -370, 50 + catcher, -390)
    mid_algo(-50 + catcher, -390, 50 + catcher, -390)


def catcher_move(key, x, y):
    global catcher, catcher_speed
    if endgame==1 or pause==1:
        return
    if key == GLUT_KEY_LEFT:
        catcher -= catcher_speed
    elif key == GLUT_KEY_RIGHT:
        catcher += catcher_speed
    if catcher<-230:
        catcher = -230
    if catcher>230:
        catcher = 230

    glutPostRedisplay()

def mid_algo(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    zone = zone_finder(dx, dy)

    c_x1, c_y1 = zone_conv_zero(x1, y1, zone)
    c_x2, c_y2 = zone_conv_zero(x2, y2, zone)

    if c_x1 > c_x2:
        c_x1, c_x2 = c_x2, c_x1
        c_y1, c_y2 = c_y2, c_y1

    c_dx = c_x2 - c_x1
    c_dy = c_y2 - c_y1

    d = 2 * c_dy - c_dx
    east = 2 * c_dy
    nEast = 2 * (c_dy - c_dx)

    while c_x1 <= c_x2:
        X, Y = revert_conv(c_x1, c_y1, zone)
        glBegin(GL_POINTS)
        glVertex2f(X, Y)
        glEnd()
        if d < 0:
            d += east
        else:
            d += nEast
            c_y1 += 1
        c_x1 += 1

def revert_conv(x, y, zone):
    if zone==0:
        return x, y
    if zone==1:
        return y, x
    if zone==2:
        return -y, x
    if zone==3:
        return -x, y
    if zone==4:
        return -x, -y
    if zone==5:
        return -y, -x
    if zone==6:
        return y, -x
    if zone==7:
        return x, -y

def zone_conv_zero(x, y, zone):
    if zone==0:
        return x, y
    if zone==1:
        return y, x
    if zone==2:
        return -y, x
    if zone==3:
        return -x, y
    if zone==4:
        return -x, -y
    if zone==5:
        return -y, -x
    if zone==6:
        return y, -x
    if zone==7:
        return x, -y


def zone_finder(dx, dy):
    zone= None
    if abs(dx)>=abs(dy):
        if dx>=0 and dy>=0:
            zone=0
        if dx<=0 and dy>=0:
            zone=3
        if dx<=0 and dy<=0:
            zone=4
        if dx>=0 and dy<=0:
            zone=7
    else:
        if dx>=0 and dy>=0:
            zone=1
        if dx<=0 and dy>=0:
            zone=2
        if dx<=0 and dy<=0:
            zone=5
        if dx>=0 and dy<=0:
            zone=6

    return zone

def mouse_click(button, state, x_pix, y_pix):
    global pause, endgame, score, catcher, dmd_speed, dmd_x, dmd_y
    global initial_color, prev_t

    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return

    gl_x, gl_y = to_gl(x_pix, y_pix)

    if -280 <= gl_x <= -220 and 340 <= gl_y <= 380:
        print("Starting Over!!!")
        pause        = 0
        endgame      = 0
        score        = 0
        catcher      = 0
        dmd_speed    = 2
        dmd_x        = random.randint(-280, 280)
        dmd_y        = 350
        initial_color = bright_color()
        prev_t       = time.time()
        glutPostRedisplay()
        return


    if -20 <= gl_x <= 20 and 340 <= gl_y <= 380 and endgame!=1:
        if pause==1:
            pause=0
        else:
            pause=1
        prev_t = time.time()
        glutPostRedisplay()
        return

    if 220 <= gl_x <= 260 and 320 <= gl_y <= 380:
        print(f"Goodbye!!! Score: {score}")
        glutLeaveMainLoop()





glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(600,800)
glutInitWindowPosition(500, 100)
glutCreateWindow(b"Game: Catch Diamonds")

glClearColor(0, 0, 0, 0)
glutDisplayFunc(show)
glutSpecialFunc(catcher_move)
glutIdleFunc(animate)
glutMouseFunc(mouse_click)
glutMainLoop()


