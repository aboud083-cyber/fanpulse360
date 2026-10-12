import os
import math
import pandas as pd
import requests

# ============================================================
# FANPULSE 360 - SYNCHRONISATION PYTHON -> AIRTABLE
# ============================================================

TOKEN = os.getenv("AIRTABLE_TOKEN")

if not TOKEN:
    raise ValueError("AIRTABLE_TOKEN introuvable.")

BASE_ID = "app4nr1ZA0uopyhVL"
TABLE_NAME = "Supporters"

URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("Chargement du CRM FanPulse 360...")

crm = pd.read_csv("data/supporters_scored.csv")

print(f"{len(crm)} supporters trouvés.")


# ============================================================
# OUTILS
# ============================================================

def clean(value):
    """Transforme NaN en None pour l'API Airtable."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def bool_value(value):
    """Convertit proprement les valeurs CSV en booléen."""

    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in [
        "true",
        "1",
        "oui",
        "yes"
    ]


# ============================================================
# PREPARATION DES SUPPORTERS
# ============================================================

records = []

for _, row in crm.iterrows():

    supporter_name = f"{row['prenom']} {row['nom']}"

    fields = {
        "Supporter": supporter_name,
        "Supporter ID": clean(row["supporter_id"]),
        "Email": clean(row["email"]),
        "Ville": clean(row["ville"]),
        "Abonné": bool_value(row["abonne"]),
        "Consentement marketing": bool_value(
            row["consentement_marketing"]
        ),
        "Nb matchs": int(row["nb_matchs"]),
        "Total dépensé": float(row["total_depense"]),
        "Satisfaction moyenne": float(
            row["satisfaction_moyenne"]
        ),
        "NPS moyen": float(row["nps_moyen"]),
        "Score engagement": int(row["score_engagement"]),
        "Segment": clean(row["segment_crm"])
    }

    # Taux présence :
    # ton scoring.py l'a converti en pourcentage (ex : 88.5)
    # Airtable attend 0.885 pour afficher 88.5 %
    taux = clean(row["taux_presence"])

    if taux is not None:
        fields["Taux présence"] = float(taux) / 100

    records.append({
        "fields": fields
    })


# ============================================================
# ENVOI PAR LOTS DE 10
# ============================================================

print()
print("Synchronisation avec Airtable...")

success = 0

for i in range(0, len(records), 10):

    batch = records[i:i + 10]

    payload = {
        "records": batch,
        "typecast": True
    }

    response = requests.post(
        URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if response.status_code in [200, 201]:

        success += len(batch)

        print(
            f"OK : {success}/{len(records)} supporters synchronisés"
        )

    else:

        print()
        print("ERREUR AIRTABLE")
        print("Code :", response.status_code)
        print(response.text)

        break


# ============================================================
# RESULTAT
# ============================================================

print()
print("=" * 60)

if success == len(records):

    print("SYNCHRONISATION FANPULSE 360 TERMINEE")
    print(f"{success} supporters envoyés vers Airtable.")

else:

    print(
        f"Synchronisation interrompue : "
        f"{success}/{len(records)} supporters envoyés."
    )

print("=" * 60)