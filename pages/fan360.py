import streamlit as st
from services.database import initialize_database, get_supporters, get_supporter, update_supporter, create_action, get_actions
from services.ui import setup, page_header, fan_label, safe_switch

setup("Fan 360", "Fiche 360° du supporter : valeur, engagement, expérience et actions CRM.")
initialize_database()

fans = get_supporters()
page_header("👤","Fan 360","Vision complète de chaque supporter : engagement, valeur, expérience et actions.")

if fans.empty:
    st.warning("Aucun supporter dans la base.")
    st.stop()

mapping = {fan_label(row): row["supporter_id"] for _, row in fans.iterrows()}
labels = list(mapping.keys())
saved_id = st.session_state.get("selected_fan_id")
index = next((i for i, label in enumerate(labels) if mapping[label] == saved_id), 0)

choice = st.selectbox("Supporter", labels, index=index)
supporter_id = mapping[choice]
st.session_state["selected_fan_id"] = supporter_id
fan = get_supporter(supporter_id)

st.markdown(
    f"""<div class="fp-card">
    <h2 style="margin-top:0">{fan["prenom"]} {fan["nom"]}</h2>
    <span class="fp-accent">{fan.get("segment_crm","")}</span>
    <span class="fp-muted"> • {fan.get("ville","")} • {fan.get("email","")}</span>
    </div>""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Fan Score", f'{float(fan.get("score_engagement",0) or 0):.0f}/100')
c2.metric("Matchs", int(float(fan.get("nb_matchs",0) or 0)))
c3.metric("Valeur", f'{float(fan.get("total_depense",0) or 0):,.0f} €')
c4.metric("Satisfaction", f'{float(fan.get("satisfaction_moyenne",0) or 0):.1f}/5')

left, right = st.columns(2)

with left:
    st.subheader("Profil")
    st.write(f"**Canal préféré :** {fan.get('canal_prefere','—')}")
    st.write(f"**Places :** {int(float(fan.get('nb_places',0) or 0))}")
    st.write(f"**Achats :** {int(float(fan.get('nb_achats',0) or 0))}")
    st.write(f"**Taux de présence :** {float(fan.get('taux_presence',0) or 0):.0f}%")
    st.write(f"**NPS moyen :** {float(fan.get('nps_moyen',0) or 0):.1f}")

with right:
    st.subheader("Mise à jour CRM")
    segments = ["VIP", "Fidèle", "Régulier", "Occasionnel", "Nouveau", "À réengager"]
    channels = ["Email", "SMS", "Application", "Téléphone", "Réseaux sociaux"]
    current_segment = fan.get("segment_crm")
    current_channel = fan.get("canal_prefere")

    new_segment = st.selectbox(
        "Segment",
        segments,
        index=segments.index(current_segment) if current_segment in segments else 0,
    )
    new_channel = st.selectbox(
        "Canal préféré",
        channels,
        index=channels.index(current_channel) if current_channel in channels else 0,
    )
    note = st.text_area("Note CRM", fan.get("note_crm", "") or "")

    if st.button("💾 Enregistrer le profil", type="primary"):
        update_supporter(supporter_id, new_segment, new_channel, note)
        st.success("Profil enregistré.")
        st.rerun()

st.divider()
st.subheader("➕ Créer une action CRM")
a, b = st.columns([1, 2])
action_type = a.selectbox("Type", ["Email", "Appel", "Réactivation", "Invitation VIP", "Offre billetterie", "Questionnaire"])
description = b.text_input("Description", placeholder="Ex. Appeler pour proposer l'offre hospitalité")
if st.button("Créer l'action"):
    create_action(supporter_id, action_type, description or action_type)
    st.success("Action CRM créée.")
    st.rerun()

actions = get_actions(supporter_id)
if not actions.empty:
    st.dataframe(actions[["type_action","description","statut","date_creation"]], use_container_width=True, hide_index=True)

st.divider()
st.subheader("Continuer avec ce supporter")
x, y, z = st.columns(3)
if x.button("📣 Créer une campagne", use_container_width=True):
    st.session_state["campaign_segment"] = fan.get("segment_crm")
    safe_switch("pages/campaigns.py")
if y.button("🎟️ Ajouter une vente", use_container_width=True):
    safe_switch("pages/ticketing.py")
if z.button("❤️ Ajouter une expérience", use_container_width=True):
    safe_switch("pages/experience.py")
