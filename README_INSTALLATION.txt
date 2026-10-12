FANPULSE 360 — RESTAURATION COHÉRENTE

IMPORTANT
- La base existante est conservée dans :
  C:\Users\diallo\FanPulse360_Data\fanpulse.db
- Les 300 supporters existants ne sont pas supprimés.

INSTALLATION
1. Fermer Streamlit avec Ctrl+C.
2. Faire une copie de C:\Users\diallo\Desktop\FanPulse360.
3. Copier le contenu du ZIP dans C:\Users\diallo\Desktop\FanPulse360.
4. Accepter le remplacement de app.py, pages/, services/ et .streamlit/.
5. Ne pas supprimer C:\Users\diallo\FanPulse360_Data.
6. Installer si nécessaire :
   python -m pip install -r requirements.txt
7. Lancer :
   python -m streamlit run app.py

TEST
- CRM -> sélectionner un supporter -> Ouvrir dans Fan 360.
- Fan 360 -> Ajouter une vente -> Billetterie.
- Une vente met à jour le supporter ET l'affluence du match.
- Expérience 1/5 ou 2/5 -> action CRM automatique.
- Campagnes -> audience réelle persistée.
- Dashboard -> KPI recalculés depuis SQLite.
- IA -> Ollama local s'il est lancé, sinon analyse data intégrée.
