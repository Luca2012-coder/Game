import random

# Start van het spel
print("Welkom bij je levenssimulatie!")
naam = input("Wat is je naam? ")
leeftijd = 0
geld = 1000
geluk = 50
gezondheid = 50

# Functie om keuzes te tonen en effect toe te passen
def levenskeuze(leeftijd, geld, geluk, gezondheid):
    keuzes = [
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

    print("\nKies een actie voor dit jaar:")
    for keuze in keuzes:
        print(keuze)
    
    while True:
        try:
            keuze = int(input("Typ het nummer van je keuze (1-12): "))
            if 1 <= keuze <= 12:
                break
            else:
                print("Kies een nummer tussen 1 en 12.")
        except:
            print("Typ een geldig nummer.")
    
    # Effecten van keuzes
    if keuze == 1:
        geld += 500
        geluk -= 5
    elif keuze == 2:
        geluk += 5
        geld += 100  # kleine bijbaan
    elif keuze == 3:
        gezondheid += 5
        geld -= 50
    elif keuze == 4:
        geluk += 10
        gezondheid -= 5
    elif keuze == 5:
        geluk += 5
        geld -= 100
    elif keuze == 6:
        geld += 200
        geluk -= 5
    elif keuze == 7:
        winst = random.randint(-200, 1000)
        geld += winst
        gezondheid -= random.randint(0, 10)
    elif keuze == 8:
        geluk += 10
        geld -= random.randint(0, 200)
    elif keuze == 9:
        gezondheid += 5
        geld -= 50
    elif keuze == 10:
        geluk += 10
        geld -= 500
    elif keuze == 11:
        geluk += 10
        geld -= 300
    elif keuze == 12:
        geluk -= 5
        gezondheid -= 5

    return geld, geluk, gezondheid

# Simulatie loop
while leeftijd < 80 and gezondheid > 0:
    leeftijd += 1
    print(f"\n--- Leeftijd: {leeftijd} jaar ---")
    geld, geluk, gezondheid = levenskeuze(leeftijd, geld, geluk, gezondheid)
    print(f"Geld: {geld}, Geluk: {geluk}, Gezondheid: {gezondheid}")

print("\nJe leven is voorbij!")
print(f"Leeftijd: {leeftijd}, Geld: {geld}, Geluk: {geluk}, Gezondheid: {gezondheid}")
