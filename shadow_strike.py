"""
SHADOW STRIKE: LAST SURVIVOR
A self-contained 2D platform shooter made with Python + Pygame.
Install:  py -m pip install pygame
Run:      py shadow_strike.py

Controls
--------
A / D or Left / Right : Move
W / Up / Space        : Jump
Mouse Left or J       : Shoot
R                     : Reload
ESC / P                : Pause
Enter                 : Start / restart
F                     : Toggle fullscreen
"""

import math
import random
import sys
from dataclasses import dataclass

import pygame

pygame.init()
pygame.mixer.quit()  # The game works even if no audio device is available.

WIDTH, HEIGHT = 1100, 650
FPS = 60
GROUND_Y = 535
WORLD_W = 2200
GRAVITY = 1800
PLAYER_SPEED = 330
JUMP_SPEED = 690
MAG_SIZE = 24
RELOAD_TIME = 1.15

# Palette
BG = (9, 14, 29)
DARK = (13, 22, 41)
PANEL = (10, 20, 39)
BLUE = (55, 173, 255)
CYAN = (69, 244, 224)
WHITE = (235, 244, 255)
MUTED = (145, 168, 196)
RED = (255, 74, 94)
ORANGE = (255, 166, 62)
GREEN = (65, 231, 164)
PURPLE = (176, 104, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHADOW STRIKE: Last Survivor")
clock = pygame.time.Clock()

def font(size, bold=False):
    return pygame.font.SysFont("consolas", size, bold=bold)

F_SMALL = font(15)
F_MED = font(20, True)
F_BIG = font(44, True)
F_TITLE = font(62, True)

def clamp(value, lo, hi):
    return max(lo, min(hi, value))

def draw_text(surface, text, x, y, f=F_SMALL, color=WHITE, center=False):
    img = f.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    surface.blit(img, rect)
    return rect

def panel(surface, rect, fill=PANEL, border=(37, 89, 137), radius=12, width=2):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, width, border_radius=radius)

