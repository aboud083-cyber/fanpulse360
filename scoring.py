import pandas as pd

# ============================================================
# FANPULSE 360
# CALCUL DU FAN ENGAGEMENT SCORE
# ============================================================

print("Chargement des données FanPulse 360...")

supporters = pd.read_csv("data/supporters.csv")
billets = pd.read_csv("data/billetterie.csv")
satisfaction = pd.read_csv("data/satisfaction.csv")


# ============================================================
# 1. INDICATEURS BILLETTERIE PAR SUPPORTER
# ============================================================

stats_billets = (
    billets.groupby("supporter_id")
    .agg(
        nb_matchs=("match_id", "nunique"),
        nb_achats=("ticket_id", "count"),
        total_depense=("montant", "sum"),
        nb_places=("quantite", "sum"),
        taux_presence=("presence", "mean"),
        derniere_activite=("date_achat", "max")
    )
    .reset_index()
)


# ============================================================
# 2. INDICATEURS SATISFACTION
# ============================================================

stats_satisfaction = (
    satisfaction.groupby("supporter_id")
    .agg(
        satisfaction_moyenne=("note_globale", "mean"),
        nps_moyen=("nps", "mean"),
        nb_avis=("avis_id", "count")
    )
    .reset_index()
)


# ============================================================
# 3. FUSION DES DONNEES
# ============================================================

crm = supporters.merge(
    stats_billets,
    on="supporter_id",
    how="left"
)

crm = crm.merge(
    stats_satisfaction,
    on="supporter_id",
    how="left"
)


# Supporters n'ayant jamais acheté
crm["nb_matchs"] = crm["nb_matchs"].fillna(0)
crm["nb_achats"] = crm["nb_achats"].fillna(0)
crm["total_depense"] = crm["total_depense"].fillna(0)
crm["nb_places"] = crm["nb_places"].fillna(0)
crm["taux_presence"] = crm["taux_presence"].fillna(0)
crm["nb_avis"] = crm["nb_avis"].fillna(0)

crm["satisfaction_moyenne"] = (
    crm["satisfaction_moyenne"].fillna(0)
)

crm["nps_moyen"] = crm["nps_moyen"].fillna(0)


# ============================================================
# 4. CALCUL DU FAN ENGAGEMENT SCORE /100
# ============================================================

def calculer_score(row):

    score = 0

    # --------------------------------------------------------
    # A. FREQUENCE DES MATCHS : 30 POINTS
    # --------------------------------------------------------

    matchs = row["nb_matchs"]

    if matchs >= 6:
        score += 30
    elif matchs >= 4:
        score += 24
    elif matchs >= 2:
        score += 16
    elif matchs >= 1:
        score += 8


    # --------------------------------------------------------
    # B. VALEUR CLIENT / DEPENSE : 25 POINTS
    # --------------------------------------------------------

    depense = row["total_depense"]

    if depense >= 500:
        score += 25
    elif depense >= 300:
        score += 20
    elif depense >= 150:
        score += 15
    elif depense > 0:
        score += 8


    # --------------------------------------------------------
    # C. ABONNEMENT : 15 POINTS
    # --------------------------------------------------------

    if row["abonne"] == True:
        score += 15


    # --------------------------------------------------------
    # D. PRESENCE AU STADE : 10 POINTS
    # --------------------------------------------------------

    presence = row["taux_presence"]

    if presence >= 0.90:
        score += 10
    elif presence >= 0.70:
        score += 7
    elif presence > 0:
        score += 4


    # --------------------------------------------------------
    # E. SATISFACTION : 10 POINTS
    # --------------------------------------------------------

    satisfaction = row["satisfaction_moyenne"]

    if satisfaction >= 4.5:
        score += 10
    elif satisfaction >= 4:
        score += 8
    elif satisfaction >= 3:
        score += 5
    elif satisfaction > 0:
        score += 2


    # --------------------------------------------------------
    # F. CONSENTEMENT MARKETING : 5 POINTS
    # --------------------------------------------------------

    if row["consentement_marketing"] == True:
        score += 5


    # --------------------------------------------------------
    # G. PARTICIPATION AUX ENQUETES : 5 POINTS
    # --------------------------------------------------------

    if row["nb_avis"] >= 3:
        score += 5
    elif row["nb_avis"] >= 1:
        score += 3


    return min(round(score), 100)


crm["score_engagement"] = crm.apply(
    calculer_score,
    axis=1
)


# ============================================================
# 5. SEGMENTATION CRM
# ============================================================

def segmenter(row):

    score = row["score_engagement"]
    matchs = row["nb_matchs"]

    # Aucun achat
    if matchs == 0:
        return "À réengager"

    if score >= 85:
        return "VIP"

    elif score >= 70:
        return "Fidèle"

    elif score >= 50:
        return "Régulier"

    elif score >= 30:
        return "Occasionnel"

    else:
        return "Nouveau"


crm["segment_crm"] = crm.apply(
    segmenter,
    axis=1
)


# ============================================================
# 6. ARRONDIS
# ============================================================

crm["satisfaction_moyenne"] = (
    crm["satisfaction_moyenne"].round(2)
)

crm["nps_moyen"] = crm["nps_moyen"].round(1)

crm["taux_presence"] = (
    crm["taux_presence"] * 100
).round(1)


# ============================================================
# 7. EXPORT DU CRM ENRICHI
# ============================================================

crm.to_csv(
    "data/supporters_scored.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. AFFICHAGE DES RESULTATS
# ============================================================

print()
print("=" * 60)
print("FANPULSE 360 - FAN ENGAGEMENT SCORING")
print("=" * 60)

print()
print("Nombre de supporters :", len(crm))

print()
print("REPARTITION CRM")
print("-" * 30)

print(
    crm["segment_crm"]
    .value_counts()
    .to_string()
)

print()
print("TOP 10 SUPPORTERS")
print("-" * 60)

top10 = crm[
    [
        "supporter_id",
        "prenom",
        "nom",
        "nb_matchs",
        "total_depense",
        "score_engagement",
        "segment_crm"
    ]
].sort_values(
    "score_engagement",
    ascending=False
).head(10)

print(top10.to_string(index=False))

print()
print("=" * 60)
print("Fichier créé : data/supporters_scored.csv")
print("=" * 60)