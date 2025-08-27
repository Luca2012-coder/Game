# pacman_mission.py
# A tiny Pac-Man-like daily mission built with pygame.
# This script loads profiles.json, asks/gets a profile name, lets you play,
# and writes your rewards (money/xp) back to the profile. If today's daily
# mission is already completed, rewards are heavily reduced (training mode).
#
# Run locally (cannot run on Streamlit Cloud):
#   pip install pygame
#   python pacman_mission.py --profile "YOUR_NAME"
#
# Controls: Arrow keys to move. Collect coins, avoid guards. 60 seconds timer.

import pygame
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import date, datetime

DATA_FILE = Path("profiles.json")

# ---------------------
# Utility: load/save
# ---------------------

def load_profiles():
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_profiles(obj):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------------------
# Game constants
# ---------------------
TILE = 32
GRID_W, GRID_H = 19, 15
W, H = GRID_W * TILE, GRID_H * TILE
FPS = 60
TIMER_SECONDS = 60
PLAYER_SPEED = 2.5
GUARD_SPEED = 1.8
COIN_COUNT = 25

COL_BG = (15, 15, 22)
COL_WALL = (40, 40, 70)
COL_PLAYER = (240, 210, 0)
COL_GUARD = (210, 50, 50)
COL_COIN = (240, 190, 60)
COL_TEXT = (230, 230, 240)

# Simple random maze: place border walls + some inner blocks

def make_walls():
    walls = set()
    for x in range(GRID_W):
        walls.add((x, 0))
        walls.add((x, GRID_H - 1))
    for y in range(GRID_H):
        walls.add((0, y))
        walls.add((GRID_W - 1, y))
    # inner blocks
    rng = random.Random(42)
    for _ in range(70):
        x = rng.randrange(2, GRID_W - 2)
        y = rng.randrange(2, GRID_H - 2)
        walls.add((x, y))
    return walls


def random_empty_cell(walls, occupied=set()):
    while True:
        x = random.randrange(1, GRID_W - 1)
        y = random.randrange(1, GRID_H - 1)
        if (x, y) not in walls and (x, y) not in occupied:
            return (x, y)


