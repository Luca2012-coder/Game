import streamlit as st

def tic_tac_toe():
    st.title("❌⭕ Tic Tac Toe")
    if "ttt_bord" not in st.session_state:
        st.session_state.ttt_bord = [""] * 9
        st.session_state.ttt_speler = "X"
        st.session_state.ttt_winnaar = ""

    def check_winner():
        b = st.session_state.ttt_bord
        w = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for i,j,k in w:
            if b[i] == b[j] == b[k] and b[i] != "":
                return b[i]
        return ""

    cols = st.columns(3)
    for i in range(9):
        with cols[i % 3]:
            if st.button(st.session_state.ttt_bord[i] or " ", key=i):
                if st.session_state.ttt_bord[i] == "" and st.session_state.ttt_winnaar == "":
                    st.session_state.ttt_bord[i] = st.session_state.ttt_speler
                    winnaar = check_winner()
                    if winnaar:
                        st.session_state.ttt_winnaar = winnaar
                    else:
                        st.session_state.ttt_speler = "O" if st.session_state.ttt_speler == "X" else "X"

    if st.session_state.ttt_winnaar:
        st.success(f"{st.session_state.ttt_winnaar} wint!")
        if st.button("🔄 Opnieuw"):
            st.session_state.ttt_bord = [""] * 9
            st.session_state.ttt_speler = "X"
            st.session_state.ttt_winnaar = ""
