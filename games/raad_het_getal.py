import streamlit as st
import random

def raad_het_getal():
    st.title("🎯 Raad het Getal")
    if "doelgetal" not in st.session_state:
        st.session_state.doelgetal = random.randint(1, 100)
        st.session_state.pogingen = 0
        st.session_state.geraden = False

    gok = st.number_input("Voer je gok in:", min_value=1, max_value=100, step=1, key="gok")
    if st.button("Gok!") and not st.session_state.geraden:
        st.session_state.pogingen += 1
        if gok < st.session_state.doelgetal:
            st.warning("Hoger!")
        elif gok > st.session_state.doelgetal:
            st.warning("Lager!")
        else:
            st.success(f"🎉 Je raadde het in {st.session_state.pogingen} pogingen!")
            st.session_state.geraden = True

    if st.session_state.geraden:
        if st.button("🔄 Opnieuw spelen"):
            st.session_state.doelgetal = random.randint(1, 100)
            st.session_state.pogingen = 0
            st.session_state.geraden = False
