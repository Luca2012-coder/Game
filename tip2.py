import streamlit as st
import time

# ================= INIT =================
def init(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init("money", 0)
init("money_per_click", 1)
init("money_per_second", 0)
init("prestige", 0)
init("weapon_level", 0)
init("bonus_cd", 0)
init("malteser", False)
init("total_clicks", 0)
init("total_upgrades", 0)
init("start_time", time.time())

init("achievements", {
    "100 geld": False,
    "1.000 geld": False,
    "100.000 geld": False,
    "10 per seconde": False,
    "Malteser gekocht": False,
    "Prestige gedaan": False
})

# ================= DATA =================
weapons = [
    ("Abel's Punch", 1, 0),
    ("Kartonnen Pistol", 25, 100),
    ("Metaal Pistol", 50, 500),
    ("Final Boss Debie", 100000, 500000)
]

MALTESER_PRICE = 250_000
MALTESER_BONUS = 50

# ================= LOGIC =================
def click():
    bonus = MALTESER_BONUS if st.session_state.malteser else 0
    gain = (st.session_state.money_per_click + bonus) * (1 + st.session_state.prestige)
    st.session_state.money += gain
    st.session_state.total_clicks += 1

def auto_tick():
    st.session_state.money += (
        st.session_state.money_per_second * (1 + st.session_state.prestige) * 0.1
    )

def buy_click_upgrade():
    if st.session_state.money >= 10:
        st.session_state.money -= 10
        st.session_state.money_per_click += 1
        st.session_state.total_upgrades += 1

def buy_auto_upgrade():
    if st.session_state.money >= 25:
        st.session_state.money -= 25
        st.session_state.money_per_second += 1
        st.session_state.total_upgrades += 1

def buy_weapon():
    lvl = st.session_state.weapon_level + 1
    if lvl < len(weapons) and st.session_state.money >= weapons[lvl][2]:
        st.session_state.money -= weapons[lvl][2]
        st.session_state.weapon_level = lvl
        st.session_state.money_per_click = weapons[lvl][1]
        st.session_state.total_upgrades += 1

def buy_malteser():
    if not st.session_state.malteser and st.session_state.money >= MALTESER_PRICE:
        st.session_state.money -= MALTESER_PRICE
        st.session_state.malteser = True
        st.session_state.achievements["Malteser gekocht"] = True

def bonus():
    if st.session_state.bonus_cd <= 0:
        st.session_state.money += 50 * (1 + st.session_state.prestige)
        st.session_state.bonus_cd = 10

def prestige():
    if st.session_state.money >= 1000:
        st.session_state.prestige += 1
        st.session_state.money = 0
        st.session_state.money_per_click = 1
        st.session_state.money_per_second = 0
        st.session_state.weapon_level = 0
        st.session_state.malteser = False
        st.session_state.achievements["Prestige gedaan"] = True

def check_achievements():
    m = st.session_state.money
    if m >= 100:
        st.session_state.achievements["100 geld"] = True
    if m >= 1_000:
        st.session_state.achievements["1.000 geld"] = True
    if m >= 100_000:
        st.session_state.achievements["100.000 geld"] = True
    if st.session_state.money_per_second >= 10:
        st.session_state.achievements["10 per seconde"] = True

# ================= UI =================
st.title("💥 ULTRA Kartonnen Clicker")

st.write(f"💰 **Geld:** €{int(st.session_state.money)}")
st.write(f"👊 **Per klik:** €{st.session_state.money_per_click} + {MALTESER_BONUS if st.session_state.malteser else 0}")
st.write(f"⏱️ **Per seconde:** €{st.session_state.money_per_second}")
st.write(f"⭐ **Prestige:** x{1 + st.session_state.prestige}")
st.write(f"🔫 **Wapen:** {weapons[st.session_state.weapon_level][0]}")
st.write(f"🐶 **Malteser:** {'Ja' if st.session_state.malteser else 'Nee'}")

st.divider()

if st.button("🔘 KLIK OP WAPEN"):
    click()

st.divider()
st.subheader("🛒 Shop")

c1, c2 = st.columns(2)
with c1:
    st.button("Upgrade klik (+1 | €10)", on_click=buy_click_upgrade)
with c2:
    st.button("Auto geld (+1/sec | €25)", on_click=buy_auto_upgrade)

lvl = st.session_state.weapon_level + 1
if lvl < len(weapons):
    st.button(
        f"Koop {weapons[lvl][0]} (€{weapons[lvl][2]})",
        on_click=buy_weapon
    )

if not st.session_state.malteser:
    st.button("🐶 Koop Malteser (+50 per klik | €250.000)", on_click=buy_malteser)

st.divider()
st.button("🎁 Bonus (+50)", on_click=bonus)
st.button("🔁 Prestige (vanaf €1000)", on_click=prestige)

st.divider()
st.subheader("📊 Statistieken")
st.write(f"Totale kliks: {st.session_state.total_clicks}")
st.write(f"Totale upgrades: {st.session_state.total_upgrades}")
st.write(f"Tijd gespeeld: {int(time.time() - st.session_state.start_time)} sec")

st.divider()
st.subheader("🏆 Achievements")
for a, v in st.session_state.achievements.items():
    st.write(("✔" if v else "✖") + " " + a)

# ================= LOOP =================
auto_tick()
if st.session_state.bonus_cd > 0:
    st.session_state.bonus_cd -= 0.1

check_achievements()

time.sleep(0.1)
st.experimental_rerun()
