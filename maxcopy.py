import streamlit as st
import time
import random

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="TIP Clicker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================
# CSS (BASE44 STYLE)
# =============================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #3a0a6a, #5a189a);
}
.main {
    background: transparent;
}
header, footer, .stDeployButton {display:none;}

.stat-card {
    background: rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    width: 420px;
    margin: auto;
    color: #ffd60a;
}

.coin-btn button {
    width: 220px;
    height: 220px;
    border-radius: 50%;
    font-size: 90px;
    background: #ffd60a;
    border: none;
}

.menu-btn button {
    height: 90px;
    border-radius: 16px;
    font-weight: bold;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# STATE INIT
# =============================
def init(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

init("money", 0)
init("per_click", 1)
init("per_sec", 0)
init("level", 1)
init("page", "game")

# =============================
# AUTO INCOME
# =============================
st.session_state.money += st.session_state.per_sec * 0.1

# =============================
# TOP STATS
# =============================
st.markdown(f"""
<div class="stat-card">
    <h2>🪙 {int(st.session_state.money):,}</h2>
    <p>+{st.session_state.per_sec}/sec van hulpjes</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# =============================
# GAME TITLE
# =============================
st.markdown("<h1 style='text-align:center;color:#ffd60a;'>TIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:white;'>Klik op Tip voor geld!</p>", unsafe_allow_html=True)

# =============================
# COIN BUTTON
# =============================
st.markdown("<div class='coin-btn'>", unsafe_allow_html=True)
if st.button("🐶"):
    st.session_state.money += st.session_state.per_click
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"<p style='text-align:center;color:white;'>⚡ Klik Power: {st.session_state.per_click} | Level: {st.session_state.level}</p>",
    unsafe_allow_html=True
)

st.write("")
st.write("")

# =============================
# MENU
# =============================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("🛒\nShop"):
        st.session_state.page = "shop"

with c2:
    st.button("🥚\nEieren")

with c3:
    st.button("🐶\nHonden")

with c4:
    st.button("🔥\nBosses")

with c5:
    st.button("🏆\nMissies")

# =============================
# SHOP PAGE
# =============================
if st.session_state.page == "shop":
    st.divider()
    st.subheader("🛒 Shop")

    if st.button("➕ Upgrade Klik (+1) — €50"):
        if st.session_state.money >= 50:
            st.session_state.money -= 50
            st.session_state.per_click += 1

    if st.button("🤖 Hulpje (+1/sec) — €200"):
        if st.session_state.money >= 200:
            st.session_state.money -= 200
            st.session_state.per_sec += 1

    if st.button("⬅️ Terug"):
        st.session_state.page = "game"

# =============================
# LOOP
# =============================
time.sleep(0.1)
st.experimental_rerun()
