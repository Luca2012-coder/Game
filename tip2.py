import streamlit as st
import time

# ================= STATS =================
if "money" not in st.session_state:
    st.session_state.money = 0
if "money_per_click" not in st.session_state:
    st.session_state.money_per_click = 1
if "money_per_second" not in st.session_state:
    st.session_state.money_per_second = 0
if "prestige" not in st.session_state:
    st.session_state.prestige = 0
if "weapon_level" not in st.session_state:
    st.session_state.weapon_level = 0
if "bonus_cooldown" not in st.session_state:
    st.session_state.bonus_cooldown = 0
if "achievements" not in st.session_state:
    st.session_state.achievements = {
        "100 geld": False,
        "1000 geld": False,
        "10 per seconde": False
    }

# ================= WAPENS =================
weapon_names = ["Abel's Punch", "Kartonnen Pistol", "Metaal Pistol", "Final Boss Debie"]
weapon_click_values = [1, 25, 50, 100000]
weapon_prices = [0, 100, 500, 500000]

# ================= FUNCTIES =================
def click_weapon():
    st.session_state.money += st.session_state.money_per_click * (1 + st.session_state.prestige)

def buy_click_upgrade():
    if st.session_state.money >= 10:
        st.session_state.money -= 10
        st.session_state.money_per_click += 1

def buy_auto_upgrade():
    if st.session_state.money >= 25:
        st.session_state.money -= 25
        st.session_state.money_per_second += 1

def buy_weapon():
    lvl = st.session_state.weapon_level + 1
    if lvl < len(weapon_names) and st.session_state.money >= weapon_prices[lvl]:
        st.session_state.money -= weapon_prices[lvl]
        st.session_state.weapon_level = lvl
        st.session_state.money_per_click = weapon_click_values[lvl]

def bonus_money():
    if st.session_state.bonus_cooldown <= 0:
        st.session_state.money += 50 * (1 + st.session_state.prestige)
        st.session_state.bonus_cooldown = 10  # cooldown in sec

def do_prestige():
    if st.session_state.money >= 1000:
        st.session_state.prestige += 1
        st.session_state.money = 0
        st.session_state.money_per_click = 1
        st.session_state.money_per_second = 0
        st.session_state.weapon_level = 0

def update_achievements():
    if st.session_state.money >= 100:
        st.session_state.achievements["100 geld"] = True
    if st.session_state.money >= 1000:
        st.session_state.achievements["1000 geld"] = True
    if st.session_state.money_per_second >= 10:
        st.session_state.achievements["10 per seconde"] = True

# ================= LAYOUT =================
st.title("📦 Kartonnen Wapen Clicker")

# Toon geld en stats
st.write(f"**Geld:** €{int(st.session_state.money)}")
st.write(f"**Klik per klik:** €{st.session_state.money_per_click}")
st.write(f"**Per seconde:** €{st.session_state.money_per_second}")
st.write(f"**Prestige multiplier:** x{1 + st.session_state.prestige}")
st.write(f"**Huidig wapen:** {weapon_names[st.session_state.weapon_level]}")

# Klik weapon
if st.button("Klik op Wapen!"):
    click_weapon()

# Shop upgrades
st.subheader("Shop")
cols = st.columns(2)

with cols[0]:
    if st.button("Klik upgrade (+1 per klik, €10)"):
        buy_click_upgrade()
with cols[1]:
    if st.button("Auto geld (+1/sec, €25)"):
        buy_auto_upgrade()

# Weapon upgrade
lvl = st.session_state.weapon_level + 1
if lvl < len(weapon_names):
    if st.button(f"Koop {weapon_names[lvl]} (€{weapon_prices[lvl]}, {weapon_click_values[lvl]} per klik)"):
        buy_weapon()

# Bonus
if st.button("Bonus geld (+50, 10s cooldown)"):
    bonus_money()

# Prestige
if st.button("Prestige (reset vanaf €1000)"):
    do_prestige()

# Achievements
st.subheader("Achievements")
for name, done in st.session_state.achievements.items():
    st.write(f"{'✔' if done else '✖'} {name}")

# ================= AUTO-GELD =================
# update geld automatisch elke 0.1 sec
def auto_increment():
    st.session_state.money += st.session_state.money_per_second * (1 + st.session_state.prestige) * 0.1
    if st.session_state.bonus_cooldown > 0:
        st.session_state.bonus_cooldown -= 0.1
    update_achievements()

auto_increment()
time.sleep(0.1)
st.experimental_rerun()
