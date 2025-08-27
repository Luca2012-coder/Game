# la_famiglia_game.py
import streamlit as st
import json
import random
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path("profiles.json")
st.set_page_config(page_title="La Famiglia – Parody Game", page_icon="🍝", layout="wide")

# Shop items with position on avatar: top, eyes, neck, torso, feet, side
SHOP_ITEMS = {
    "Fedora": {"price": 150, "emoji": "🎩", "pos": "top", "xp": 12},
    "Sunglasses": {"price": 200, "emoji": "🕶️", "pos": "eyes", "xp": 18},
    "Gold Chain": {"price": 400, "emoji": "📿", "pos": "neck", "xp": 40},
    "Fancy Suit": {"price": 700, "emoji": "🤵", "pos": "torso", "xp": 70},
    "Black Boots": {"price": 180, "emoji": "👞", "pos": "feet", "xp": 18},
    "Motorcycle": {"price": 1200, "emoji": "🏍️", "pos": "side", "xp": 120},
    "Sigaar": {"price": 250, "emoji": "🪵", "pos": "side", "xp": 20}
}

RANKS = [
    (0, "Rekruut"),
    (51, "Soldato"),
    (151, "Capo"),
    (301, "Consigliere"),
    (601, "Underboss"),
    (1001, "Boss")
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
        "money": 150,
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
        a.get("top",""),
        f"{a.get('base','😎')}{a.get('eyes','')}",
        a.get("neck",""),
        a.get("torso",""),
        a.get("feet","")
    ]
    side = a.get("side","")
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
st.sidebar.markdown("Tips: Maak een profiel, vul sollicitatie volledig in, upgrade avatar met shop items.")

# ------------------------
# Tabs
# ------------------------
tab_profile, tab_mission, tab_shop, tab_rank = st.tabs(["📝 Sollicitatie & Profiel", "🎯 Dagelijkse missie", "🛍️ Shop & Avatar", "📜 Rang & Historie"])

# ------------------------
# Tab: Sollicitatie & Profiel
# ------------------------
with tab_profile:
    st.header("📝 Sollicitatieformulier")
    st.caption("Vul volledig in. Kans op afwijzing is reëel!")

    with st.form("application_form", clear_on_submit=False):
        name = st.text_input("Volledige naam", value=(st.session_state["current_profile"] or ""))
        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=25)
        bio = st.text_area("Korte introductie / bio", value="Ik wil meedoen omdat...")

        experience = st.multiselect("Ervaring", ["Pizzabakken", "Logistiek", "Onderhandelen", "Discretie", "PR", "Technische hulp (IT)", "Financieel inzicht", "Kok / keuken"])
        specialties = st.multiselect("Specialiteiten", ["Pizzabakken", "Discretie", "Netwerken", "Financieel inzicht", "PR", "Onderhandelen"])

        calc = st.number_input("Rekentest: 17 + 23 = ?", value=0)
        loyal = st.checkbox("Ik ga professioneel en discreet om met opdrachten (loyale verklaring)")

        motivation = st.text_area("Motivatie (uitgebreid is beter)")

        submitted = st.form_submit_button("Verstuur sollicitatie")

    if submitted:
        form = {"name": name.strip(), "age": int(age), "bio": bio.strip(),
                "experience": experience, "specialties": specialties,
                "calc": int(calc), "loyal": bool(loyal), "motivation": motivation.strip()}

        # Beoordeling
        score = 0
        if 18 <= form["age"] <= 80: score += 2
        if len(form["motivation"])>100: score+=3
        elif len(form["motivation"])>40: score+=2
        elif len(form["motivation"])>10: score+=1
        for e in form["experience"]: score += 1
        for s in form["specialties"]: score +=1
        if form["calc"]==40: score+=2
        if form["loyal"]: score+=3
        judge=random.random()
        if judge<0.05: score-=5
        elif judge>0.95: score+=3

        if score>=10: status="Aangenomen"
        elif score>=5: status="Op proef"
        else: status="Afgewezen"

        if name.strip() not in st.session_state["profiles"]:
            profile = new_profile_struct(name.strip(), age, bio.strip())
            st.session_state["profiles"][name.strip()] = profile
        profile = st.session_state["profiles"][name.strip()]
        profile["application"] = {"form": form, "score": score, "status": status, "when": datetime.now().isoformat(timespec="seconds")}
        save_event(profile, f"Sollicitatie ingediend — status: {status}")

        if status=="Aangenomen":
            profile["money"]+=50; profile["xp"]+=20
            save_event(profile,"Aangenomen: +€50 +20 XP")
            st.success(f"Gefeliciteerd — {status}! Je krijgt €50 en 20 XP.")
        elif status=="Op proef":
            profile["money"]+=20; profile["xp"]+=8
            save_event(profile,"Op proef: +€20 +8 XP")
            st.warning("Op proef. Presteer goed in dagelijkse missie om te bewijzen.")
        else:
            save_event(profile,"Afgewezen bij sollicitatie")
            st.error("Helaas — afgewezen. Probeer later opnieuw.")

        st.session_state["current_profile"] = name.strip()
        autosave()