# ---------------------
# Game objects
# ---------------------
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.radius = TILE // 2 - 4

    def update(self, walls):
        # Try moving in x then y with collision against wall tiles
        nx = self.x + self.vx
        ny = self.y + self.vy
        # Collision check by sampling center point -> grid
        gx, gy = int(nx // TILE), int(ny // TILE)
        if (gx, int(self.y // TILE)) not in walls:
            self.x = nx
        if (int(self.x // TILE), gy) not in walls:
            self.y = ny

    def draw(self, surf):
        pygame.draw.circle(surf, COL_PLAYER, (int(self.x), int(self.y)), self.radius)


class Guard:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = GUARD_SPEED
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def update(self, walls, player):
        # Randomly change direction or chase lightly towards player
        if random.random() < 0.02:
            self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        # small bias towards player
        if random.random() < 0.03:
            dx = 1 if player.x > self.x else -1
            dy = 1 if player.y > self.y else -1
            self.dir = random.choice([(dx,0),(0,dy)])
        nx = self.x + self.dir[0]*self.speed
        ny = self.y + self.dir[1]*self.speed
        gx, gy = int(nx // TILE), int(ny // TILE)
        if (gx, int(self.y // TILE)) not in walls:
            self.x = nx
        else:
            self.dir = (-self.dir[0], self.dir[1])
        if (int(self.x // TILE), gy) not in walls:
            self.y = ny
        else:
            self.dir = (self.dir[0], -self.dir[1])

    def draw(self, surf):
        r = TILE//2 - 6
        pygame.draw.rect(surf, COL_GUARD, pygame.Rect(int(self.x)-r, int(self.y)-r, r*2, r*2))


# ---------------------
# Drawing helpers
# ---------------------

def draw_grid(surf, walls):
    surf.fill(COL_BG)
    for (x, y) in walls:
        pygame.draw.rect(surf, COL_WALL, pygame.Rect(x*TILE, y*TILE, TILE, TILE))


def draw_text(surf, font, text, x, y):
    img = font.render(text, True, COL_TEXT)
    surf.blit(img, (x, y))


# ---------------------
# Rewards logic
# ---------------------

def apply_rewards(profile, coins_collected):
    today = date.today().isoformat()
    # base reward per coin
    base_money = 5
    base_xp = 3
    money = coins_collected * base_money
    xp = coins_collected * base_xp

    # Daily mission check
    if profile.get("last_mission_date") == today:
        # training mode — reduce to near zero
        money = int(money * 0.1)
        xp = int(xp * 0.1)
        mode = "training"
    else:
        # mark daily mission complete (better payout)
        profile["last_mission_date"] = today
        # small success bonus
        money = int(money * 1.5)
        xp = int(xp * 1.5)
        mode = "daily"

    profile["money"] = profile.get("money", 0) + money
    profile["xp"] = profile.get("xp", 0) + xp
    profile.setdefault("history", []).append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": f"Pacman missie ({mode}): +€{money}, +{xp} XP (munten: {coins_collected})"
    })

    # level calc to roughly match Streamlit app
    profile["level"] = 1 + profile["xp"] // 150

    return money, xp, mode


# ---------------------
# Main game
# ---------------------

def main(profile_name: str):
    profiles = load_profiles()
    if profile_name not in profiles:
        print(f"Profiel '{profile_name}' niet gevonden in profiles.json. Maak eerst een profiel in de Streamlit app.")
        return
    profile = profiles[profile_name]

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("La Famiglia – Pacman Missie")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    walls = make_walls()
    # Place player
    px, py = random_empty_cell(walls)
    player = Player(px*TILE + TILE/2, py*TILE + TILE/2)

    # Guards
    guards = []
    for _ in range(4):
        gx, gy = random_empty_cell(walls)
        guards.append(Guard(gx*TILE + TILE/2, gy*TILE + TILE/2))

    # Coins
    coins = set()
    occupied = set(walls)
    for _ in range(COIN_COUNT):
        cx, cy = random_empty_cell(walls, occupied)
        coins.add((cx, cy))
        occupied.add((cx, cy))

    start_ticks = pygame.time.get_ticks()
    coins_collected = 0
    alive = True

    # Key handling state (smooth movement)
    held = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in held:
                    held[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in held:
                    held[event.key] = False

        # movement vector
        vx = (held[pygame.K_RIGHT] - held[pygame.K_LEFT]) * PLAYER_SPEED * TILE * dt
        vy = (held[pygame.K_DOWN] - held[pygame.K_UP]) * PLAYER_SPEED * TILE * dt
        player.vx, player.vy = vx, vy

        if alive:
            player.update(walls)
            for g in guards:
                g.update(walls, player)

            # collisions
            pr = TILE//2 - 4
            for g in guards:
                if abs(player.x - g.x) < pr and abs(player.y - g.y) < pr:
                    alive = False
                    break

            # coin collection
            pgx, pgy = int(player.x // TILE), int(player.y // TILE)
            if (pgx, pgy) in coins:
                coins.remove((pgx, pgy))
                coins_collected += 1

        # time
        seconds = TIMER_SECONDS - (pygame.time.get_ticks() - start_ticks) / 1000.0
        if seconds <= 0:
            seconds = 0
            alive = False

        # draw
        draw_grid(screen, walls)
        # draw coins
        for (cx, cy) in coins:
            pygame.draw.circle(screen, COL_COIN, (cx*TILE + TILE//2, cy*TILE + TILE//2), 6)
        # draw guards & player
        for g in guards:
            g.draw(screen)
        player.draw(screen)

        draw_text(screen, font, f"Munten: {coins_collected}", 8, 6)
        draw_text(screen, font, f"Tijd: {int(seconds)}", 8, 24)
        draw_text(screen, font, f"Profiel: {profile_name}", 8, 42)

        if not alive:
            # end screen
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))

            if seconds > 0:
                msg = "Gepakt!"  # caught
            else:
                msg = "Tijd voorbij"

            draw_text(screen, font, msg + " — druk op ENTER om af te ronden", 40, H//2 - 20)
            pygame.display.flip()

            # wait for enter, then apply rewards
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit(0)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False
                clock.tick(30)

            # Rewards depend on daily status
            money, xp, mode = apply_rewards(profile, coins_collected)
            profiles[profile_name] = profile
            save_profiles(profiles)

            # Final screen
            screen.fill(COL_BG)
            draw_text(screen, font, f"Beloning ({mode}): +€{money}, +{xp} XP", 60, H//2 - 10)
            draw_text(screen, font, "Sluit het venster (ESC of close).", 60, H//2 + 14)
            pygame.display.flip()

            # wait for ESC or window close
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit(0)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit(0)
                clock.tick(30)

        pygame.display.flip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, help="Exacte profielnaam zoals in profiles.json")
    args = parser.parse_args()
    try:
        main(args.profile)
    except Exception as e:
        print("Er ging iets mis:", e)
        raise
