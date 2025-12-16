import json

WIDTH = 900
HEIGHT = 550

# ================= STATS =================
money = 0
money_per_click = 1
money_per_second = 0
prestige = 0

# ================= WAPENS =================
weapon_images = ["abels_punch", "kartonnen_pistol", "metaal_pistol", "karton3"]
weapon_level = 0
weapon = Actor(weapon_images[weapon_level])
weapon.pos = (WIDTH // 2, HEIGHT // 2)

weapon_prices = [0, 100, 500, 500000]  # Upgrade prijs per wapen
weapon_click_values = [1, 25, 50, 100000]  # Geld per klik per wapen

# ================= ANIMATIE =================
weapon.scale = 1
click_timer = 0

# ================= BONUS =================
bonus_timer = 0

# ================= ACHIEVEMENTS =================
achievements = {
    "100 geld": False,
    "1000 geld": False,
    "10 per seconde": False
}

# ================= SAVE =================
def save_game():
    data = {
        "money": money,
        "money_per_click": money_per_click,
        "money_per_second": money_per_second,
        "prestige": prestige,
        "weapon_level": weapon_level,
        "weapon_prices": weapon_prices,
        "weapon_click_values": weapon_click_values,
        "achievements": achievements
    }
    with open("save.json", "w") as f:
        json.dump(data, f)

def load_game():
    global money, money_per_click, money_per_second, prestige
    global weapon_level, weapon_prices, weapon_click_values
    global achievements

    try:
        with open("save.json") as f:
            data = json.load(f)
            money = data["money"]
            money_per_click = data["money_per_click"]
            money_per_second = data["money_per_second"]
            prestige = data["prestige"]
            weapon_level = data["weapon_level"]
            weapon_prices = data["weapon_prices"]
            weapon_click_values = data["weapon_click_values"]
            achievements = data["achievements"]
            weapon.image = weapon_images[weapon_level]
    except:
        pass

load_game()

# ================= GAME =================
def draw():
    screen.clear()
    screen.fill((15, 15, 30))

    weapon.draw()

    # Stats
    screen.draw.text(f"Geld: €{int(money)}", (20, 20), fontsize=40, color="yellow")
    screen.draw.text(f"Klik: €{money_per_click}", (20, 70))
    screen.draw.text(f"/sec: €{money_per_second}", (20, 100))
    screen.draw.text(f"Prestige: x{1+prestige}", (20, 130), color="orange")

    # Shop
    screen.draw.text("SHOP", (650, 20), fontsize=40, color="cyan")
    screen.draw.text(f"[1] Klik +1 (€10)", (600, 80))
    screen.draw.text(f"[2] Auto +1/sec (€25)", (600, 110))

    # Volgend wapen
    next_weapon_level = weapon_level + 1
    if next_weapon_level < len(weapon_images):
        screen.draw.text(
            f"[3] Koop {weapon_images[next_weapon_level].replace('_',' ').title()} (€{weapon_prices[next_weapon_level]}, {weapon_click_values[next_weapon_level]} per klik)",
            (600, 140)
        )

    screen.draw.text("[B] Bonus geld", (600, 180))
    screen.draw.text("[P] Prestige (geld reset)", (600, 210))
    screen.draw.text("[S] Opslaan", (600, 240))

    # Achievements
    y = 300
    screen.draw.text("Achievements:", (20, y))
    for a in achievements:
        status = "✔" if achievements[a] else "✖"
        screen.draw.text(f"{status} {a}", (20, y+25))
        y += 25

def on_mouse_down(pos):
    global money, click_timer
    if weapon.collidepoint(pos):
        money += money_per_click * (1 + prestige)
        weapon.scale = 1.2
        click_timer = 5

def on_key_down(key):
    global money, money_per_click, money_per_second
    global weapon_level, prestige, click_timer, bonus_timer

    # Klik upgrade
    if key == keys.K_1 and money >= 10:
        money -= 10
        money_per_click += 1

    # Auto upgrade
    if key == keys.K_2 and money >= 25:
        money -= 25
        money_per_second += 1

    # Wapen upgrade
    if key == keys.K_3 and weapon_level < len(weapon_images)-1:
        price = weapon_prices[weapon_level+1]
        if money >= price:
            money -= price
            weapon_level += 1
            weapon.image = weapon_images[weapon_level]
            money_per_click = weapon_click_values[weapon_level]

    # Bonus geld
    if key == keys.B and bonus_timer <= 0:
        money += 50 * (1 + prestige)
        bonus_timer = 600  # 10 sec bij 60 fps

    # Prestige
    if key == keys.P and money >= 1000:
        prestige += 1
        money = 0
        money_per_click = 1
        money_per_second = 0
        weapon_level = 0
        weapon.image = weapon_images[0]

    # Opslaan
    if key == keys.S:
        save_game()

def update():
    global money, click_timer, bonus_timer

    # Auto geld
    money += (money_per_second * (1 + prestige)) / 60

    # Animatie terug
    if click_timer > 0:
        click_timer -= 1
    else:
        weapon.scale = 1

    bonus_timer -= 1

    # Achievements
    if money >= 100:
        achievements["100 geld"] = True
    if money >= 1000:
        achievements["1000 geld"] = True
    if money_per_second >= 10:
        achievements["10 per seconde"] = True