def draw_bar(surface, x, y, w, h, ratio, color, back=(34, 48, 69)):
    pygame.draw.rect(surface, back, (x, y, w, h), border_radius=h//2)
    if ratio > 0:
        pygame.draw.rect(surface, color, (x, y, int(w*clamp(ratio, 0, 1)), h), border_radius=h//2)

@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    damage: int = 25
    life: float = 1.4
    friendly: bool = True

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: tuple
    size: float

class Player:
    def __init__(self):
        self.x = 220.0
        self.y = GROUND_Y - 62
        self.w, self.h = 36, 62
        self.vx = self.vy = 0.0
        self.health = 100
        self.max_health = 100
        self.facing = 1
        self.grounded = True
        self.anim = 0.0
        self.shoot_flash = 0.0
        self.invuln = 0.0
        self.ammo = MAG_SIZE
        self.reserve = 144
        self.reload = 0.0
        self.coins = 0
        self.kills = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y), self.w, self.h)

    def jump(self):
        if self.grounded:
            self.vy = -JUMP_SPEED
            self.grounded = False

    def reload_gun(self):
        if self.reload <= 0 and self.ammo < MAG_SIZE and self.reserve > 0:
            self.reload = RELOAD_TIME

    def update(self, dt, keys, world_mouse=None):
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += PLAYER_SPEED
        if self.vx:
            self.facing = 1 if self.vx > 0 else -1
            self.anim += dt * 11
        else:
            self.anim += dt * 2
        self.x = clamp(self.x + self.vx*dt, 35, WORLD_W-35)
        self.vy += GRAVITY*dt
        self.y += self.vy*dt
        if self.y + self.h >= GROUND_Y:
            self.y = GROUND_Y-self.h
            self.vy = 0
            self.grounded = True
        self.shoot_flash = max(0, self.shoot_flash-dt)
        self.invuln = max(0, self.invuln-dt)
        if self.reload > 0:
            self.reload -= dt
            if self.reload <= 0:
                need = MAG_SIZE-self.ammo
                take = min(need, self.reserve)
                self.ammo += take
                self.reserve -= take
                self.reload = 0

    def draw(self, surface, cam_x, shake_x=0, shake_y=0):
        sx = int(self.x-cam_x+shake_x)
        sy = int(self.y+shake_y)
        if self.invuln > 0 and int(self.invuln*18) % 2 == 0:
            return
        # Shadow
        pygame.draw.ellipse(surface, (4, 8, 17), (sx-24, GROUND_Y-9+shake_y, 48, 12))
        bob = int(math.sin(self.anim)*2) if self.grounded else 0
        # Legs
        leg_swing = int(math.sin(self.anim)*5) if abs(self.vx) > 1 else 0
        hip_y = sy+43+bob
        pygame.draw.line(surface, (27, 37, 58), (sx-7, hip_y), (sx-10+leg_swing, sy+59), 9)
        pygame.draw.line(surface, (27, 37, 58), (sx+7, hip_y), (sx+10-leg_swing, sy+59), 9)
        pygame.draw.line(surface, (76, 94, 122), (sx-10+leg_swing, sy+59), (sx-2+leg_swing, sy+60), 6)
        pygame.draw.line(surface, (76, 94, 122), (sx+10-leg_swing, sy+59), (sx+18-leg_swing, sy+60), 6)
        # Body / tactical jacket
        body = pygame.Rect(sx-15, sy+20+bob, 30, 28)
        pygame.draw.rect(surface, (29, 48, 75), body, border_radius=7)
        pygame.draw.rect(surface, (53, 88, 125), body, 2, border_radius=7)
        pygame.draw.line(surface, CYAN, (sx, sy+24+bob), (sx, sy+42+bob), 2)
        pygame.draw.rect(surface, (20, 31, 50), (sx-14, sy+31+bob, 8, 12), border_radius=2)
        # Neck and head
        pygame.draw.rect(surface, (177, 119, 87), (sx-5, sy+15+bob, 10, 9))
        pygame.draw.ellipse(surface, (205, 153, 118), (sx-12, sy+1+bob, 24, 22))
        # Hair and eye
        if self.facing > 0:
            pygame.draw.polygon(surface, (23, 27, 43), [(sx-13,sy+10+bob),(sx-10,sy+1+bob),(sx+3,sy-2+bob),(sx+12,sy+5+bob),(sx+9,sy+10+bob),(sx-2,sy+7+bob)])
            pygame.draw.circle(surface, (23, 34, 48), (sx+6, sy+11+bob), 2)
        else:
            pygame.draw.polygon(surface, (23, 27, 43), [(sx+13,sy+10+bob),(sx+10,sy+1+bob),(sx-3,sy-2+bob),(sx-12,sy+5+bob),(sx-9,sy+10+bob),(sx+2,sy+7+bob)])
            pygame.draw.circle(surface, (23, 34, 48), (sx-6, sy+11+bob), 2)
        # Arms and rifle
        shoulder = (sx+self.facing*8, sy+27+bob)
        hand = (sx+self.facing*18, sy+31+bob)
        pygame.draw.line(surface, (177, 119, 87), shoulder, hand, 6)
        gun_start = (sx+self.facing*7, sy+29+bob)
        gun_end = (sx+self.facing*34, sy+27+bob)
        pygame.draw.line(surface, (27, 35, 48), gun_start, gun_end, 7)
        pygame.draw.line(surface, (104, 133, 162), gun_start, gun_end, 2)
        pygame.draw.line(surface, (27, 35, 48), (sx+self.facing*18,sy+30+bob), (sx+self.facing*17,sy+38+bob), 4)
        if self.shoot_flash > 0:
            tipx = sx+self.facing*38
            tipy = sy+27+bob
            pygame.draw.polygon(surface, ORANGE, [(tipx,tipy),(tipx+self.facing*19,tipy-7),(tipx+self.facing*13,tipy),(tipx+self.facing*19,tipy+7)])
            pygame.draw.circle(surface, (255, 231, 148), (tipx,tipy), 5)

