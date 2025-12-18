import streamlit as st
import random

st.set_page_config(page_title="Mini BitLife", page_icon="🧬")

# =====================
# SESSION STATE INIT
# =====================
if 'leeftijd' not in st.session_state:
    st.session_state.leeftijd = 0
    st.session_state.maand = 1
    st.session_state.geld = 1000
    st.session_state.geluk = 50
    st.session_state.gezondheid = 50
    st.session_state.studiejaren = 0
    st.session_state.max_leeftijd = random.randint(80, 120)
    st.session_state.dood = False
    st.session_state.ziekte = None
    st.session_state.ziekte_ernst = 0

# =====================
# KEUZES
# =====================
keuzes = [
    "Werken",
    "Studeren",
    "Sporten",
    "Feesten",
    "Vrijwilligerswerk",
    "Sparen",
    "Riskante actie",
    "Relatie beginnen",
    "Gezond eten",
    "Huis kopen",
    "Reizen",
    "Niks doen",
    "Dokter bezoeken"
]

# =====================
# ZIEKTES
# =====================
ziektes = [
    ("Griep", 5),
    ("Burn-out", 7),
    ("Longontsteking", 10),
    ("Hartproblemen", 12),
    ("Mysterieus virus", 15)
]

# =====================
# LEVENSKEUZE
# =====================
def levenskeuze(keuze):
    # ---- WERKEN ----
    if keuze == "Werken":
        if st.session_state.leeftijd < 21:
            st.warning("❌ Je bent te jong om te werken!")
            return
        salaris = (
            500 +
            st.session_state.studiejaren * 200 +
            st.session_state.geluk * 5
        )
        st.session_state.geld += salaris
        st.session_state.geluk -= 5
        st.success(f"💼 Je verdiende €{salaris}")

    # ---- STUDEREN ----
    elif keuze == "Studeren":
        st.session_state.studiejaren += 1
        st.session_state.geluk += 3
        st.session_state.geld -= 200
        st.success("📚 Je hebt een jaar gestudeerd!")

    elif keuze == "Sporten":
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50

    elif keuze == "Feesten":
        st.session_state.geluk += 10
        st.session_state.gezondheid -= 5

    elif keuze == "Vrijwilligerswerk":
        st.session_state.geluk += 5

    elif keuze == "Sparen":
        st.session_state.geld += 200
        st.session_state.geluk -= 3

    elif keuze == "Riskante actie":
        st.session_state.geld += random.randint(-300, 1000)
        schade = random.randint(0, 30)
        st.session_state.gezondheid -= schade
        if schade > 20:
            creatieve_dood("domme_actie")

    elif keuze == "Relatie beginnen":
        st.session_state.geluk += 8
        st.session_state.geld -= random.randint(0, 150)

    elif keuze == "Gezond eten":
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50

    elif keuze == "Huis kopen":
        st.session_state.geld -= 500
        st.session_state.geluk += 10

    elif keuze == "Reizen":
        st.session_state.geld -= 300
        st.session_state.geluk += 10

    elif keuze == "Niks doen":
        st.session_state.geluk -= 5
        st.session_state.gezondheid -= 5

    elif keuze == "Dokter bezoeken":
        if st.session_state.ziekte:
            kosten = st.session_state.ziekte_ernst * 50
            if st.session_state.geld >= kosten:
                st.session_state.geld -= kosten
                st.session_state.ziekte = None
                st.session_state.ziekte_ernst = 0
                st.success("🏥 Je bent genezen!")
            else:
                st.warning("❌ Niet genoeg geld voor behandeling!")
        else:
            st.info("Je bent niet ziek.")

    # Grenzen
    st.session_state.gezondheid = max(0, min(100, st.session_state.gezondheid))
    st.session_state.geluk = max(0, min(100, st.session_state.geluk))
    st.session_state.geld = max(0, st.session_state.geld)

# =====================
# CREATIVE DOOD & KRANTENKOP
# =====================
def krantenkop(oorzaak):
    if oorzaak == "gezondheid":
        koppen = [
            "📰 SCHOK: Gezondheid genegeerd, leven eindigt tragisch",
            "📰 LOKALE INWONER OVERLEDEN NA JAREN SLECHTE KEUZES",
            "📰 ARTSEN MACHTELOOS: levensstijl eist tol",
            "📰 FEESTEN TOT HET EINDE – LETTERLIJK"
        ]
    elif oorzaak == "ouderdom":
        koppen = [
            "📰 LEGENDE OVERLIJDT NA LANG EN VOL LEVEN",
            "📰 EEUW BIJNA GEHAALD: rustig overlijden",
            "📰 STAD NEEMT AFSCHEID VAN EEUWIGE OVERLEVER",
            "📰 TIJD HAALDE HEM EINDELIJK IN"
        ]
    elif oorzaak == "domme_actie":
        koppen = [
            "📰 DARWIN AWARD UITGEREIKT NA DOMME ACTIE",
            "📰 ‘DIT GAAT VAST GOED’ GING NIET GOED",
            "📰 RISICOLOZE ACTIE BLEEK TOCH RISICOVOL",
            "📰 GETUIGEN: ‘WE ZAGEN DIT AL AANKOMEN’"
        ]
    elif oorzaak == "ziekte":
        koppen = [
            "📰 DODELIJKE ZIEKTE SLAAT TOE",
            "📰 ZIEKENHUIS KON LEVEN NIET REDDEN",
            "📰 EPIDEMIE EIST SLACHTOFFER",
            "📰 ZIEKTE GENEGEERD MET FATALE GEVOLGEN"
        ]
    else:
        koppen = [
            "📰 MYSTERIEUZE DOOD SCHOKT GEMEENSCHAP",
            "📰 VRAGEN NA ONVERWACHT OVERLIJDEN"
        ]
    return random.choice(koppen)

