# ⚡ FanPulse 360

Plateforme CRM & Fan Experience développée avec Streamlit, Python et SQLite.

## Fonctionnalités
- CRM supporters et segmentation
- Fiche Fan 360
- Campagnes CRM
- Billetterie
- Matchs
- Expérience / satisfaction
- Tableau de bord
- Analyse IA / data

## Lancer en local

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Déploiement Streamlit Community Cloud

- Repository : ce dépôt GitHub
- Branch : `main`
- Main file path : `app.py`
- Python : `3.12`

Les 300 supporters de démonstration sont initialisés depuis
`data/supporters_scored.csv` lors du premier lancement.

> Remarque : SQLite convient à cette démonstration. Sur Streamlit Community
> Cloud, les écritures locales peuvent être réinitialisées lors d'un reboot
> ou redéploiement. Pour une application multi-utilisateur persistante,
> connecter ensuite une base PostgreSQL/Supabase.

> Ollama local (`localhost:11434`) n'est pas accessible depuis le serveur
> Streamlit Cloud. L'application conserve son analyse data sans Ollama.
