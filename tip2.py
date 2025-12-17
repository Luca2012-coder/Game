import streamlit as st
import random

# Initialiseer sessiestate voor geld en upgrade
if 'geld' not in st.session_state:
    st.session_state.geld = 0
if 'upgrade' not in st.session_state:
    st.session_state.upgrade = None  # 'karton' of 'metaal'
if 'per_klik' not in st.session_state:
    st.session_state.per_klik = 100
if 'resultaat' not in st.session_state:
    st.session_state.resultaat = ""

# Functies
def klik():
    winst = st.session_state.per_klik
    if st.session_state.upgrade == 'karton':
        winst += 500
    elif st.session_state.upgrade == 'metaal':
        winst += 1000
    st.session_state.geld += winst
    st.session_state.resultaat = f"Je hebt geklikt! Je krijgt {winst} geld."

def abels_punch():
    kans = random.random()
    verlies = 0
    if kans < 0.6:  # 60% kans
        if st.session_state.upgrade == 'karton':
            verlies = 250
        elif st.session_state.upgrade == 'metaal':
            verlies = 750
        else:
            verlies = 50
        st.session_state.geld -= verlies
        st.session_state.resultaat = f"Abel's punch! Je verliest {verlies} geld."
    else:
        st.session_state.resultaat = "Abel's punch! Je verliest niks."

def koop_upgrade(wapen):
    st.session_state.upgrade = wapen
    st.session_state.resultaat = f"Upgrade gekocht: {wapen}"

# Streamlit interface
st.title("Clicker Game")

st.write(f"Geld: {st.session_state.geld}")
st.write(f"Upgrade: {st.session_state.upgrade if st.session_state.upgrade else 'Geen'}")

if st.button("Klik (100 geld)"):
    klik()

if st.button("Abel's Punch!"):
    abels_punch()

if st.button("Koop Kartonnen Wapen (+500 per klik)"):
    koop_upgrade('karton')

if st.button("Koop Metalen Wapen (+1000 per klik)"):
    koop_upgrade('metaal')

st.write(st.session_state.resultaat)
