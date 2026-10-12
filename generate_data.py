import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# ============================================================
# FANPULSE 360 - GENERATEUR DE DONNEES FICTIVES
# ============================================================

fake = Faker("fr_FR")
Faker.seed(42)
random.seed(42)

# Création du dossier data
os.makedirs("data", exist_ok=True)

# ------------------------------------------------------------
# 1. GENERATION DES SUPPORTERS
# ------------------------------------------------------------

NB_SUPPORTERS = 300

villes = [
    ("Paris", "75000"),
    ("Saint-Denis", "93200"),
    ("Boulogne-Billancourt", "92100"),
    ("Montreuil", "93100"),
    ("Créteil", "94000"),
    ("Versailles", "78000"),
    ("Cergy", "95000"),
    ("Aubervilliers", "93300"),
    ("Nanterre", "92000"),
    ("Ivry-sur-Seine", "94200"),
]

canaux = [
    "Email",
    "SMS",
    "Application",
    "Réseaux sociaux"
]

supporters = []

for i in range(1, NB_SUPPORTERS + 1):

    prenom = fake.first_name()
    nom = fake.last_name()

    age = random.randint(18, 70)

    ville, code_postal = random.choice(villes)

    date_inscription = fake.date_between(
        start_date="-4y",
        end_date="today"
    )

    consentement = random.random() < 0.85
    abonne = random.random() < 0.35

    canal = random.choice(canaux)

    supporters.append({
        "supporter_id": f"SUP{i:04d}",
        "prenom": prenom,
        "nom": nom,
        "age": age,
        "ville": ville,
        "code_postal": code_postal,
        "email": f"supporter{i:04d}@example.com",
        "date_inscription": date_inscription,
        "consentement_marketing": consentement,
        "abonne": abonne,
        "canal_prefere": canal
    })

df_supporters = pd.DataFrame(supporters)

# ------------------------------------------------------------
# 2. GENERATION DES MATCHS
# ------------------------------------------------------------

adversaires = [
    "Lyon",
    "Marseille",
    "Lille",
    "Monaco",
    "Nantes",
    "Rennes",
    "Nice",
    "Toulouse",
    "Strasbourg",
    "Lens",
    "Bordeaux",
    "Auxerre"
]

competitions = [
    "Championnat",
    "Championnat",
    "Championnat",
    "Coupe",
    "Europe"
]

matchs = []

date_depart = datetime(2026, 8, 15)

for i, adversaire in enumerate(adversaires, start=1):

    date_match = date_depart + timedelta(days=(i - 1) * 14)

    capacite = 25000

    spectateurs = random.randint(15000, capacite)

    matchs.append({
        "match_id": f"MAT{i:03d}",
        "match": f"Paris United - {adversaire}",
        "date": date_match.strftime("%Y-%m-%d"),
        "adversaire": adversaire,
        "competition": random.choice(competitions),
        "stade": "FanPulse Arena",
        "capacite": capacite,
        "spectateurs": spectateurs,
        "taux_remplissage": round(
            spectateurs / capacite * 100, 2
        )
    })

df_matchs = pd.DataFrame(matchs)

# ------------------------------------------------------------
# 3. GENERATION DE LA BILLETTERIE
# ------------------------------------------------------------

billets = []

ticket_counter = 1

tribunes = [
    "Tribune Nord",
    "Tribune Sud",
    "Tribune Est",
    "Tribune Ouest",
    "Carré VIP"
]

canaux_achat = [
    "Site web",
    "Application",
    "Guichet",
    "Partenaire"
]

for supporter in supporters:

    # Nombre de matchs achetés par supporter
    nombre_matchs = random.choices(
        population=[0, 1, 2, 3, 4, 5, 6],
        weights=[10, 20, 25, 20, 12, 8, 5],
        k=1
    )[0]

    if nombre_matchs == 0:
        continue

    matchs_supporter = random.sample(
        matchs,
        min(nombre_matchs, len(matchs))
    )

    for match in matchs_supporter:

        if supporter["abonne"]:
            categorie = random.choices(
                ["Abonné", "Standard", "VIP"],
                weights=[75, 20, 5],
                k=1
            )[0]
        else:
            categorie = random.choices(
                ["Standard", "VIP", "Hospitalité"],
                weights=[85, 10, 5],
                k=1
            )[0]

        if categorie == "VIP":
            prix = random.randint(120, 250)
            tribune = "Carré VIP"

        elif categorie == "Hospitalité":
            prix = random.randint(180, 350)
            tribune = "Carré VIP"

        elif categorie == "Abonné":
            prix = random.randint(20, 55)
            tribune = random.choice(tribunes[:-1])

        else:
            prix = random.randint(25, 90)
            tribune = random.choice(tribunes[:-1])

        quantite = random.choices(
            [1, 2, 3, 4],
            weights=[60, 30, 7, 3],
            k=1
        )[0]

        montant = prix * quantite

        date_match = datetime.strptime(
            match["date"],
            "%Y-%m-%d"
        )

        jours_avant = random.randint(3, 60)

        date_achat = date_match - timedelta(
            days=jours_avant
        )

        presence = random.random() < 0.88

        billets.append({
            "ticket_id": f"TKT{ticket_counter:05d}",
            "supporter_id": supporter["supporter_id"],
            "email_supporter": supporter["email"],
            "match_id": match["match_id"],
            "match": match["match"],
            "date_achat": date_achat.strftime("%Y-%m-%d"),
            "type_billet": categorie,
            "tribune": tribune,
            "quantite": quantite,
            "prix_unitaire": prix,
            "montant": montant,
            "canal_achat": random.choice(canaux_achat),
            "presence": presence
        })

        ticket_counter += 1

