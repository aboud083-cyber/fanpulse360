import streamlit as st
from services.database import initialize_database, get_supporters, create_campaign, get_campaigns, get_campaign_targets, update_campaign_status
from services.ui import setup, page_header

setup("Campagnes", "Construire une campagne sur une audience CRM réelle et conserver ses cibles dans SQLite.")
initialize_database()

page_header("📣","Campagnes","Créez des activations CRM sur des audiences réelles et mesurables.")

fans = get_supporters()
segments = sorted(fans["segment_crm"].dropna().astype(str).unique().tolist())
preset = st.session_state.get("campaign_segment")
index = segments.index(preset) if preset in segments else 0

a, b = st.columns(2)
segment = a.selectbox("Segment cible", segments, index=index)
channel = b.selectbox("Canal", ["Email", "SMS", "Application", "Réseaux sociaux"])

c, d = st.columns(2)
objective = c.selectbox("Objectif", ["Réengagement", "Billetterie", "Fidélisation", "VIP / Hospitalité", "Satisfaction"])
name = d.text_input("Nom de la campagne", f"{objective} — {segment}")

message = st.text_area(
    "Message",
    f"Bonjour, une expérience exclusive FanPulse vous attend. Cette activation {objective.lower()} est personnalisée pour notre segment {segment}.",
)

target = fans[
    (fans["segment_crm"] == segment) &
    (fans["consentement_marketing"].fillna(1).astype(bool))
]

k1, k2, k3 = st.columns(3)
k1.metric("Audience éligible", len(target))
k2.metric("Engagement moyen", f'{target["score_engagement"].mean():.1f}/100' if not target.empty else "—")
k3.metric("Valeur audience", f'{target["total_depense"].fillna(0).sum():,.0f} €')

with st.expander("Voir l'audience"):
    st.dataframe(target[["prenom","nom","email","score_engagement","total_depense"]], use_container_width=True, hide_index=True)

if st.button("💾 Créer la campagne", type="primary"):
    campaign_id = create_campaign(name, segment, channel, objective, message)
    st.success(f"Campagne #{campaign_id} créée avec {len(target)} cibles réelles.")
    st.rerun()

st.divider()
st.subheader("Pilotage")

campaigns = get_campaigns()
if campaigns.empty:
    st.info("Aucune campagne pour le moment.")
else:
    st.dataframe(campaigns, use_container_width=True, hide_index=True)

    campaign_map = {
        f'#{int(row["id"])} — {row["nom"]} — {row["statut"]}': int(row["id"])
        for _, row in campaigns.iterrows()
    }
    selected = st.selectbox("Campagne", list(campaign_map.keys()))
    campaign_id = campaign_map[selected]
    targets = get_campaign_targets(campaign_id)
    st.caption(f"{len(targets)} cible(s) mémorisée(s) dans cette campagne.")

    with st.expander("Cibles de la campagne"):
        st.dataframe(targets, use_container_width=True, hide_index=True)

    x, y, z = st.columns(3)
    if x.button("✅ Prête", use_container_width=True):
        update_campaign_status(campaign_id, "Prête")
        st.rerun()
    if y.button("🚀 En cours", use_container_width=True):
        update_campaign_status(campaign_id, "En cours")
        st.rerun()
    if z.button("🏁 Terminée", use_container_width=True):
        update_campaign_status(campaign_id, "Terminée")
        st.rerun()
