# la_famiglia_game.py
# Streamlit app: La Famiglia (parody). Persistent profiles + avatar shop + ranks,
# slow/low-yield earning actions, and a Daily Mission that is actually played in a
# separate pygame mini-game (pacman_mission.py). Earnings are synced via profiles.json.
#
# How to run locally:
#   1) pip install streamlit
#   2) streamlit run la_famiglia_game.py
#   3) (For Daily Mission) pip install pygame, then run: python pacman_mission.py --profile YOUR_NAME
#
# NOTE: The pacman mini-game (pygame) will NOT run on Streamlit Cloud. Play it locally.

import streamlit as st
import json
import random
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path("profiles.json")
st.set_page_config(page_title="La Famiglia – Parody Game", page_icon="🍝", layout="wide")

# Shop items with position on avatar: top, eyes, neck, torso, feet, side
SHOP_ITEMS = {
    "Fedora": {"price": 300, "emoji": "🎩", "pos": "top", "xp": 18},
    "Sunglasses": {"price": 350, "emoji": "🕶️", "pos": "eyes", "xp": 22},
    "Gold Chain": {"price": 600, "emoji": "📿", "pos": "neck", "xp": 44},
    "Fancy Suit": {"price": 1200, "emoji": "🤵", "pos": "torso", "xp": 90},
    "Black Boots": {"price": 420, "emoji": "👞", "pos": "feet", "xp": 24},
    "Motorcycle": {"price": 2200, "emoji": "🏍️", "pos": "side", "xp": 150},
    "Recipe Scroll": {"price": 280, "emoji": "📜", "pos": "side", "xp": 20}
}

RANKS = [
    (0, "Rekruut"),
    (101, "Soldato"),
    (301, "Capo"),
    (701, "Consigliere"),
    (1501, "Underboss"),
    (3001, "Boss"),
]

BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]

# ------------------------
# Helpers: load/save
# ------------------------

def load_profiles():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            backup = DATA_FILE.with_suffix(".broken.json")
            DATA_FILE.replace(backup)
            return {}
    return {}


def save_profiles(profiles):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Kon profielen niet opslaan: {e}")


def autosave():
    save_profiles(st.session_state["profiles"])


# ------------------------
# Session initialization
# ------------------------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = load_profiles()

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = None


# ------------------------
# Profile helpers
# ------------------------

def new_profile_struct(name, age, bio):
    return {
        "name": name,
        "age": age,
        "bio": bio,
        "created": datetime.now().isoformat(timespec="seconds"),
        "money": 120,   # small start, slow growth
        "xp": 0,
        "level": 1,
        "items": [],
        "history": [],
        "avatar": {"base": random.choice(BASE_AVATARS), "top": "", "eyes": "", "neck": "", "torso": "", "feet": "", "side": ""},
        "last_mission_date": None,
        "application": None
    }


def save_event(profile, text):
    profile["history"].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text})
    autosave()


def get_rank(xp):
    rank = RANKS[0][1]
    for req, title in RANKS:
        if xp >= req:
            rank = title
    return rank


def render_avatar(profile):
    a = profile["avatar"]
    lines = [
        a.get("top", ""),
        f"{a.get('base','😎')}{a.get('eyes','')}",
        a.get("neck", ""),
        a.get("torso", ""),
        a.get("feet", "")
    ]
    side = a.get("side", "")
    avatar_str = "\n".join(lines)
    if side:
        avatar_str = avatar_str.replace("\n", f" {side}\n")
    return avatar_str


# ------------------------
# Sidebar profile management
# ------------------------

st.sidebar.title("Profielen")
if st.sidebar.button("Nieuw profiel"):
    st.session_state["creating_new"] = True

profiles_list = list(st.session_state["profiles"].keys())
selected = st.sidebar.selectbox("Selecteer profiel", options=["--nieuw--"] + profiles_list)
if selected != "--nieuw--":
    st.session_state["current_profile"] = selected
    st.session_state["creating_new"] = False

if "creating_new" not in st.session_state:
    st.session_state["creating_new"] = False

if st.sidebar.button("Verwijder huidig profiel"):
    cur = st.session_state["current_profile"]
    if cur and cur in st.session_state["profiles"]:
        del st.session_state["profiles"][cur]
        st.session_state["current_profile"] = None
        autosave()
        st.sidebar.success("Profiel verwijderd")

st.sidebar.markdown("---")
st.sidebar.markdown("**Tip:** Speel de dagelijkse missie lokaal via `pacman_mission.py` voor grotere, maar nog steeds bescheiden beloningen.")

# ------------------------
# Tabs
# ------------------------

profile_tab, earn_tab, mission_tab, shop_tab, rank_tab = st.tabs([
    "📝 Sollicitatie & Profiel", "💼 Altijd geld (moeilijk)", "🎯 Dagelijkse missie", "🛍️ Shop & Avatar", "📜 Rang & Historie"
])

