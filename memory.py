import streamlit as st
import random
import time

def memory_game():
    st.title("🧠 Memory Game")

    if "cards" not in st.session_state:
        kaarten = ['🍎', '🍌', '🍇', '🍒', '🍉', '🍓', '🍍', '🥝'] * 2
        random.shuffle(kaarten)
        st.session_state.cards = kaarten
        st.session_state.kaartstatus = [False] * 16  # True = gevonden match
        st.session_state.geopende_indexen = []      # open kaarten (max 2)
        st.session_state.matches = 0
        st.session_state.timer_start = 0            # tijd waarop laatste 2 kaarten open gingen

    def check_match():
        if len(st.session_state.geopende_indexen) == 2:
            i1, i2 = st.session_state.geopende_indexen
            if st.session_state.cards[i1] == st.session_state.cards[i2]:
                st.session_state.kaartstatus[i1] = True
                st.session_state.kaartstatus[i2] = True
                st.session_state.matches += 1
            st.session_state.geopende_indexen = []

    now = time.time()

    # Check of we moeten sluiten
    if st.session_state.timer_start != 0 and now - st.session_state.timer_start > 1.5:
        check_match()
        st.session_state.timer_start = 0  # reset timer zodat klikken weer kan

    def klik(index):
        # Als kaart al open of gematcht, doe niks
        if st.session_state.kaartstatus[index] or index in st.session_state.geopende_indexen:
            return

        # Blokkeer klikken alleen als er al 2 kaarten open liggen en timer loopt
        if len(st.session_state.geopende_indexen) == 2 and st.session_state.timer_start != 0:
            return

        # Open de kaart
        if len(st.session_state.geopende_indexen) < 2:
            st.session_state.geopende_indexen.append(index)

        # Als nu 2 kaarten open, start timer
        if len(st.session_state.geopende_indexen) == 2:
            st.session_state.timer_start = time.time()

    cols = st.columns(4)
    for i, kaart in enumerate(st.session_state.cards):
        if st.session_state.kaartstatus[i] or i in st.session_state.geopende_indexen:
            tekst = kaart
        else:
            tekst = "❓"
        with cols[i % 4]:
            if st.button(tekst, key=i):
                klik(i)

    if st.session_state.matches == 8:
        st.success("🎉 Gefeliciteerd, je hebt alle paren gevonden!")

    if st.button("🔄 Nieuw spel"):
        for key in ["cards", "kaartstatus", "geopende_indexen", "matches", "timer_start"]:
            if key in st.session_state:
                del st.session_state[key]
