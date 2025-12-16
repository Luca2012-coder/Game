import streamlit as st
import time

st.set_page_config(page_title="Kartonnen Wapen Clicker", layout="centered")

# ====== INIT ======
if "money" not in st.session_state:
    st.session_state.money = 0
    st.session_state.click_value = 1
    st.session_state.auto_money = 0
    st.session_state.weapon = "🧻 Kartonnen Pistol"
    st.session_state.last_time = time.time()
    st.session_state.weapons_owned = ["🧻 Kartonnen Pistol"]

# ====== AUTO GELD ======
now = time.time()
delta = now - st.session_state.last_time
st.session_state.money += int(delta * st.session_state.auto_money)
st.session_state.last_time = now

# ====== UI ======
st.title("🧻 Kartonnen Wapen Clicker")
st.subheader(f"💰 Geld: €{st.session_state.money}")
st.write(f"🔫 Huidig wapen: **{st.session_state.weapon}**")
st.write(f"💥 Geld per klik: {st.session_state.click_value}")
st.write(f"⏱️ Geld per seconde: {st.session_state.auto_money}")

st.divider()

# ====== KLIKKNOP ======
if st.button(st.session_state.weapon, use_container_width=True):
    st.session_state.money += st.session_state.click_value
    st.rerun()

st.divider()

# ====== SHOP ======
st.header("🛒 Shop")

# Upgrade klik
if st.button("💥 Upgrade klik (+1) – €10"):
    if st.session_state.money >= 10:
        st.session_state.money -= 10
        st.session_state.click_value += 1
        st.rerun()
    else:
        st.warning("Niet genoeg geld!")

# Auto geld
if st.button("⏱️ Auto geld (+1/sec) – €25"):
    if st.session_state.money >= 25:
        st.session_state.money -= 25
        st.session_state.auto_money += 1
        st.rerun()
    else:
        st.warning("Niet genoeg geld!")

st.divider()

# ====== WAPENS ======
st.header("🔫 Wapens")

weapons = {
    "📦 Kartonnen Shotgun": 50,
    "📐 Kartonnen Sniper": 100,
    "🧱 Kartonnen Bazooka": 250
}

for wapen, prijs in weapons.items():
    if wapen not in st.session_state.weapons_owned:
        if st.button(f"Koop {wapen} – €{prijs}"):
            if st.session_state.money >= prijs:
                st.session_state.money -= prijs
                st.session_state.weapons_owned.append(wapen)
                st.session_state.weapon = wapen
                st.session_state.click_value += 2
                st.rerun()
            else:
                st.warning("Niet genoeg geld!")
    else:
        if st.button(f"Gebruik {wapen}"):
            st.session_state.weapon = wapen
            st.rerun()

st.divider()

# ====== RESET ======
if st.button("🔄 RESET GAME"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.caption("🧠 Gemaakt met Streamlit | Kartonnen economie simulator")
