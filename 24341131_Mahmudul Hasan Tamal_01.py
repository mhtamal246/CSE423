######################################################################
################################TASK 1################################
######################################################################

from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
import random

grey_rain = []
white_rain = []
wind_angle = 0
sky_step = 2
sky_colors = [(204/255, 231/255, 232/255),
              (171/255, 219/255, 227/255),
              (100/255, 100/255, 180/255),
              (30/255, 30/255, 60/255)]

for i in range(50):
    x = random.randint(-640, 640)
    y = random.randint(180, 360)
    grey_rain.append([x, y])

for i in range(50):
    x = random.randint(-640, 640)
    y = random.randint(180, 360)
    white_rain.append([x, y])

def Show():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1280, 720)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-640, 640, -360, 360, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_sky()
    draw_field()
    draw_trees()
    draw_house()
    draw_rain()
    glutSwapBuffers()

def draw_rain():
    global wind_angle

    if wind_angle == 0:
        x_shift = 0
    elif wind_angle > 0:
        x_shift = 10
    else:
        x_shift = -10

    glColor3f(200/255, 128/255, 128/255)
    glBegin(GL_LINES)
    for i in range(50):
        glVertex2f(grey_rain[i][0], grey_rain[i][1])
        glVertex2f(grey_rain[i][0] + x_shift, grey_rain[i][1] - 15)
    glEnd()

    glColor3f(255/255, 255/255, 255/255)
    glBegin(GL_LINES)
    for i in range(50):
        glVertex2f(white_rain[i][0], white_rain[i][1])
        glVertex2f(white_rain[i][0] + x_shift, white_rain[i][1] - 15)
    glEnd()

def animate():
    for i in range(50):
        grey_rain[i][1] -= 5
        if grey_rain[i][1] < -360:
            grey_rain[i][0] = random.randint(-640, 640)
            grey_rain[i][1] = random.randint(180, 360)

    for i in range(50):
        white_rain[i][1] -= 5
        if white_rain[i][1] < -360:
            white_rain[i][0] = random.randint(-640, 640)
            white_rain[i][1] = random.randint(180, 360)

    glutPostRedisplay()

def keyboardListener(key, x, y):
    global wind_angle

    if key == GLUT_KEY_RIGHT:
        if wind_angle < 60:
            wind_angle += 20
            print("Wind++")
    elif key == GLUT_KEY_LEFT:
        if wind_angle > -60:
            wind_angle -= 20
            print("Wind--")

    glutPostRedisplay()

def normalKeyListener(key, x, y):
    global sky_step

    if key == b'd':
        if sky_step > 0:
            sky_step -= 1
            print("day")

    elif key == b'a':
        if sky_step < 3:
            sky_step += 1
            print("night")

    glutPostRedisplay()

def draw_sky():
    global sky_step
    glBegin(GL_QUADS)
    glColor3f(sky_colors[sky_step][0], sky_colors[sky_step][1], sky_colors[sky_step][2])
    glVertex2f(-640, 180)
    glVertex2f(640, 180)
    glVertex2f(640, 360)
    glVertex2f(-640, 360)
    glEnd()

def draw_field():
    glBegin(GL_QUADS)
    glColor3f(224/255, 123/255, 57/255)
    glVertex2f(-640, -360)
    glVertex2f(640, -360)
    glVertex2f(640, 180)
    glVertex2f(-640, 180)
    glEnd()

def draw_trees():
    num_trees = 20
    start = -600
    spacing = 63

    for i in range(num_trees):
        x = start + i * spacing
        draw_tree(x, 140)

def draw_tree(x, y):
    glBegin(GL_QUADS)
    glColor3f(140/255, 70/255, 20/255)
    glVertex2f(x - 8, y - 40)
    glVertex2f(x + 8, y - 40)
    glVertex2f(x + 8, y)
    glVertex2f(x - 8, y)
    glEnd()

    glBegin(GL_TRIANGLES)
    glColor3f(0/255, 153/255, 0/255)
    glVertex2f(x - 25, y)
    glVertex2f(x + 25, y)
    glVertex2f(x, y + 35)

    glColor3f(0/255, 191/255, 0/255)
    glVertex2f(x - 20, y + 15)
    glVertex2f(x + 20, y + 15)
    glVertex2f(x, y + 50)

    glColor3f(0/255, 229/255, 0/255)
    glVertex2f(x - 15, y + 30)
    glVertex2f(x + 15, y + 30)
    glVertex2f(x, y + 65)
    glEnd()

