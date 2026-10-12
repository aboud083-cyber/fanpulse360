import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path.home() / "FanPulse360_Data" / "fanpulse.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# ======================================================
# TABLE DES MATCHS DE BILLETTERIE
# ======================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS billetterie_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domicile TEXT NOT NULL,
    exterieur TEXT NOT NULL,
    date_match TEXT NOT NULL,
    stade TEXT,
    capacite INTEGER,
    statut TEXT DEFAULT 'À venir'
)
""")


# ======================================================
# TABLE DES BILLETS
# ======================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS billets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ticket_id TEXT UNIQUE NOT NULL,

    supporter_id TEXT,

    match_id INTEGER NOT NULL,

    tribune TEXT NOT NULL,
    bloc TEXT,
    rang TEXT,
    place TEXT,

    prix REAL NOT NULL,

    statut TEXT DEFAULT 'Valide',

    qr_token TEXT UNIQUE NOT NULL,

    date_achat TEXT NOT NULL,

    date_scan TEXT,

    FOREIGN KEY (match_id)
        REFERENCES billetterie_matches(id)
)
""")


# ======================================================
# TABLE DES SCANS
# ======================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS scans_billets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ticket_id TEXT NOT NULL,

    date_scan TEXT NOT NULL,

    porte TEXT,

    resultat TEXT NOT NULL
)
""")


# ======================================================
# MATCHS DE DÉMONSTRATION
# ======================================================

cursor.execute("""
SELECT COUNT(*)
FROM billetterie_matches
""")

nb_matchs = cursor.fetchone()[0]


if nb_matchs == 0:

    matchs_demo = [

        (
            "Racing Strasbourg",
            "Lille",
            "2027-02-15 20:45",
            "Stade de la Meinau",
            30000,
            "À venir"
        ),

        (
            "Racing Strasbourg",
            "Lyon",
            "2027-03-01 17:00",
            "Stade de la Meinau",
            30000,
            "À venir"
        ),

        (
            "Racing Strasbourg",
            "Marseille",
            "2027-03-15 21:00",
            "Stade de la Meinau",
            30000,
            "À venir"
        )

    ]

    cursor.executemany("""
        INSERT INTO billetterie_matches (
            domicile,
            exterieur,
            date_match,
            stade,
            capacite,
            statut
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, matchs_demo)


conn.commit()
conn.close()


print("======================================")
print(" BILLETTERIE FANPULSE360")
print("======================================")
print()
print("✅ Base billetterie créée avec succès")
print()
print("Base :", DB_PATH)
print()
print("Tables créées :")
print("- billetterie_matches")
print("- billets")
print("- scans_billets")
print()
print("🎟️ 3 matchs de démonstration disponibles")