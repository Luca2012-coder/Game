import streamlit as st
import random

def kamertje_verhuren():
    st.title("🏠 Kamertje Verhuren")
    kamers = ["Kamer 1", "Kamer 2", "Kamer 3"]
    prijzen = [50, 75, 100]
    verhuurd = st.session_state.get("verhuurd", [False]*len(kamers))

    for i, kamer in enumerate(kamers):
        if verhuurd[i]:
            st.write(f"{kamer} is verhuurd!")
        else:
            if st.button(f"Verhuur {kamer} voor €{prijzen[i]}"):
                verhuurd[i] = True
                st.session_state.verhuurd = verhuurd
                st.success(f"{kamer} is nu verhuurd!")

    if st.button("Reset kamers"):
        st.session_state.verhuurd = [False]*len(kamers)
