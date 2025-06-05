import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import time

def flappy():
    WIDTH = 400
    HEIGHT = 600
    blokje_x = 100

    # Helper functies binnen flappy
    def reset_pijp():
        gat_y = random.randint(150, 450)
        start_x = WIDTH
        return {'x': start_x, 'gat_y': gat_y}

    def rects_collide(r1, r2):
        # r = [x, y, width, height]
        return not (r1[0] + r1[2] < r2[0] or r1[0] > r2[0] + r2[2] or
                    r1[1] + r1[3] < r2[1] or r1[1] > r2[1] + r2[3])

    def teken_spel():
        fig, ax = plt.subplots(figsize=(4,6))
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.axis('off')

        # teken blokje
        blokje = patches.Rectangle((blokje_x-15, st.session_state.blokje_y-15), 30, 30, color='orange')
        ax.add_patch(blokje)

        # teken pijpen
        for pijp in st.session_state.pijpen:
            # bovenpijp
            boven = patches.Rectangle((pijp['x'], 0), 50, pijp['gat_y'] - 75, color='green')
            ax.add_patch(boven)
            # onderpijp
            onder = patches.Rectangle((pijp['x'], pijp['gat_y'] + 75), 50, HEIGHT - pijp['gat_y'] - 75, color='green')
            ax.add_patch(onder)

        # score tekst
        ax.text(10, HEIGHT-30, f"Score: {st.session_state.score}", fontsize=15, color='black')

        st.pyplot(fig)

    def update_game(jump=False):
        if not st.session_state.started or st.session_state.game_over:
            return

        if jump:
            st.session_state.zwaartekracht = -8

        st.session_state.zwaartekracht += 0.5
        st.session_state.blokje_y += st.session_state.zwaartekracht

        # beweeg pijpen
        for pijp in st.session_state.pijpen:
            pijp['x'] -= 2

        # voeg nieuwe pijp toe als de laatste pijp voorbij helft is
        if st.session_state.pijpen[-1]['x'] < WIDTH/2:
            st.session_state.pijpen.append(reset_pijp())

        # verwijder pijpen buiten beeld
        if st.session_state.pijpen[0]['x'] < -50:
            st.session_state.pijpen.pop(0)
            st.session_state.score += 1

        # check botsingen
        blokje_rect = [blokje_x -15, st.session_state.blokje_y -15, 30, 30]
        for pijp in st.session_state.pijpen:
            boven_rect = [pijp['x'], 0, 50, pijp['gat_y'] - 75]
            onder_rect = [pijp['x'], pijp['gat_y'] + 75, 50, HEIGHT - pijp['gat_y'] - 75]
            if rects_collide(blokje_rect, boven_rect) or rects_collide(blokje_rect, onder_rect):
                st.session_state.game_over = True

        if st.session_state.blokje_y > HEIGHT or st.session_state.blokje_y < 0:
            st.session_state.game_over = True

    # Initialize session state
    if 'blokje_y' not in st.session_state:
        st.session_state.blokje_y = HEIGHT // 2
    if 'zwaartekracht' not in st.session_state:
        st.session_state.zwaartekracht = 0
    if 'pijpen' not in st.session_state:
        st.session_state.pijpen = [reset_pijp()]
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'started' not in st.session_state:
        st.session_state.started = False
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False

    st.title("Flappy Blok (Streamlit Mini-Game)")

    if st.session_state.game_over:
        st.write(f"Game over! Je score: {st.session_state.score}")
        if st.button("Opnieuw spelen"):
            st.session_state.blokje_y = HEIGHT // 2
            st.session_state.zwaartekracht = 0
            st.session_state.pijpen = [reset_pijp()]
            st.session_state.score = 0
            st.session_state.started = False
            st.session_state.game_over = False
    else:
        if not st.session_state.started:
            if st.button("Start spel (druk op Start)"):
                st.session_state.started = True
        else:
            if st.button("Spring! (Space)"):
                update_game(jump=True)
            else:
                update_game(jump=False)

        teken_spel()

    # Refresh elke 0.1 sec om het spel te laten lopen
    if st.session_state.started and not st.session_state.game_over:
        time.sleep(0.1)
        st.experimental_rerun()
