import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

WIDTH = 180
HEIGHT = 250
blokje_x = 50

def reset_pijp():
    gat_y = random.randint(60, HEIGHT - 60)
    start_x = WIDTH
    return {'x': start_x, 'gat_y': gat_y}

def rects_collide(r1, r2):
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
        fig, ax = plt.subplots(figsize=(1.8, 2.5))
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.axis('off')

        blokje = patches.Rectangle((blokje_x-9, st.session_state.blokje_y-9), 18, 18, color='orange')
        ax.add_patch(blokje)

        for pijp in st.session_state.pijpen:
            boven = patches.Rectangle((pijp['x'], 0), 20, pijp['gat_y'] - 40, color='green')
            onder = patches.Rectangle((pijp['x'], pijp['gat_y'] + 40), 20, HEIGHT - pijp['gat_y'] - 40, color='green')
            ax.add_patch(boven)
            ax.add_patch(onder)

        ax.text(5, HEIGHT - 20, f"Score: {st.session_state.score}", fontsize=10, color='black')

        st.pyplot(fig)

    def update_game(jump=False):
        if not st.session_state.started or st.session_state.game_over:
            return

        if jump:
            st.session_state.zwaartekracht = -5

        st.session_state.zwaartekracht += 0.3
        st.session_state.blokje_y += st.session_state.zwaartekracht

        for pijp in st.session_state.pijpen:
            pijp['x'] -= 2

        if st.session_state.pijpen[-1]['x'] < WIDTH / 2:
            st.session_state.pijpen.append(reset_pijp())

        if st.session_state.pijpen[0]['x'] < -20:
            st.session_state.pijpen.pop(0)
            st.session_state.score += 1

        blokje_rect = [blokje_x - 9, st.session_state.blokje_y - 9, 18, 18]
        for pijp in st.session_state.pijpen:
            boven_rect = [pijp['x'], 0, 20, pijp['gat_y'] - 40]
            onder_rect = [pijp['x'], pijp['gat_y'] + 40, 20, HEIGHT - pijp['gat_y'] - 40]
            if rects_collide(blokje_rect, boven_rect) or rects_collide(blokje_rect, onder_rect):
                st.session_state.game_over = True

        if st.session_state.blokje_y > HEIGHT or st.session_state.blokje_y < 0:
            st.session_state.game_over = True

    st.title("Flappy Blok (klein)")

    # Knop vlak boven de plot en met kleine margin via markdown CSS
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
            if st.button("Start spel"):
                st.session_state.started = True
                update_game(jump=True)
        else:
            # Zet de knop met wat markdown vlak boven de plot
            st.markdown("<div style='margin-bottom:2px'>", unsafe_allow_html=True)
            if st.button("Spring"):
                update_game(jump=True)
            else:
                update_game(jump=False)
            st.markdown("</div>", unsafe_allow_html=True)

        teken_spel()
