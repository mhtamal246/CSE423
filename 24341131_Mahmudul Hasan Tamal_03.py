from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

cam_radius = 600
cam_angle = 0
cam_height = 600
cam_elev = 50
MIN_ELEV_DEG = 15
MAX_ELEV_DEG = 80
fovY = 105

cam_mode = "tp"
BACK_OFFSET = 40
LOOK_DISTANCE = 100
HEAD_HEIGHT = 145

cheat_mode = False
SPIN_SPEED_DEG = 7
cheat_cam_angle = None
gun_follow = False

CHEAT_FIRE_COOLDOWN = 6
cheat_cooldown = 0
AIM_TOLERANCE_DEG = 3

GRID_LENGTH = 600
WALL_THICK = 5
MARGIN_X = 30
MARGIN_FRONT = 57
MARGIN_BACK = 12
enemies = []
player_pos = [0, 0]
player_angle = 0

enemy_scale_factor = 1
enemy_scale_direction = 1
enemy_speed = 0.5

player_health = 5
score = 0
player_dead = False
missed_bullets = 0
BULLET_SPEED = 15
BULLET_SIZE = 7
BULLET_LIFE = 60
bullets = []


def showScreen():
    global score, player_health
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_grid()
    draw_barriers()
    draw_bullets()
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 1)
    glRotatef(player_angle, 0, 0, 1)
    draw_player()
    glPopMatrix()
    for enemy_pos in enemies:
        if player_dead:
            break
        glPushMatrix()
        glTranslatef(enemy_pos[0], enemy_pos[1], 0)
        draw_enemy()
        glPopMatrix()
    draw_text(10, 770, f"Player Life Remaining: {player_health}")
    if player_dead:
        draw_text(10, 740, "GAME OVER!!! press R to restart")
        draw_text(10, 710, " ")
    else:
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {missed_bullets}")
    glutSwapBuffers()


def spawn_enemies():
    global enemies
    enemies = []
    for i in range(5):
        x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        enemies.append((x, y))


def move_enemies_towards_player():
    global player_health, player_dead
    if player_health == 0:
        return
    COLLISION_DIST = 35
    for i in range(len(enemies)):
        ex, ey = enemies[i]
        px, py = player_pos
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        step_x = enemy_speed * dx / dist
        step_y = enemy_speed * dy / dist
        ex += step_x
        ey += step_y
        if dist < COLLISION_DIST and not player_dead:
            player_health -= 1
            if player_health <= 0:
                player_health = 0
                player_dead = True
            print("Player hit! Health:", player_health)
            ex = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            ey = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            if player_health <= 0:
                player_health = 0
        half_margin = 10
        ex = max(-GRID_LENGTH + WALL_THICK + half_margin,
                 min(GRID_LENGTH - WALL_THICK - half_margin, ex))
        ey = max(-GRID_LENGTH + WALL_THICK + half_margin,
                 min(GRID_LENGTH - WALL_THICK - half_margin, ey))
        enemies[i] = (ex, ey)


def spawn_player_bullet():
    rad = math.radians(player_angle + 90)
    spawn_x = player_pos[0] + 20 * math.cos(rad)
    spawn_y = player_pos[1] + 20 * math.sin(rad)
    bullets.append([spawn_x, spawn_y, player_angle, BULLET_LIFE])
    print("Player Bullet Fired!")

def cheat():
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    player_angle = (player_angle + SPIN_SPEED_DEG) % 360
    if cheat_cooldown > 0:
        cheat_cooldown -= 1
    if cheat_cooldown == 0:
        px, py = player_pos
        for ex, ey in enemies:
            angle_to_enemy = (math.degrees(math.atan2(ey - py, ex - px)) - 90) % 360
            diff = min((angle_to_enemy - player_angle) % 360,
                       (player_angle - angle_to_enemy) % 360)
            if diff < AIM_TOLERANCE_DEG:
                spawn_player_bullet()
                cheat_cooldown = CHEAT_FIRE_COOLDOWN
                break

def shrink_expand():
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    enemy_scale_factor += 0.005 * enemy_scale_direction
    if enemy_scale_factor >= 1.2:
        enemy_scale_factor = 1.2
        enemy_scale_direction = -1
    elif enemy_scale_factor <= 0.8:
        enemy_scale_factor = 0.8
        enemy_scale_direction = 1


