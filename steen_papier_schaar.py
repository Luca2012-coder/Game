import streamlit as st
import random

def steen_papier_schaar():
    st.title("✂️🪨📄 Steen Papier Schaar")
    keuzes = ["Steen", "Papier", "Schaar"]
    keuze = st.selectbox("Maak je keuze:", keuzes)
    if st.button("Speel!"):
        computer = random.choice(keuzes)
        st.write(f"💻 De computer kiest: **{computer}**")
        if keuze == computer:
            st.info("Gelijkspel!")
        elif (keuze == "Steen" and computer == "Schaar") or \
             (keuze == "Papier" and computer == "Steen") or \
             (keuze == "Schaar" and computer == "Papier"):
            st.success("Je wint!")
        else:
            st.error("Je verliest!")
