import random

# Start van het spel
print("Welkom bij je levenssimulatie!")
naam = input("Wat is je naam? ")
leeftijd = 0
geld = 1000
geluk = 50
gezondheid = 50
max_leeftijd = random.randint(80, 120)

# Lijst van 12 keuzes per maand
maand_keuzes = [
    "1. Werken (+geld, -geluk)",
    "2. Studeren (+geluk, +kans op betere baan)",
    "3. Sporten (+gezondheid, -geld)",
    "4. Feesten (+geluk, -gezondheid)",
    "5. Vrijwilligerswerk (+geluk, -geld)",
    "6. Sparen (+geld, -geluk)",
    "7. Riskante actie doen (+geld, kans op -gezondheid)",
    "8. Relatie beginnen (+geluk, kans op -geld)",
    "9. Gezond eten (+gezondheid, -geld)",
    "10. Huis kopen (-geld, +geluk)",
    "11. Reizen (-geld, +geluk)",
    "12. Niks doen (-geluk, -gezondheid)"
]

# Functie om keuzes te maken
def levenskeuze(geld, geluk, gezondheid):
    print("\nKies een actie:")
    for keuze in maand_keuzes:
        print(keuze)
    
    while True:
        try:
            keuze_num = int(input("Typ het nummer van je keuze (1-12): "))
            if 1 <= keuze_num <= 12:
                break
            else:
                print("Kies een nummer tussen 1 en 12.")
        except:
            print("Typ een geldig nummer.")
    
    # Effecten van keuzes
    if keuze_num == 1:
        geld += 500
        geluk -= 5
    elif keuze_num == 2:
        geluk += 5
        geld += 100
    elif keuze_num == 3:
        gezondheid += 5
        geld -= 50
    elif keuze_num == 4:
        geluk += 10
        gezondheid -= 5
    elif keuze_num == 5:
        geluk += 5
        geld -= 100
    elif keuze_num == 6:
        geld += 200
        geluk -= 5
    elif keuze_num == 7:
        winst = random.randint(-200, 1000)
        geld += winst
        gezondheid -= random.randint(0, 15)
    elif keuze_num == 8:
        geluk += 10
        geld -= random.randint(0, 200)
    elif keuze_num == 9:
        gezondheid += 5
        geld -= 50
    elif keuze_num == 10:
        geluk += 10
        geld -= 500
    elif keuze_num == 11:
        geluk += 10
        geld -= 300
    elif keuze_num == 12:
        geluk -= 5
        gezondheid -= 5

    # Grenzen controleren
    gezondheid = max(0, min(100, gezondheid))
    geluk = max(0, min(100, geluk))
    geld = max(0, geld)
    
    return geld, geluk, gezondheid

# Creatieve dood functie
def creatieve_dood(leeftijd):
    doods_scenario = [
        f"{naam} viel in slaap en werd nooit meer wakker op {leeftijd}-jarige leeftijd.",
        f"{naam} werd beroemd en stierf vredig in zijn/haar mansion op {leeftijd}-jarige leeftijd.",
        f"{naam} werd opgegeten door een gigantische pinguïn op {leeftijd}-jarige leeftijd. (Ja, echt!)",
        f"{naam} stierf lachend tijdens een grap op {leeftijd}-jarige leeftijd.",
        f"{naam} werd een legende en stierf als held op {leeftijd}-jarige leeftijd."
    ]
    print("\nJe leven is voorbij!")
    print(random.choice(doods_scenario))
    print(f"Eindstats: Geld: {geld}, Geluk: {geluk}, Gezondheid: {gezondheid}")

# Simulatie loop
while leeftijd < max_leeftijd and gezondheid > 0:
    leeftijd += 1
    print(f"\n--- Leeftijd: {leeftijd} jaar ---")
    for maand in range(1, 13):
        print(f"\nMaand {maand}")
        geld, geluk, gezondheid = levenskeuze(geld, geluk, gezondheid)
        print(f"Geld: {geld}, Geluk: {geluk}, Gezondheid: {gezondheid}")
        if gezondheid <= 0:
            break

# Dood of einde van leven
creatieve_dood(leeftijd)