def animate():
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    if player_dead:
        glutPostRedisplay()
        return

    if cheat_mode:
        cheat()

    shrink_expand()
    move_enemies_towards_player()
    update_bullets()
    glutPostRedisplay()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def third_person_camera():
    rad = math.radians(cam_angle)
    eye_x = cam_radius * math.cos(rad)
    eye_y = cam_radius * math.sin(rad)
    eye_z = cam_radius * math.sin(math.radians(cam_elev))
    gluLookAt(eye_x, eye_y, eye_z,
              0, 0, 0,
              0, 0, 1)

def first_person_camera():
    global player_pos, player_angle, cheat_mode, cheat_cam_angle, gun_follow
    if cheat_mode == True:
        if gun_follow == True:
            view_angle = player_angle
        else:
            view_angle = cheat_cam_angle
    else:
        view_angle = player_angle

    dir_rad = math.radians(view_angle + 90)
    dir_x = math.cos(dir_rad)
    dir_y = math.sin(dir_rad)
    eye_x = player_pos[0] - BACK_OFFSET * dir_x
    eye_y = player_pos[1] - BACK_OFFSET * dir_y
    eye_z = HEAD_HEIGHT
    look_x = player_pos[0] + LOOK_DISTANCE * dir_x
    look_y = player_pos[1] + LOOK_DISTANCE * dir_y
    look_z = HEAD_HEIGHT
    gluLookAt(eye_x, eye_y, eye_z,
              look_x, look_y, look_z,
              0, 0, 1)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if cam_mode == "tp":
        third_person_camera()
    else:
        first_person_camera()


def update_bullets():
    global bullets, enemies, score, missed_bullets, player_health, player_dead
    keep_list = []
    for b in bullets:
        x = b[0]
        y = b[1]
        ang = b[2]
        life = b[3]
        rad = math.radians(ang + 90)
        x = x + BULLET_SPEED * math.cos(rad)
        y = y + BULLET_SPEED * math.sin(rad)
        life = life - 1
        if abs(x) > GRID_LENGTH or abs(y) > GRID_LENGTH or life <= 0:
            missed_bullets = missed_bullets + 1
            print("Player missed bullets:", missed_bullets)
            if missed_bullets >= 10 and not player_dead:
                player_health = 0
                player_dead = True
            continue
        hit_enemy = False
        j = 0
        while j < len(enemies):
            enemy_pos = enemies[j]
            ex = enemy_pos[0]
            ey = enemy_pos[1]
            if math.hypot(x - ex, y - ey) < 28:
                score = score + 1
                rx = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                ry = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                enemies[j] = (rx, ry)
                hit_enemy = True
                break
            j = j + 1
        if not hit_enemy:
            keep_list.append([x, y, ang, life])
    bullets = keep_list


def draw_bullets():
    glColor3f(1, 0, 0)
    for x, y, i, j in bullets:
        glPushMatrix()
        glTranslatef(x, y, BULLET_SIZE / 2)
        glutSolidCube(BULLET_SIZE)
        glPopMatrix()


def draw_enemy():
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glScalef(enemy_scale_factor,
             enemy_scale_factor,
             enemy_scale_factor)
    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), 30, 15, 15)
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()
    glPopMatrix()


def draw_player():
    glPushMatrix()
    if player_dead:
        glColor3f(0, 0, 1)
        glRotatef(-90, 1, 0, 0)
        glTranslatef(0, -40, 0)
    else:
        glColor3f(0, 0, 1)
    glPushMatrix()
    glTranslatef(-20, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 7, 40, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(20, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 7, 40, 10, 10)
    glPopMatrix()
    glTranslatef(0, 0, 40)
    glColor3f(0, 0.6, 0)
    glPushMatrix()
    glScalef(2, 1.2, 2)
    glutSolidCube(20)
    glPopMatrix()
    glColor3f(0.8, 0.8, 0.8)
    glPushMatrix()
    glTranslatef(0, 12, 15)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 4, 45, 10, 10)
    glPopMatrix()
    glColor3f(1, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(-16, 10, 10)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 4, 25, 10, 10)
    glPopMatrix()
    glColor3f(1, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(16, 10, 10)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 4, 25, 10, 10)
    glPopMatrix()
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 37)
    gluSphere(gluNewQuadric(), 12, 10, 10)
    glPopMatrix()
    glPopMatrix()


