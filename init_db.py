from services.database import initialize_database, get_supporters

print("Initialisation de FanPulse 360...")

initialize_database()

supporters = get_supporters()

print("Base FanPulse créée avec succès.")
print(f"{len(supporters)} supporters enregistrés.")
print()
print(supporters[
    [
        "prenom",
        "nom",
        "segment_crm",
        "score_engagement"
    ]
].head())