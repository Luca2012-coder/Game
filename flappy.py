import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

WIDTH = 300
HEIGHT = 450
blokje_x = 80

def reset_pijp():
    gat_y = random.randint(100, HEIGHT - 100)
    start_x = WIDTH
    return {'x': start_x, 'gat_y': gat_y}

def rects_collide(r1, r2):
    # r = [x, y, width, height]
    return not (r1[0] + r1[2] < r2[0] or r1[0] > r2[0] + r2[2] or
                r1[1] + r1[3] < r2[1] or r1[1] > r2[1] + r2[3])

def flappy():
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

    def teken_spel():
        fig, ax = plt.subplots(figsize=(3,4.5))
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.axis('off')

        blokje = patches.Rectangle((blokje_x-15, st.session_state.blokje_y-15), 30, 30, color='orange')
        ax.add_patch(blokje)

        for pijp in st.session_state.pijpen:
            boven = patches.Rectangle((pijp['x'], 0), 40, pijp['gat_y'] - 60, color='green')
            onder = patches.Rectangle((pijp['x'], pijp['gat_y'] + 60), 40, HEIGHT - pijp['gat_y'] - 60, color='green')
            ax.add_patch(boven)
            ax.add_patch(onder)

        ax.text(10, HEIGHT - 30, f"Score: {st.session_state.score}", fontsize=14, color='black')

        st.pyplot(fig)

    def update_game(jump=False):
        if not st.session_state.started or st.session_state.game_over:
            return

        if jump:
            st.session_state.zwaartekracht = -7

        st.session_state.zwaartekracht += 0.4
        st.session_state.blokje_y += st.session_state.zwaartekracht

        for pijp in st.session_state.pijpen:
            pijp['x'] -= 2

        if st.session_state.pijpen[-1]['x'] < WIDTH / 2:
            st.session_state.pijpen.append(reset_pijp())

        if st.session_state.pijpen[0]['x'] < -40:
            st.session_state.pijpen.pop(0)
            st.session_state.score += 1

        blokje_rect = [blokje_x - 15, st.session_state.blokje_y - 15, 30, 30]
        for pijp in st.session_state.pijpen:
            boven_rect = [pijp['x'], 0, 40, pijp['gat_y'] - 60]
            onder_rect = [pijp['x'], pijp['gat_y'] + 60, 40, HEIGHT - pijp['gat_y'] - 60]
            if rects_collide(blokje_rect, boven_rect) or rects_collide(blokje_rect, onder_rect):
                st.session_state.game_over = True

        if st.session_state.blokje_y > HEIGHT or st.session_state.blokje_y < 0:
            st.session_state.game_over = True

    st.title("Flappy Blok")

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
        user_input = st.text_input("Typ 'v' en druk op Enter om te starten/springen", "")

        if not st.session_state.started:
            if user_input.lower() == 'v':
                st.session_state.started = True
                update_game(jump=True)
        else:
            if user_input.lower() == 'v':
                update_game(jump=True)
            else:
                update_game(jump=False)

        teken_spel()
