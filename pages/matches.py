import streamlit as st
from services.database import initialize_database, get_matches, add_match, update_match_status, get_tickets
from services.ui import setup, page_header

setup("Matchs", "Créer les matchs et suivre l'affluence générée par la billetterie.")
initialize_database()

page_header("⚽","Matchs","Pilotez les rencontres, la capacité et l’affluence.")

with st.expander("➕ Créer un match", expanded=True):
    a, b = st.columns(2)
    adversaire = a.text_input("Adversaire")
    date_match = b.date_input("Date du match")
    c, d = st.columns(2)
    competition = c.text_input("Compétition", "Championnat")
    capacite = d.number_input("Capacité", min_value=1000, max_value=100000, value=30000, step=500)

    if st.button("Créer le match", type="primary"):
        if adversaire.strip():
            add_match(adversaire.strip(), str(date_match), competition.strip(), int(capacite))
            st.success("Match créé. Il est maintenant disponible dans Billetterie et Expérience.")
            st.rerun()
        else:
            st.warning("Renseigne l'adversaire.")

matches = get_matches()

if matches.empty:
    st.info("Aucun match enregistré.")
    st.stop()

display = matches.copy()
display["remplissage_%"] = ((display["spectateurs"].fillna(0) / display["capacite"].replace(0, 1)) * 100).round(1)

st.dataframe(display, use_container_width=True, hide_index=True)

st.subheader("Modifier le statut")
options = {
    f'#{int(row["id"])} — {row["adversaire"]} — {row["date_match"]}': int(row["id"])
    for _, row in matches.iterrows()
}
selected = st.selectbox("Match", list(options.keys()))
status = st.selectbox("Statut", ["À venir", "Ouvert", "Complet", "Terminé", "Annulé"])
if st.button("Mettre à jour le statut"):
    update_match_status(options[selected], status)
    st.success("Statut mis à jour.")
    st.rerun()

tickets = get_tickets()
st.metric("Places vendues enregistrées", int(tickets["quantite"].fillna(0).sum()) if not tickets.empty else 0)
