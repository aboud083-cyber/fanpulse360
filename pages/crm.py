import streamlit as st
import pandas as pd
from services.database import initialize_database, get_supporters, get_actions, update_action_status
from services.ui import setup, page_header, fan_label, safe_switch

setup("CRM", "Recherche, segmentation et pilotage opérationnel des supporters.")
initialize_database()

fans = get_supporters()
page_header("👥","CRM","Recherchez, segmentez et pilotez les supporters en temps réel.")

a, b, c = st.columns([2, 1, 1])
query = a.text_input("🔎 Rechercher", placeholder="Nom, prénom, email ou ville")
segments = ["Tous"] + sorted(fans["segment_crm"].dropna().astype(str).unique().tolist())
segment = b.selectbox("Segment", segments)
city_options = ["Toutes"] + sorted(fans["ville"].dropna().astype(str).unique().tolist())
city = c.selectbox("Ville", city_options)

filtered = fans.copy()

if query:
    mask = pd.Series(False, index=filtered.index)
    for col in ["prenom", "nom", "email", "ville"]:
        mask |= filtered[col].fillna("").astype(str).str.contains(query, case=False, regex=False)
    filtered = filtered[mask]

if segment != "Tous":
    filtered = filtered[filtered["segment_crm"] == segment]

if city != "Toutes":
    filtered = filtered[filtered["ville"] == city]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Supporters affichés", len(filtered))
k2.metric("Engagement moyen", f'{filtered["score_engagement"].mean():.1f}/100' if not filtered.empty else "—")
k3.metric("Valeur totale", f'{filtered["total_depense"].fillna(0).sum():,.0f} €')
k4.metric("Abonnés", int(filtered["abonne"].fillna(0).astype(bool).sum()) if not filtered.empty else 0)

show_cols = ["prenom","nom","email","ville","segment_crm","score_engagement","total_depense","canal_prefere"]
show_cols = [x for x in show_cols if x in filtered.columns]
st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

st.divider()
st.subheader("👤 Ouvrir un supporter dans Fan 360")

if filtered.empty:
    st.info("Aucun supporter ne correspond aux filtres.")
else:
    mapping = {fan_label(row): row["supporter_id"] for _, row in filtered.iterrows()}
    choice = st.selectbox("Supporter", list(mapping.keys()))
    if st.button("Ouvrir dans Fan 360", type="primary"):
        st.session_state["selected_fan_id"] = mapping[choice]
        safe_switch("pages/fan360.py")

st.divider()
st.subheader("✅ Actions CRM")
actions = get_actions()

if actions.empty:
    st.info("Aucune action CRM.")
else:
    st.dataframe(actions, use_container_width=True, hide_index=True)
    opened = actions[actions["statut"] != "Terminée"]
    if not opened.empty:
        option_map = {
            f'#{int(row["id"])} — {row.get("prenom","")} {row.get("nom","")} — {row["type_action"]}':
            int(row["id"])
            for _, row in opened.iterrows()
        }
        selected = st.selectbox("Action à clôturer", list(option_map.keys()))
        if st.button("✅ Marquer comme terminée"):
            update_action_status(option_map[selected], "Terminée")
            st.success("Action terminée.")
            st.rerun()