# ------------------------
# Tab: Sollicitatie & Profiel
# ------------------------

with profile_tab:
    st.header("📝 Sollicitatieformulier")
    st.caption("Vul volledig in. Kans op afwijzing is reëel!")

    with st.form("application_form", clear_on_submit=False):
        name = st.text_input("Volledige naam", value=(st.session_state["current_profile"] or ""))
        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=25)
        bio = st.text_area("Korte introductie / bio", value="Ik wil meedoen omdat...")

        experience = st.multiselect("Ervaring", [
            "Pizzabakken", "Logistiek", "Onderhandelen", "Discretie", "PR", "Technische hulp (IT)", "Financieel inzicht", "Kok / keuken"
        ])
        specialties = st.multiselect("Specialiteiten", [
            "Pizzabakken", "Discretie", "Netwerken", "Financieel inzicht", "PR", "Onderhandelen"
        ])

        calc = st.number_input("Rekentest: 17 + 23 = ?", value=0)
        loyal = st.checkbox("Ik ga professioneel en discreet om met opdrachten (loyale verklaring)")
        motivation = st.text_area("Motivatie (uitgebreid is beter)")

        submitted = st.form_submit_button("Verstuur sollicitatie")

    if submitted:
        form = {"name": name.strip(), "age": int(age), "bio": bio.strip(),
                "experience": experience, "specialties": specialties,
                "calc": int(calc), "loyal": bool(loyal), "motivation": motivation.strip()}

        # Strict scoring
        score = 0
        if 18 <= form["age"] <= 80: score += 2
        if len(form["motivation"])>100: score+=3
        elif len(form["motivation"])>40: score+=2
        elif len(form["motivation"])>10: score+=1
        score += min(3, len(form["experience"]))  # limited value
        score += min(2, len(form["specialties"]))
        if form["calc"]==40: score+=2
        if form["loyal"]: score+=3
        judge=random.random()
        if judge<0.06: score-=5
        elif judge>0.96: score+=3

        if score>=10: status="Aangenomen"
        elif score>=6: status="Op proef"
        else: status="Afgewezen"

        if name.strip() not in st.session_state["profiles"]:
            profile = new_profile_struct(name.strip(), age, bio.strip())
            st.session_state["profiles"][name.strip()] = profile
        profile = st.session_state["profiles"][name.strip()]
        profile["application"] = {"form": form, "score": score, "status": status, "when": datetime.now().isoformat(timespec="seconds")}
        save_event(profile, f"Sollicitatie ingediend — status: {status}")

        if status=="Aangenomen":
            profile["money"]+=40; profile["xp"]+=18
            save_event(profile,"Aangenomen: +€40 +18 XP")
            st.success(f"Gefeliciteerd — {status}! Je krijgt €40 en 18 XP.")
        elif status=="Op proef":
            profile["money"]+=15; profile["xp"]+=6
            save_event(profile,"Op proef: +€15 +6 XP")
            st.warning("Op proef. Bewijs jezelf via dagelijkse missie en moeilijke klussen.")
        else:
            save_event(profile,"Afgewezen bij sollicitatie")
            st.error("Helaas — afgewezen. Probeer later opnieuw.")

        st.session_state["current_profile"] = name.strip()
        autosave()

    # Active profile summary
    if st.session_state["current_profile"]:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.markdown("---")
        st.subheader(f"Actief profiel: {p['name']}")
        st.write(f"💰 Geld: €{p['money']}  |  ⭐ XP: {p['xp']}  |  🎖️ Rang: {get_rank(p['xp'])}")
        st.markdown(f"<div style='font-size:64px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)

# ------------------------
# Tab: Always-available earning (hard)
# ------------------------
with earn_tab:
    st.header("💼 Altijd geld verdienen (moeilijk)")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel in de sidebar.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.write("Deze acties zijn risicovol en leveren weinig op. Soms verlies je geld.")
        st.markdown("---")

        # Action 1: Protection run
        st.subheader("Bescherming innen bij zaken")
        st.caption("~50% kans op winst, ~50% kans op verlies. Uitbetaling klein.")
        if st.button("Probeer bescherming te innen"):
            r = random.random()
            if r < 0.48:
                gain = random.randint(12, 26)
                xp = random.randint(4, 10)
                p["money"] += gain
                p["xp"] += xp
                save_event(p, f"Bescherming: +€{gain}, +{xp} XP")
                st.success(f"Gelukt: +€{gain}, +{xp} XP")
            else:
                loss = random.randint(6, 18)
                p["money"] = max(0, p["money"] - loss)
                p["xp"] += 2
                save_event(p, f"Tegenslag bij bescherming: -€{loss}, +2 XP voor moeite")
                st.warning(f"Tegenslag: -€{loss}, +2 XP")

        st.markdown("---")
        # Action 2: Casino edge (mostly lose)
        st.subheader("Casino poging 🎰")
        st.caption("Kleine kans op winst, meestal verlies je. (Niet aanbevolen!)")
        if st.button("Waag een gok (€10 inzet)"):
            if p["money"] < 10:
                st.error("Niet genoeg geld voor inzet")
            else:
                p["money"] -= 10
                r = random.random()
                if r > 0.97:
                    win = 140
                    xp = 22
                    p["money"] += win
                    p["xp"] += xp
                    save_event(p, f"Casino jackpot: +€{win}, +{xp} XP")
                    st.success(f"Jackpot! +€{win}, +{xp} XP")
                elif r > 0.85:
                    win = 40
                    xp = 10
                    p["money"] += win
                    p["xp"] += xp
                    save_event(p, f"Casino winst: +€{win}, +{xp} XP")
                    st.info(f"Kleine winst: +€{win}, +{xp} XP")
                else:
                    save_event(p, "Casino verlies: -€10")
                    st.warning("Verloren: -€10")

        st.markdown("---")
        # Action 3: Kleine klusjes (grind)
        st.subheader("Kleine klusjes doen")
        st.caption("Zekerheid is laag, opbrengst zeer klein. Veel herhaling nodig.")
        if st.button("Doe een klusje"):
            r = random.random()
            if r < 0.75:
                gain = random.randint(4, 9)
                xp = random.randint(2, 5)
                p["money"] += gain
                p["xp"] += xp
                save_event(p, f"Klusje gelukt: +€{gain}, +{xp} XP")
                st.success(f"Klusje gelukt: +€{gain}, +{xp} XP")
            else:
                save_event(p, "Klusje mislukte: geen opbrengst")
                st.info("Mislukt, geen beloning.")

        # Level update + autosave
        p["level"] = 1 + p["xp"] // 150
        autosave()

# ------------------------
# Tab: Daily Mission (played in pygame)
# ------------------------
with mission_tab:
    st.header("🎯 Dagelijkse missie — te spelen in pacman_mission.py")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        today_str = date.today().isoformat()
        done = (p.get("last_mission_date") == today_str)
        if done:
            st.success("Je hebt je dagelijkse missie vandaag al voltooid. Speel morgen opnieuw voor missie-beloning.")
            st.caption("Je mag het spel wel starten voor training, maar dat levert weinig tot niets op.")
        else:
            st.info("Je dagelijkse missie is nog open! Start de pacman mini-game lokaal.")
        st.markdown("---")
        st.subheader("Zo speel je de missie (lokaal):")
        st.code("""
# Terminal/Command Prompt
pip install pygame
python pacman_mission.py --profile "{naam_van_jouw_profiel}"
        """.strip().replace("{naam_van_jouw_profiel}", p["name"]))
        st.write("De mini-game schrijft je beloning rechtstreeks naar 'profiles.json'.")
        st.warning("Op Streamlit Cloud kun je pygame niet starten. Speel lokaal.")

# ------------------------
# Tab: Shop & Avatar
# ------------------------
with shop_tab:
    st.header("🛍️ Shop & Avatar")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Avatar")
            st.markdown(f"<div style='font-size:80px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Items:", ", ".join(p["items"]) if p["items"] else "Geen")
            st.markdown("---")
            st.subheader("Kies basis-avatar")
            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(p["avatar"].get("base", BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                p["avatar"]["base"] = new_base
                save_event(p, f"Basis avatar ingesteld op {new_base}")
                autosave()
                st.success("Avatar basis aangepast")

        with c2:
            st.subheader("Shop items")
            st.write(f"Jouw geld: €{p['money']}")
            for item, info in SHOP_ITEMS.items():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.write(f"{info['emoji']} **{item}** — €{info['price']} (+{info['xp']} XP)")
                with cols[1]:
                    owned = item in p["items"]
                    st.write("✅" if owned else "❌")
                with cols[2]:
                    if not owned:
                        if st.button(f"Koop {item}", key=f"buy_{item}"):
                            if p["money"] >= info["price"]:
                                p["money"] -= info["price"]
                                p["items"].append(item)
                                p["avatar"][info["pos"]] = info["emoji"]
                                p["xp"] += info["xp"]
                                save_event(p, f"Gekocht {item}")
                                autosave()
                                st.success(f"{item} gekocht!")
                            else:
                                st.error("Niet genoeg geld")

# ------------------------
# Tab: Rang & Historie
# ------------------------
with rank_tab:
    st.header("📜 Rang & Geschiedenis")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"{p['name']} — Rang: {get_rank(p['xp'])} — Level: {p['level']}")
        st.markdown(f"<div style='font-size:64px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
        st.markdown("### Statistieken")
        st.write(f"• Geld: €{p['money']}")
        st.write(f"• XP: {p['xp']}")
        st.write(f"• Items: {', '.join(p['items']) if p['items'] else 'Geen'}")
        st.markdown("### Geschiedenis (laatste 40)")
        for ev in list(reversed(p["history"]))[:40]:
            st.write(f"{ev['time']} — {ev['text']}")

# Ensure save each run
autosave()
