import streamlit as st
from services.database import initialize_database, get_supporters, get_matches, add_experience, get_experiences, create_action
from services.ui import setup, page_header, fan_label, safe_switch

setup("Expérience", "Mesurer la satisfaction et déclencher automatiquement une action CRM en cas d'insatisfaction.")
initialize_database()

page_header("⭐","Expérience","Mesurez la satisfaction et transformez chaque retour en action CRM.")

fans = get_supporters()
matches = get_matches()

if matches.empty:
    st.warning("Crée d'abord un match.")
    if st.button("⚽ Aller à Matchs"):
        safe_switch("pages/matches.py")
    st.stop()

fan_map = {fan_label(row): row["supporter_id"] for _, row in fans.iterrows()}
labels = list(fan_map.keys())
saved_id = st.session_state.get("selected_fan_id")
index = next((i for i, label in enumerate(labels) if fan_map[label] == saved_id), 0)

fan_choice = st.selectbox("Supporter", labels, index=index)
supporter_id = fan_map[fan_choice]
st.session_state["selected_fan_id"] = supporter_id

match_map = {
    f'{row["adversaire"]} — {row["date_match"]}': int(row["id"])
    for _, row in matches.iterrows()
}
match_choice = st.selectbox("Match", list(match_map.keys()))

a, b = st.columns(2)
satisfaction = a.slider("Satisfaction", 1, 5, 4)
nps = b.slider("NPS", 0, 10, 8)
comment = st.text_area("Commentaire", placeholder="Ex. Très bonne ambiance mais attente trop longue à la buvette.")

if st.button("❤️ Enregistrer l'expérience", type="primary"):
    add_experience(supporter_id, match_map[match_choice], satisfaction, nps, comment)
    if satisfaction <= 2:
        create_action(
            supporter_id,
            "Appel",
            f"Rappeler après une satisfaction de {satisfaction}/5. Commentaire : {comment or 'Non renseigné'}",
        )
        st.success("Avis enregistré. Fan 360 est mis à jour et une action CRM a été créée automatiquement.")
    else:
        st.success("Avis enregistré. Fan 360 et le dashboard sont mis à jour.")
    st.rerun()

experiences = get_experiences()
if not experiences.empty:
    st.dataframe(experiences, use_container_width=True, hide_index=True)
