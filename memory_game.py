import streamlit as st
import random
import time

def memory_game():
    st.title("🧠 Memory Game")

    # Kaarten en shuffle
    kaarten = ['🍎', '🍌', '🍇', '🍒', '🍉', '🍓', '🍍', '🥝'] * 2
    if "cards" not in st.session_state:
        random.shuffle(kaarten)
        st.session_state.cards = kaarten
        st.session_state.kaartstatus = [False] * 16  # False = kaart is gesloten
        st.session_state.geopende_indexen = []
        st.session_state.matches = 0
        st.session_state.lock = False

    # Functie om te checken op match
    def check_match():
        i1, i2 = st.session_state.geopende_indexen
        if st.session_state.cards[i1] == st.session_state.cards[i2]:
            st.session_state.kaartstatus[i1] = True
            st.session_state.kaartstatus[i2] = True
            st.session_state.matches += 1
        st.session_state.geopende_indexen = []
        st.session_state.lock = False

    # Kaart klikken
    def klik(index):
        if st.session_state.lock or st.session_state.kaartstatus[index]:
            return
        if len(st.session_state.geopende_indexen) < 2:
            st.session_state.geopende_indexen.append(index)
            if len(st.session_state.geopende_indexen) == 2:
                st.session_state.lock = True
                time.sleep(1)
                check_match()

    # Kaarten tonen
    cols = st.columns(4)
    for i, kaart in enumerate(st.session_state.cards):
        if st.session_state.kaartstatus[i]:
            met_tekst = kaart
        elif i in st.session_state.geopende_indexen:
            met_tekst = kaart
        else:
            met_tekst = "❓"

        with cols[i % 4]:
            if st.button(met_tekst, key=i):
                klik(i)

    # Winst checken
    if st.session_state.matches == 8:
        st.success("🎉 Gefeliciteerd, je hebt alle paren gevonden!")

    # Reset knop
    if st.button("🔄 Nieuw spel"):
        st.session_state.pop("cards", None)
        st.session_state.pop("kaartstatus", None)
        st.session_state.pop("geopende_indexen", None)
        st.session_state.pop("matches", None)
        st.session_state.pop("lock", None)