class Enemy:
    def __init__(self, x, kind=0, wave=1):
        self.x = float(x)
        self.kind = kind
        self.w = 36 if kind == 0 else 44
        self.h = 48 if kind == 0 else 58
        self.y = GROUND_Y-self.h
        self.max_hp = (45 if kind == 0 else 95) + wave*3
        self.hp = self.max_hp
        self.speed = (105 if kind == 0 else 64) + min(wave*3, 45)
        self.damage = 9 if kind == 0 else 15
        self.attack_cd = random.uniform(.2, .8)
        self.anim = random.random()*6
        self.flash = 0
        self.facing = 1
        self.dead = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y), self.w, self.h)

    def update(self, dt, player, enemy_bullets, particles):
        self.anim += dt*7
        self.flash = max(0, self.flash-dt)
        direction = 1 if player.x > self.x else -1
        self.facing = direction
        dist = abs(player.x-self.x)
        if self.kind == 1 and dist < 360:
            self.attack_cd -= dt
            if self.attack_cd <= 0:
                self.attack_cd = random.uniform(1.5, 2.2)
                dx = player.x-self.x
                dy = (player.y+25)-(self.y+25)
                length = max(1, math.hypot(dx, dy))
                enemy_bullets.append(Bullet(self.x, self.y+24, dx/length*330, 12, 2.5, False))
                enemy_bullets[-1].vy = dy/length*330
        else:
            self.x += direction*self.speed*dt
        if dist < (self.w+player.w)/2+3 and player.invuln <= 0:
            player.health -= self.damage*dt
            player.invuln = .12
            for _ in range(2):
                particles.append(Particle(player.x, player.y+28, random.uniform(-100,100), random.uniform(-150,-30), .3, .3, RED, 3))

    def draw(self, surface, cam_x, shake_x=0, shake_y=0):
        sx, sy = int(self.x-cam_x+shake_x), int(self.y+shake_y)
        col = PURPLE if self.kind == 1 else (139, 66, 79)
        edge = (255, 114, 126) if self.kind == 0 else (211, 136, 255)
        bob = int(math.sin(self.anim)*2)
        pygame.draw.ellipse(surface, (4, 8, 17), (sx-23, GROUND_Y-8+shake_y, 46, 10))
        # Limbs
        pygame.draw.line(surface, (49, 38, 55), (sx-8,sy+31+bob), (sx-11,sy+self.h-2), 8)
        pygame.draw.line(surface, (49, 38, 55), (sx+8,sy+31+bob), (sx+11,sy+self.h-2), 8)
        pygame.draw.rect(surface, col, (sx-15,sy+14+bob,30,self.h-23), border_radius=6)
        pygame.draw.rect(surface, edge, (sx-15,sy+14+bob,30,self.h-23), 2, border_radius=6)
        pygame.draw.circle(surface, (62, 49, 64), (sx,sy+10+bob), 13)
        # Glowing eyes
        pygame.draw.circle(surface, RED, (sx-5,sy+10+bob), 3)
        pygame.draw.circle(surface, RED, (sx+5,sy+10+bob), 3)
        pygame.draw.line(surface, (30, 29, 42), (sx+self.facing*8,sy+23+bob), (sx+self.facing*20,sy+29+bob), 5)
        if self.flash > 0:
            pygame.draw.circle(surface, WHITE, (sx,sy+20), 18, 2)
        # HP bar
        bw = 42
        pygame.draw.rect(surface, (34, 25, 42), (sx-bw//2, sy-12, bw, 5), border_radius=2)
        pygame.draw.rect(surface, RED if self.kind == 0 else PURPLE, (sx-bw//2, sy-12, int(bw*max(0,self.hp/self.max_hp)), 5), border_radius=2)

def make_particles(particles, x, y, color, count=12, power=220):
    for _ in range(count):
        angle = random.random()*math.tau
        speed = random.uniform(power*.25, power)
        life = random.uniform(.18, .6)
        particles.append(Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed, life, life, color, random.uniform(2,4)))

def draw_background(surface, cam_x, time_now):
    surface.fill(BG)
    # Stars
    for i in range(65):
        x = (i*173 - int(cam_x*.13)) % (WIDTH+20)
        y = (i*71+31) % 280
        brightness = 95 + int(35*(.5+.5*math.sin(time_now*1.2+i)))
        pygame.draw.circle(surface, (brightness, brightness+8, min(255,brightness+30)), (x,y), 1)
    # Moon
    pygame.draw.circle(surface, (48, 76, 115), (840-int(cam_x*.04), 115), 58)
    pygame.draw.circle(surface, (78, 109, 150), (828-int(cam_x*.04), 105), 49)
    # Distant city silhouettes
    for layer, color, base, factor in [
        (0,(18,31,56),420,.12),(1,(15,26,47),465,.24),(2,(12,22,40),500,.38)
    ]:
        x = -int(cam_x*factor) % 240
        idx = -1
        while x < WIDTH+240:
            width = 45 + ((idx*37+layer*19) % 70)
            height = 65 + ((idx*47+layer*31) % 155)
            rect = pygame.Rect(x, base-height, width, height)
            pygame.draw.rect(surface, color, rect)
            if layer == 1:
                for wy in range(rect.top+15, rect.bottom-10, 23):
                    for wx in range(rect.left+9, rect.right-7, 17):
                        if (wx+wy+idx)%3 == 0:
                            pygame.draw.rect(surface, (35,65,95), (wx,wy,4,7))
            x += width+12
            idx += 1
    # Ground / platform
    pygame.draw.rect(surface, (22,35,51), (0, GROUND_Y, WIDTH, HEIGHT-GROUND_Y))
    pygame.draw.rect(surface, (50,72,86), (0, GROUND_Y, WIDTH, 9))
    pygame.draw.line(surface, CYAN, (0,GROUND_Y), (WIDTH,GROUND_Y), 2)
    for i in range(28):
        x = (i*93-int(cam_x)) % (WIDTH+50)
        pygame.draw.line(surface, (30,51,68), (x,GROUND_Y+14), (x-25,HEIGHT), 1)
    # Foreground broken railing silhouettes
    for i in range(12):
        x = (i*151-int(cam_x*.9)) % (WIDTH+100)
        pygame.draw.rect(surface, (14,24,38), (x, GROUND_Y-18, 5, 18))
        pygame.draw.line(surface, (14,24,38), (x-20,GROUND_Y-18),(x+30,GROUND_Y-18),3)

def draw_hud(surface, player, score, wave, combo, elapsed):
    # top panels
    panel(surface, (18,16,290,92), (9,18,35), (37,93,147), 12)
    draw_text(surface, "SURVIVOR", 34, 25, F_SMALL, CYAN)
    draw_text(surface, f"{int(max(0,player.health)):03d} / 100", 34, 45, F_MED, WHITE)
    draw_bar(surface, 34, 75, 245, 13, player.health/player.max_health, GREEN if player.health>35 else RED)
    panel(surface, (430,16,240,76), (9,18,35), (37,93,147), 12)
    draw_text(surface, "SCORE", 450, 25, F_SMALL, CYAN)
    draw_text(surface, f"{score:08d}", 450, 45, F_BIG, WHITE)
    panel(surface, (816,16,266,92), (9,18,35), (37,93,147), 12)
    draw_text(surface, "RIFLE  //  AUTO", 834, 25, F_SMALL, CYAN)
    draw_text(surface, f"{player.ammo:02d}", 834, 45, F_BIG, WHITE)
    draw_text(surface, f"/ {player.reserve:03d} RESERVE", 898, 61, F_SMALL, MUTED)
    draw_bar(surface, 834, 84, 220, 7, player.ammo/MAG_SIZE, ORANGE)
    draw_text(surface, f"WAVE {wave:02d}", 25, 124, F_MED, WHITE)
    draw_text(surface, f"ELIMINATIONS {player.kills:03d}", 25, 151, F_SMALL, MUTED)
    draw_text(surface, f"COINS {player.coins:03d}", WIDTH-150, 124, F_MED, ORANGE)
    if combo > 1:
        draw_text(surface, f"{combo}x COMBO", WIDTH//2, 118, F_MED, ORANGE, True)
    if player.reload > 0:
        draw_text(surface, "RELOADING...", WIDTH-145, 151, F_SMALL, CYAN)
        draw_bar(surface, WIDTH-145, 171, 110, 5, 1-player.reload/RELOAD_TIME, CYAN)
    draw_text(surface, f"TIME {int(elapsed//60):02d}:{int(elapsed%60):02d}", WIDTH-130, HEIGHT-28, F_SMALL, MUTED)

def button(surface, rect, label, selected=False):
    color = (18, 46, 76) if selected else (12, 25, 46)
    border = CYAN if selected else (47, 83, 119)
    pygame.draw.rect(surface, color, rect, border_radius=9)
    pygame.draw.rect(surface, border, rect, 2, border_radius=9)
    draw_text(surface, label, rect.centerx, rect.centery, F_MED, WHITE, True)

def draw_menu(surface, best_score, paused=False, game_over=False):
    overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    overlay.fill((3,7,17,205))
    surface.blit(overlay,(0,0))
    box = pygame.Rect(WIDTH//2-280, 100, 560, 450)
    panel(surface, box, (8,17,35), (48,143,205), 20, 2)
    draw_text(surface, "SHADOW STRIKE", WIDTH//2, 155, F_TITLE, WHITE, True)
    draw_text(surface, "LAST SURVIVOR  //  PROTOCOL 09", WIDTH//2, 203, F_SMALL, CYAN, True)
    if game_over:
        draw_text(surface, "MISSION FAILED", WIDTH//2, 255, F_BIG, RED, True)
        draw_text(surface, f"FINAL SCORE  {game_over[0]:08d}", WIDTH//2, 300, F_MED, WHITE, True)
        draw_text(surface, f"ELIMINATIONS  {game_over[1]}     WAVE  {game_over[2]}", WIDTH//2, 331, F_SMALL, MUTED, True)
        button(surface, pygame.Rect(WIDTH//2-125, 365, 250, 48), "PLAY AGAIN  [ENTER]", True)
    elif paused:
        draw_text(surface, "GAME PAUSED", WIDTH//2, 263, F_BIG, WHITE, True)
        button(surface, pygame.Rect(WIDTH//2-125, 320, 250, 48), "RESUME  [P / ESC]", True)
        button(surface, pygame.Rect(WIDTH//2-125, 380, 250, 48), "RESTART  [ENTER]")
    else:
        draw_text(surface, "SURVIVE THE INCOMING WAVES", WIDTH//2, 257, F_MED, WHITE, True)
        button(surface, pygame.Rect(WIDTH//2-125, 310, 250, 52), "START MISSION  [ENTER]", True)
        draw_text(surface, "A / D MOVE     W / SPACE JUMP     MOUSE / J SHOOT", WIDTH//2, 391, F_SMALL, MUTED, True)
        draw_text(surface, "R RELOAD     P / ESC PAUSE     F FULLSCREEN", WIDTH//2, 417, F_SMALL, MUTED, True)
        draw_text(surface, "TIP: Keep moving. Heavy enemies fire back.", WIDTH//2, 456, F_SMALL, ORANGE, True)
    draw_text(surface, f"PERSONAL BEST  {best_score:08d}", WIDTH//2, 510, F_SMALL, CYAN, True)

def reset_game():
    return {
        "player": Player(), "bullets": [], "enemy_bullets": [], "enemies": [],
        "particles": [], "coins": [], "score": 0, "wave": 1, "wave_timer": 0,
        "spawn_timer": 1.0, "cam_x": 0.0, "shake": 0.0, "shake_power": 0.0,
        "elapsed": 0.0, "combo": 0, "combo_timer": 0.0, "started": False,
        "paused": False, "over": None, "toast": "", "toast_timer": 0.0,
    }

game = reset_game()
best_score = 0
fullscreen = False
running = True
shoot_held = False
last_shot = 0.0
time_now = 0.0

def spawn_enemy(g):
    p = g["player"]
    side = random.choice([-1,1])
    x = p.x + side*random.randint(500,760)
    x = clamp(x, 35, WORLD_W-35)
    wave = g["wave"]
    kind = 1 if wave >= 3 and random.random() < min(.18 + wave*.025, .45) else 0
    g["enemies"].append(Enemy(x, kind, wave))

while running:
    dt = min(clock.tick(FPS)/1000, .033)
    time_now += dt
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    shoot_input = mouse_buttons[0] or keys[pygame.K_j]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    WIDTH, HEIGHT = screen.get_size()
                    GROUND_Y = int(HEIGHT*.82)
                else:
                    WIDTH, HEIGHT, GROUND_Y = 1100, 650, 535
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                # Keep the game world playable after display changes.
                game["player"].y = min(game["player"].y, GROUND_Y-game["player"].h)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not game["started"] or game["over"] or game["paused"]:
                    game = reset_game()
                    game["started"] = True
            elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                if game["started"] and not game["over"]:
                    game["paused"] = not game["paused"]
            elif event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                if game["started"] and not game["paused"] and not game["over"]:
                    game["player"].jump()
            elif event.key == pygame.K_r:
                if game["started"] and not game["paused"] and not game["over"]:
                    game["player"].reload_gun()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shoot_held = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            shoot_held = False

    g = game
    if g["started"] and not g["paused"] and not g["over"]:
        p = g["player"]
        g["elapsed"] += dt
        p.update(dt, keys)
        g["cam_x"] = clamp(p.x-WIDTH*.42, 0, WORLD_W-WIDTH)
        g["spawn_timer"] -= dt
        if g["spawn_timer"] <= 0:
            spawn_enemy(g)
            g["spawn_timer"] = max(.42, random.uniform(1.05,1.65)-g["wave"]*.045)
        g["wave_timer"] += dt
        if g["wave_timer"] >= 22:
            g["wave_timer"] = 0
            g["wave"] += 1
            g["toast"] = f"WAVE {g['wave']} // HOSTILES INBOUND"
            g["toast_timer"] = 2.1
            p.reserve = min(240, p.reserve+24)
            p.health = min(100, p.health+8)

        # Shoot toward the direction the character faces. This keeps keyboard play consistent.
        last_shot -= dt
        if shoot_input and p.reload <= 0 and last_shot <= 0:
            if p.ammo > 0:
                p.ammo -= 1
                p.shoot_flash = .075
                last_shot = .115
                muzzle_x = p.x+p.facing*38
                muzzle_y = p.y+27
                g["bullets"].append(Bullet(muzzle_x, muzzle_y, p.facing*850, 25, 1.3, True))
                g["shake"] = max(g["shake"], .12)
                g["shake_power"] = max(g["shake_power"], 3.5)
                make_particles(g["particles"], muzzle_x, muzzle_y, ORANGE, 4, 90)
            else:
                p.reload_gun()
                g["toast"] = "OUT OF AMMO — RELOADING"
                g["toast_timer"] = 1.2

        # Bullets update and collide
        for b in g["bullets"][:]:
            b.x += b.vx*dt
            b.life -= dt
            hit = None
            for enemy in g["enemies"]:
                if not enemy.dead and enemy.rect.collidepoint(int(b.x), int(b.y)):
                    hit = enemy
                    break
            if hit:
                hit.hp -= b.damage
                hit.flash = .12
                make_particles(g["particles"], b.x, b.y, ORANGE, 5, 130)
                if hit.hp <= 0 and not hit.dead:
                    hit.dead = True
                    p.kills += 1
                    g["score"] += 100 if hit.kind == 0 else 250
                    g["combo"] += 1
                    g["combo_timer"] = 2.4
                    if g["combo"] % 5 == 0:
                        g["score"] += 250
                        g["toast"] = f"{g['combo']} KILL STREAK  +250"
                        g["toast_timer"] = 1.4
                    make_particles(g["particles"], hit.x, hit.y+20, RED, 18, 250)
                    if random.random() < .36:
                        g["coins"].append([hit.x, GROUND_Y-25, random.uniform(0,math.tau)])
                    g["shake"] = max(g["shake"], .18)
                    g["shake_power"] = max(g["shake_power"], 5)
                g["bullets"].remove(b)
            elif b.life <= 0 or b.x < 0 or b.x > WORLD_W:
                g["bullets"].remove(b)

        # Enemy projectiles
        for b in g["enemy_bullets"][:]:
            b.x += b.vx*dt
            b.y += getattr(b,"vy",0)*dt
            b.life -= dt
            if p.rect.collidepoint(int(b.x),int(b.y)) and p.invuln <= 0:
                p.health -= b.damage
                p.invuln = .5
                g["shake"] = max(g["shake"], .24)
                g["shake_power"] = max(g["shake_power"], 8)
                make_particles(g["particles"], p.x, p.y+25, RED, 10, 180)
                g["enemy_bullets"].remove(b)
            elif b.life <= 0 or abs(b.x-p.x)>WIDTH*1.5:
                g["enemy_bullets"].remove(b)

        for enemy in g["enemies"]:
            enemy.update(dt, p, g["enemy_bullets"], g["particles"])
        g["enemies"] = [e for e in g["enemies"] if not e.dead and abs(e.x-p.x)<WIDTH*1.8]

        # Coins / pickups
        for coin in g["coins"][:]:
            coin[2] += dt*5
            if abs(coin[0]-p.x)<30 and abs(coin[1]-(p.y+30))<55:
                p.coins += 1
                g["score"] += 50
                p.health = min(100,p.health+2)
                g["coins"].remove(coin)
                make_particles(g["particles"],coin[0],coin[1],ORANGE,8,100)
            elif abs(coin[0]-p.x)>WIDTH*1.8:
                g["coins"].remove(coin)

        for part in g["particles"][:]:
            part.x += part.vx*dt
            part.y += part.vy*dt
            part.vy += 450*dt
            part.life -= dt
            if part.life <= 0:
                g["particles"].remove(part)

        g["combo_timer"] -= dt
        if g["combo_timer"] <= 0:
            g["combo"] = 0
        g["toast_timer"] = max(0,g["toast_timer"]-dt)
        g["shake"] = max(0,g["shake"]-dt)
        if p.health <= 0:
            p.health = 0
            g["over"] = (g["score"],p.kills,g["wave"])
            best_score = max(best_score,g["score"])
    else:
        # Particles continue to fade on the title screen / pause screen.
        for part in g["particles"][:]:
            part.life -= dt
            if part.life <= 0:
                g["particles"].remove(part)

    # Render scene with camera shake.
    sx = sy = 0
    if g["shake"] > 0:
        power = g["shake_power"]*(g["shake"]/.24)
        sx = random.randint(-max(1,int(power)),max(1,int(power)))
        sy = random.randint(-max(1,int(power)),max(1,int(power)))
    draw_background(screen,g["cam_x"],time_now)
    for coin in g["coins"]:
        cx, cy = int(coin[0]-g["cam_x"]+sx), int(coin[1]+math.sin(coin[2])*5+sy)
        pygame.draw.circle(screen,(110,72,20),(cx,cy),11)
        pygame.draw.circle(screen,ORANGE,(cx,cy),8,2)
        draw_text(screen,"$",cx,cy,F_SMALL,(255,236,155),True)
    for b in g["bullets"]:
        bx,by=int(b.x-g["cam_x"]+sx),int(b.y+sy)
        pygame.draw.line(screen,(255,198,94),(bx,by),(bx-int(math.copysign(13,b.vx)),by),3)
        pygame.draw.circle(screen,WHITE,(bx,by),2)
    for b in g["enemy_bullets"]:
        pygame.draw.circle(screen,PURPLE,(int(b.x-g["cam_x"]+sx),int(b.y+sy)),5)
        pygame.draw.circle(screen,WHITE,(int(b.x-g["cam_x"]+sx),int(b.y+sy)),2)
    for enemy in g["enemies"]:
        enemy.draw(screen,g["cam_x"],sx,sy)
    if g["started"]:
        g["player"].draw(screen,g["cam_x"],sx,sy)
    for part in g["particles"]:
        alpha = clamp(part.life/max(.001,part.max_life),0,1)
        radius = max(1,int(part.size*alpha))
        pygame.draw.circle(screen,part.color,(int(part.x-g["cam_x"]+sx),int(part.y+sy)),radius)
    if g["started"]:
        draw_hud(screen,g["player"],g["score"],g["wave"],g["combo"],g["elapsed"])
        if g["toast_timer"]>0:
            draw_text(screen,g["toast"],WIDTH//2,HEIGHT-70,F_MED,ORANGE,True)
    if not g["started"]:
        draw_menu(screen,best_score)
    elif g["paused"]:
        draw_menu(screen,best_score,paused=True)
    elif g["over"]:
        draw_menu(screen,best_score,game_over=g["over"])
    # Bottom control hint
    if g["started"] and not g["paused"] and not g["over"]:
        draw_text(screen,"A/D MOVE   W/SPACE JUMP   MOUSE/J FIRE   R RELOAD   P PAUSE",WIDTH//2,HEIGHT-8,F_SMALL,(126,154,185),True)
    pygame.display.flip()

pygame.quit()
sys.exit()