def draw_barriers():
    wall_thickness = 10
    wall_height = 80
    glPushMatrix()
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH + wall_thickness, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH + wall_thickness, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH + wall_thickness, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH + wall_thickness, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH + wall_thickness, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH + wall_thickness, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH + wall_thickness, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH + wall_thickness, -GRID_LENGTH, 0)
    glEnd()

    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(GRID_LENGTH - wall_thickness, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH - wall_thickness, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH - wall_thickness, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH - wall_thickness, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH - wall_thickness, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH - wall_thickness, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH - wall_thickness, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH - wall_thickness, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH - wall_thickness, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH - wall_thickness, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH - wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH - wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH - wall_thickness, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH - wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH - wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH - wall_thickness, 0)
    glEnd()

    glColor3f(1, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH + wall_thickness, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH + wall_thickness, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH + wall_thickness, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH + wall_thickness, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH + wall_thickness, wall_height)
    glEnd()
    glPopMatrix()


def draw_grid():
    glPushMatrix()
    square_size = 80
    for i in range(-GRID_LENGTH, GRID_LENGTH, square_size):
        for j in range(-GRID_LENGTH, GRID_LENGTH, square_size):
            if (i // square_size + j // square_size) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)
            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i + square_size, j, 0)
            glVertex3f(i + square_size, j + square_size, 0)
            glVertex3f(i, j + square_size, 0)
            glEnd()
    glPopMatrix()

def if_dead():
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    cam_mode = "tp"
    cheat_cam_angle = None
    gun_follow = False
    cheat_mode = False
    player_dead = False
    player_pos[:] = [0, 0]
    player_health = 5
    missed_bullets = 0
    score = 0
    bullets.clear()
    cheat_cooldown = 0
    spawn_enemies()
    return

def cheat_on():
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    cheat_mode = not cheat_mode
    if cheat_mode and cam_mode == "fp":
        cheat_cam_angle = player_angle
    else:
        cheat_cam_angle = None
    return

def keyboardListener(key, x, y):
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    move_speed = 10
    if player_dead:
        if key in (b'r', b'R'):
            if_dead()
            return
        else:
            return

    if key in (b'c', b'C') and not player_dead:
        cheat_on()

    if key in (b'v', b'V') and cheat_mode and cam_mode == "fp":
        gun_follow = not gun_follow
        if gun_follow:
            cheat_cam_angle = None
        else:
            cheat_cam_angle = player_angle
        return


    if key == b'a':
        player_angle = (player_angle + 5) % 360
    elif key == b'd':
        player_angle = (player_angle - 5) % 360
    rad = math.radians(player_angle + 90)
    dx = math.cos(rad) * move_speed
    dy = math.sin(rad) * move_speed

    if key == b'w':
        player_pos[0] += dx
        player_pos[1] += dy

    elif key == b's':
        player_pos[0] -= dx
        player_pos[1] -= dy
    max_x = GRID_LENGTH - WALL_THICK - MARGIN_X
    min_x = -GRID_LENGTH + WALL_THICK + MARGIN_X
    max_y = GRID_LENGTH - WALL_THICK - MARGIN_FRONT
    min_y = -GRID_LENGTH + WALL_THICK + MARGIN_BACK
    player_pos[0] = max(min_x, min(max_x, player_pos[0]))
    player_pos[1] = max(min_y, min(max_y, player_pos[1]))


def specialKeyListener(key, x, y):
    global cam_angle, cam_elev
    if key == GLUT_KEY_LEFT:
        cam_angle = (cam_angle - 2) % 360
    elif key == GLUT_KEY_RIGHT:
        cam_angle = (cam_angle + 2) % 360
    elif key == GLUT_KEY_UP:
        cam_elev = min(cam_elev + 2, MAX_ELEV_DEG)
    elif key == GLUT_KEY_DOWN:
        cam_elev = max(cam_elev - 2, MIN_ELEV_DEG)
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global cam_mode, cheat_mode, cheat_cam_angle, gun_follow
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not player_dead:
        spawn_player_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if cam_mode == "tp":
            cam_mode = "fp"
            if cheat_mode and not gun_follow:
                cheat_cam_angle = player_angle
        else:
            cam_mode = "tp"
            cheat_cam_angle = None
            gun_follow = False
        glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(300, 100)
    glutCreateWindow(b"Boom!!!!")
    glEnable(GL_DEPTH_TEST)
    spawn_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()