def draw_house():
    glBegin(GL_QUADS)
    glColor3f(245/255, 245/255, 220/255)
    glVertex2f(-250, -150)
    glVertex2f(250, -150)
    glVertex2f(250, 120)
    glVertex2f(-250, 120)
    glEnd()

    glBegin(GL_TRIANGLES)
    glColor3f(255/255, 222/255, 89/255)
    glVertex2f(-280, 120)
    glVertex2f(280, 120)
    glVertex2f(0, 250)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(102/255, 51/255, 0/255)
    glVertex2f(-50, -150)
    glVertex2f(50, -150)
    glVertex2f(50, -30)
    glVertex2f(-50, -30)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(135/255, 206/255, 250/255)
    glVertex2f(-180, 20)
    glVertex2f(-100, 20)
    glVertex2f(-100, 90)
    glVertex2f(-180, 90)

    glVertex2f(100, 20)
    glVertex2f(180, 20)
    glVertex2f(180, 90)
    glVertex2f(100, 90)
    glEnd()

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1280, 720)
glutInitWindowPosition(250, 150)
wind = glutCreateWindow(b"Part_1")
glutDisplayFunc(Show)
glutIdleFunc(animate)
glutSpecialFunc(keyboardListener)
glutKeyboardFunc(normalKeyListener)
glutMainLoop()

######################################################################
################################TASK_2################################
######################################################################

# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random
#
# width, height = 800, 800
#
# points = []
# initial_speed = 0.1
# speed_multiplier = 0.2
# max_speed = 1
#
# is_black_screen = False
# is_paused = False
#
# saved_speed_multiplier = speed_multiplier
#
#
# def toggle_pause():
#     global is_paused, saved_speed_multiplier, speed_multiplier
#     is_paused = not is_paused
#     if is_paused:
#         saved_speed_multiplier = speed_multiplier
#         speed_multiplier = 0
#     else:
#         speed_multiplier = saved_speed_multiplier
#
#
# class MovingPoint:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.dx = random.choice([-1, 1]) * initial_speed
#         self.dy = random.choice([-1, 1]) * initial_speed
#         self.color = (random.random(), random.random(), random.random())
#
#     def update(self):
#         if not is_paused:
#             self.x += self.dx * speed_multiplier
#             self.y += self.dy * speed_multiplier
#
#             if self.x >= 400 or self.x <= -400:
#                 self.dx *= -1
#             if self.y >= 400 or self.y <= -400:
#                 self.dy *= -1
#
#     def draw(self):
#         glColor3f(*self.color)
#         glPointSize(5)
#         glBegin(GL_POINTS)
#         glVertex2f(self.x, self.y)
#         glEnd()
#
#
# def Show():
#     global is_black_screen
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
#     glViewport(0, 0, width, height)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(-400, 400, -400, 400, 0.0, 1.0)
#     glMatrixMode(GL_MODELVIEW)
#     glLoadIdentity()
#
#     if not is_paused:
#         for point in points:
#             point.update()
#
#     if is_black_screen:
#         glColor3f(0, 0, 0)
#         glBegin(GL_QUADS)
#         glVertex2f(-400, -400)
#         glVertex2f(400, -400)
#         glVertex2f(400, 400)
#         glVertex2f(-400, 400)
#         glEnd()
#     else:
#         for point in points:
#             point.draw()
#
#     glutSwapBuffers()
#
#
# def mouseListener(button, state, x, y):
#     if is_paused:
#         return
#     if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
#         x = x - width / 2
#         y = (height / 2) - y
#         points.append(MovingPoint(x, y))
#     elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
#         global is_black_screen
#         is_black_screen = not is_black_screen
#
#
# def keyboardListener(key, x, y):
#     global speed_multiplier
#     if key == b'\x1b':
#         glutLeaveMainLoop()
#     elif key == b' ':
#         toggle_pause()
#
#
# def KeyListener(key, x, y):
#     global speed_multiplier
#     if not is_paused:
#         if key == GLUT_KEY_UP:
#             speed_multiplier = min(speed_multiplier + 0.5, max_speed)
#         elif key == GLUT_KEY_DOWN:
#             speed_multiplier = max(speed_multiplier - 0.5, 0.5)
#
#
# def animate():
#     glutPostRedisplay()
#
#
# glutInit()
# glutInitDisplayMode(GLUT_RGBA)
# glutInitWindowSize(width, height)
# glutInitWindowPosition(250, 150)
# wind = glutCreateWindow(b"Part_2")
# glutDisplayFunc(Show)
# glutIdleFunc(animate)
# glutMouseFunc(mouseListener)
# glutSpecialFunc(KeyListener)
# glutKeyboardFunc(keyboardListener)
# glutMainLoop()
