import streamlit as st
from services.database import initialize_database, get_supporters, get_matches, add_ticket, get_tickets
from services.ui import setup, page_header, fan_label, safe_switch

setup("Billetterie", "Enregistrer une vente et mettre à jour automatiquement le supporter, le match et le dashboard.")
initialize_database()

page_header("🎟️","Billetterie","Enregistrez les ventes et mettez à jour automatiquement la valeur fan et l’affluence.")

fans = get_supporters()
matches = get_matches()

if matches.empty:
    st.warning("Aucun match n'est encore enregistré.")
    if st.button("⚽ Aller à la page Matchs"):
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
    f'#{int(row["id"])} — {row["adversaire"]} — {row["date_match"]}': int(row["id"])
    for _, row in matches.iterrows()
}
match_choice = st.selectbox("Match", list(match_map.keys()))

a, b, c = st.columns(3)
qty = a.number_input("Nombre de places", 1, 20, 1)
amount = b.number_input("Montant total (€)", 0.0, 5000.0, 35.0, step=5.0)
ticket_type = c.selectbox("Type", ["Standard", "Premium", "VIP", "Hospitalité"])

if st.button("💳 Enregistrer la vente", type="primary"):
    add_ticket(supporter_id, match_map[match_choice], int(qty), float(amount), ticket_type)
    st.success("Vente enregistrée. Fan 360, Matchs et Tableau de bord ont été mis à jour.")
    st.rerun()

tickets = get_tickets()
if not tickets.empty:
    c1, c2 = st.columns(2)
    c1.metric("CA enregistré", f'{tickets["montant"].fillna(0).sum():,.0f} €')
    c2.metric("Places vendues", int(tickets["quantite"].fillna(0).sum()))
    st.dataframe(tickets, use_container_width=True, hide_index=True)
