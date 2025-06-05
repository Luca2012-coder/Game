import streamlit as st
import time
import random

def reactietest():
    st.title("⏱️ Reactietest")

    # Initialisatie
    if "fase" not in st.session_state:
        st.session_state.fase = "start"
        st.session_state.klaartijd = 0.0
        st.session_state.reactie = None

    # Startfase
    if st.session_state.fase == "start":
        st.write("Klik op Start, wacht tot de knop verschijnt en klik dan zo snel mogelijk!")
        if st.button("Start"):
            st.session_state.fase = "wachten"
            wachttijd = random.uniform(2, 6)
            st.session_state.klaartijd = time.time() + wachttijd
            st.session_state.reactie = None
            time.sleep(wachttijd)
            st.session_state.fase = "klaar"

    # Knop verschijnt na wachttijd
    if st.session_state.fase == "klaar":
        if st.button("Klik zo snel mogelijk!"):
            reactietijd = time.time() - st.session_state.klaartijd
            st.session_state.reactie = reactietijd
            st.session_state.fase = "resultaat"

    # Reactietijd tonen
    if st.session_state.fase == "resultaat":
        st.success(f"Je reactietijd was: {st.session_state.reactie:.3f} seconden")
        if st.button("Opnieuw"):
            st.session_state.fase = "start"
            st.session_state.reactie = None

if __name__ == "__main__":
    reactietest()