# ------------------------
# Tab: Dagelijkse missie
# ------------------------
with tab_mission:
    st.header("🎯 Dagelijkse missie")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        today_str = date.today().isoformat()
        if profile.get("last_mission_date")==today_str:
            st.info("Je hebt de missie al gedaan vandaag. Kom morgen terug, soldaat.")
        else:
            st.subheader("Vandaag's missie:")
            missions = [
                ("Geld innen bij pizzawinkel 🍕", (10,30),(5,15)),
                ("Corrupte politie dreigen 👮", (12,28),(6,14)),
                ("Wijn smokkelen 🍷", (8,25),(4,12)),
                ("Los ruzie op met concurrent 🔪", (9,26),(5,13)),
                ("Bescherm casino tegen afpersing 🎰", (15,30),(7,18))
            ]
            mission = random.choice(missions)
            st.write(mission[0])
            if st.button("Uitvoeren missie"):
                reward = random.randint(*mission[1])
                xp_gain = random.randint(*mission[2])
                profile["money"]+=reward
                profile["xp"]+=xp_gain
                profile["last_mission_date"]=today_str
                save_event(profile,f"Dagelijkse missie gedaan: +€{reward}, +{xp_gain} XP")
                profile["level"]=1+profile["xp"]//50
                st.success(f"Missie voltooid! +€{reward}, +{xp_gain} XP")

# ------------------------
# Tab: Shop & Avatar
# ------------------------
with tab_shop:
    st.header("🛍️ Shop & Avatar")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        col1,col2 = st.columns([1,2])
        with col1:
            st.subheader("Avatar")
            st.markdown(f"<div style='font-size:80px; white-space:pre'>{render_avatar(profile)}</div>", unsafe_allow_html=True)
            st.write("Items:", ", ".join(profile["items"]) if profile["items"] else "Geen")
            st.markdown("---")
            st.subheader("Kies basis-avatar")
            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS,index=BASE_AVATARS.index(profile["avatar"].get("base",BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                profile["avatar"]["base"]=new_base
                save_event(profile,f"Basis avatar ingesteld op {new_base}")
                autosave()
                st.success("Avatar basis aangepast")

        with col2:
            st.subheader("Shop items")
            st.write(f"Jouw geld: €{profile['money']}")
            for item, info in SHOP_ITEMS.items():
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.write(f"{info['emoji']} **{item}** — €{info['price']} (+{info['xp']} XP)")
                with cols[1]:
                    owned = item in profile["items"]
                    st.write("✅" if owned else "❌")
                with cols[2]:
                    if not owned:
                        if st.button(f"Koop {item}", key=f"buy_{item}"):
                            if profile["money"]>=info["price"]:
                                profile["money"]-=info["price"]
                                profile["items"].append(item)
                                # Update avatar layer
                                profile["avatar"][info["pos"]]=info["emoji"]
                                profile["xp"]+=info["xp"]
                                save_event(profile,f"Gekocht {item}")
                                autosave()
                                st.success(f"{item} gekocht!")
                            else:
                                st.error("Niet genoeg geld")

# ------------------------
# Tab: Rang & Historie
# ------------------------
with tab_rank:
    st.header("📜 Rang & Geschiedenis")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"{profile['name']} — Rang: {get_rank(profile['xp'])} — Level: {profile['level']}")
        st.markdown("<h2>Avatar</h2>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:64px; white-space:pre'>{render_avatar(profile)}</div>",unsafe_allow_html=True)
        st.markdown("### Statistieken")
        st.write(f"• Geld: €{profile['money']}")
        st.write(f"• XP: {profile['xp']}")
        st.write(f"• Items: {', '.join(profile['items']) if profile['items'] else 'Geen'}")
        st.markdown("### Geschiedenis (laatste 30)")
        for ev in list(reversed(profile["history"]))[:30]:
            st.write(f"{ev['time']} — {ev['text']}")

# ------------------------
autosave()