df_billetterie = pd.DataFrame(billets)

# ------------------------------------------------------------
# 4. GENERATION DE LA SATISFACTION
# ------------------------------------------------------------

avis = []

avis_counter = 1

commentaires_positifs = [
    "Très bonne ambiance dans le stade.",
    "Super expérience, je reviendrai.",
    "Entrée rapide et personnel accueillant.",
    "Très bonne organisation du match.",
    "Ambiance exceptionnelle.",
]

commentaires_moyens = [
    "Bonne expérience mais beaucoup d'attente à la buvette.",
    "Ambiance sympa mais accès au stade à améliorer.",
    "Bon match mais restauration trop chère.",
    "Expérience correcte dans l'ensemble.",
]

commentaires_negatifs = [
    "Trop d'attente à l'entrée du stade.",
    "La restauration était trop lente.",
    "Signalétique difficile à comprendre.",
    "Files d'attente beaucoup trop longues.",
    "Expérience décevante au niveau de l'accueil.",
]

for billet in billets:

    # Seuls les supporters présents peuvent répondre
    if not billet["presence"]:
        continue

    # Environ 55 % répondent à l'enquête
    if random.random() > 0.55:
        continue

    note_globale = random.choices(
        [1, 2, 3, 4, 5],
        weights=[3, 7, 20, 40, 30],
        k=1
    )[0]

    accueil = max(
        1,
        min(5, note_globale + random.choice([-1, 0, 0, 1]))
    )

    billetterie_note = max(
        1,
        min(5, note_globale + random.choice([-1, 0, 0, 1]))
    )

    ambiance = max(
        1,
        min(5, note_globale + random.choice([0, 0, 1]))
    )

    restauration = max(
        1,
        min(5, note_globale + random.choice([-2, -1, 0, 0, 1]))
    )

    if note_globale >= 4:
        commentaire = random.choice(commentaires_positifs)

    elif note_globale == 3:
        commentaire = random.choice(commentaires_moyens)

    else:
        commentaire = random.choice(commentaires_negatifs)

    # Approximation NPS cohérente avec la satisfaction
    if note_globale == 5:
        nps = random.randint(9, 10)

    elif note_globale == 4:
        nps = random.randint(7, 9)

    elif note_globale == 3:
        nps = random.randint(5, 7)

    else:
        nps = random.randint(0, 5)

    date_match = datetime.strptime(
        next(
            m["date"]
            for m in matchs
            if m["match_id"] == billet["match_id"]
        ),
        "%Y-%m-%d"
    )

    date_reponse = date_match + timedelta(
        days=random.randint(1, 3)
    )

    avis.append({
        "avis_id": f"SAT{avis_counter:05d}",
        "supporter_id": billet["supporter_id"],
        "email_supporter": billet["email_supporter"],
        "match_id": billet["match_id"],
        "match": billet["match"],
        "date_reponse": date_reponse.strftime("%Y-%m-%d"),
        "note_globale": note_globale,
        "accueil": accueil,
        "billetterie": billetterie_note,
        "ambiance": ambiance,
        "restauration": restauration,
        "nps": nps,
        "commentaire": commentaire,
        "a_recontacter": note_globale <= 2 or nps <= 5
    })

    avis_counter += 1

df_satisfaction = pd.DataFrame(avis)

# ------------------------------------------------------------
# 5. EXPORT DES FICHIERS CSV
# ------------------------------------------------------------

df_supporters.to_csv(
    "data/supporters.csv",
    index=False,
    encoding="utf-8-sig"
)

df_matchs.to_csv(
    "data/matchs.csv",
    index=False,
    encoding="utf-8-sig"
)

df_billetterie.to_csv(
    "data/billetterie.csv",
    index=False,
    encoding="utf-8-sig"
)

df_satisfaction.to_csv(
    "data/satisfaction.csv",
    index=False,
    encoding="utf-8-sig"
)

# ------------------------------------------------------------
# 6. RESUME
# ------------------------------------------------------------

print()
print("=" * 50)
print("FANPULSE 360 - GENERATION TERMINEE")
print("=" * 50)

print(f"Supporters       : {len(df_supporters)}")
print(f"Matchs           : {len(df_matchs)}")
print(f"Billets          : {len(df_billetterie)}")
print(f"Avis satisfaction: {len(df_satisfaction)}")

print()
print(
    "CA billetterie  :",
    round(df_billetterie["montant"].sum(), 2),
    "€"
)

print(
    "Panier moyen    :",
    round(df_billetterie["montant"].mean(), 2),
    "€"
)

if len(df_satisfaction) > 0:
    print(
        "Satisfaction    :",
        round(df_satisfaction["note_globale"].mean(), 2),
        "/ 5"
    )

print()
print("Fichiers créés dans le dossier data/")
print("=" * 50)