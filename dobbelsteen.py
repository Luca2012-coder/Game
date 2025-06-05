import streamlit as st
import random

def dobbelsteen():
    st.title("🎲 Dobbelsteen")

    if "worpen" not in st.session_state:
        st.session_state.worpen = []

    st.write("Klik op de knop om de dobbelsteen te gooien. Je laatste 3 worpen worden getoond.")

    if st.button("Gooi dobbelsteen"):
        worp = random.randint(1, 6)
        st.session_state.worpen.append(worp)

        # Als er 3 worpen zijn, toon ze eerst, wacht even en reset dan
        if len(st.session_state.worpen) == 3:
            # Laatste worpen en totaal worden hieronder getoond,
            # daarna resetten we de lijst
            pass

    if st.session_state.worpen:
        st.subheader("Laatste worpen:")
        for i, worp in enumerate(st.session_state.worpen, start=1):
            st.write(f"Worp {i}: 🎲 {worp}")
            st.image(f"https://upload.wikimedia.org/wikipedia/commons/thumb/{get_dice_image_path(worp)}", width=80)

        totaal = sum(st.session_state.worpen)
        st.success(f"Totaalscore van laatste 3 worpen: {totaal}")

        # Als er 3 worpen zijn, resetten na tonen
        if len(st.session_state.worpen) == 3:
            st.session_state.worpen = []

def get_dice_image_path(number):
    paths = {
        1: "1/1b/Dice-1-b.svg/120px-Dice-1-b.svg.png",
        2: "5/5f/Dice-2-b.svg/120px-Dice-2-b.svg.png",
        3: "b/b1/Dice-3-b.svg/120px-Dice-3-b.svg.png",
        4: "f/fd/Dice-4-b.svg/120px-Dice-4-b.svg.png",
        5: "0/08/Dice-5-b.svg/120px-Dice-5-b.svg.png",
        6: "2/26/Dice-6-b.svg/120px-Dice-6-b.svg.png",
    }
    return paths[number]

if __name__ == "__main__":
    dobbelsteen()