def creatieve_dood(oorzaak):
    st.session_state.dood = True

    st.title(krantenkop(oorzaak))
    st.divider()

    if oorzaak == "gezondheid":
        berichten = [
            f"Je negeerde je lichaam te lang en overleed op {st.session_state.leeftijd} jaar.",
            f"Na jaren ongezond leven gaf je lichaam het op op {st.session_state.leeftijd} jaar.",
            f"Je gezondheid was een waarschuwing, geen uitdaging. RIP op {st.session_state.leeftijd} jaar."
        ]
    elif oorzaak == "ouderdom":
        berichten = [
            f"Je stierf vredig na een lang leven van {st.session_state.leeftijd} jaar.",
            f"Je bereikte een indrukwekkende leeftijd van {st.session_state.leeftijd} jaar.",
            f"Je lichaam besloot dat het mooi geweest was na {st.session_state.leeftijd} jaar."
        ]
    elif oorzaak == "domme_actie":
        berichten = [
            f"Je laatste actie was ook je slechtste. Overleden op {st.session_state.leeftijd} jaar.",
            f"Je dacht dat je onsterfelijk was. Dat was je niet.",
            f"Je won de Darwin Award op {st.session_state.leeftijd} jaar."
        ]
    elif oorzaak == "ziekte":
        berichten = [
            f"Je overleed aan {st.session_state.ziekte} op {st.session_state.leeftijd} jaar.",
            f"De ziekte {st.session_state.ziekte} werd je fataal.",
            f"Artsen deden wat ze konden, maar {st.session_state.ziekte} won."
        ]
    else:
        berichten = [
            f"Je overleed plotseling op {st.session_state.leeftijd} jaar."
        ]

    st.error("💀 OVERLEDEN")
    st.write(random.choice(berichten))

    st.divider()
    st.subheader("📊 Eindstatistieken")
    st.write(f"🎂 Leeftijd: {st.session_state.leeftijd}")
    st.write(f"💰 Geld: €{st.session_state.geld}")
    st.write(f"😊 Geluk: {st.session_state.geluk}")
    st.write(f"❤️ Gezondheid: {st.session_state.gezondheid}")
    st.write(f"📚 Studiejaren: {st.session_state.studiejaren}")

# =====================
# UI
# =====================
st.title("🧬 Mini BitLife")

st.write(
    f"🎂 Leeftijd: {st.session_state.leeftijd} | "
    f"💰 Geld: €{st.session_state.geld} | "
    f"😊 Geluk: {st.session_state.geluk} | "
    f"❤️ Gezondheid: {st.session_state.gezondheid} | "
    f"📚 Studie: {st.session_state.studiejaren}"
)
st.write(f"📆 Maand {st.session_state.maand} van jaar {st.session_state.leeftijd + 1}")

# =====================
# SPELEN
# =====================
if not st.session_state.dood:
    keuze = st.radio("Wat wil je doen?", keuzes)

    if st.button("Bevestig keuze"):
        levenskeuze(keuze)
        st.session_state.maand += 1

        # Ziekte kans 25% per jaar (na december)
        if st.session_state.maand > 12:
            st.session_state.maand = 1
            st.session_state.leeftijd += 1
            if st.session_state.ziekte is None and random.random() < 0.25:
                ziekte, ernst = random.choice(ziektes)
                st.session_state.ziekte = ziekte
                st.session_state.ziekte_ernst = ernst
                st.warning(f"🦠 Je hebt {ziekte} gekregen!")

        # Effect ziekte
        if st.session_state.ziekte:
            st.session_state.gezondheid -= st.session_state.ziekte_ernst
            st.info(f"🤒 Je lijdt aan {st.session_state.ziekte} (-{st.session_state.ziekte_ernst} gezondheid)")

        # Check dood
        if st.session_state.gezondheid <= 0:
            if st.session_state.ziekte:
                creatieve_dood("ziekte")
            else:
                creatieve_dood("gezondheid")
        elif st.session_state.leeftijd >= st.session_state.max_leeftijd:
            creatieve_dood("ouderdom")

        st.experimental_rerun()
