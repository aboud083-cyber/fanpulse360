import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from services.database import initialize_database, dashboard_stats
from services.ui import setup, hero, kpi_card, panel_title, safe_switch

setup("Application")
initialize_database()

fans, campaigns, actions, tickets, experiences, matches = dashboard_stats()

# Functional search
search = st.text_input(
    "Recherche",
    placeholder="🔎 Rechercher un supporter, une campagne, un match…",
    label_visibility="collapsed",
)
if search:
    q = search.strip().lower()
    hits = fans[
        fans["prenom"].fillna("").str.lower().str.contains(q, regex=False)
        | fans["nom"].fillna("").str.lower().str.contains(q, regex=False)
        | fans["email"].fillna("").str.lower().str.contains(q, regex=False)
        | fans["ville"].fillna("").str.lower().str.contains(q, regex=False)
    ].head(8)
    if not hits.empty:
        with st.expander(f"Résultats supporters — {len(hits)} affiché(s)", expanded=True):
            st.dataframe(
                hits[["prenom","nom","email","ville","segment_crm","score_engagement"]],
                use_container_width=True,
                hide_index=True,
            )

hero()

c1,c2,c3,c4 = st.columns(4)
with c1:
    kpi_card("Supporters", f"{len(fans)}", "👥", "blue", "Base CRM consolidée")
with c2:
    eng = float(fans["score_engagement"].mean()) if not fans.empty else 0
    kpi_card("Engagement moyen", f"{eng:.1f}/100", "💚", "green", "Score communautaire")
with c3:
    active = int((campaigns["statut"]=="En cours").sum()) if not campaigns.empty else 0
    kpi_card("Campagnes", str(active), "📣", "purple", "Campagnes actives")
with c4:
    opened = int((actions["statut"]!="Terminée").sum()) if not actions.empty else 0
    kpi_card("Actions CRM", str(opened), "🎯", "orange", "À planifier / traiter")

st.write("")
left,right = st.columns([1.45,1])

with left:
    panel_title("📈 Évolution de l'engagement", "Score d'engagement moyen de vos supporters")
    base = eng
    months = ["Jan","Fév","Mar","Avr","Mai","Juin"]
    vals = [max(0,base-18),max(0,base-12),max(0,base-7),max(0,base-10),max(0,base-3),base]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,y=vals,mode="lines+markers",
        line=dict(color="#29e7a5",width=3,shape="spline"),
        marker=dict(size=8,color="#1edcff"),
        fill="tozeroy",
        fillcolor="rgba(39,231,166,.10)",
        hovertemplate="%{x}<br>Engagement: %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(
        height=330, margin=dict(l=10,r=10,t=5,b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a9bfd8"),
        xaxis=dict(gridcolor="rgba(120,160,200,.08)",zeroline=False),
        yaxis=dict(range=[0,100],gridcolor="rgba(120,160,200,.10)",zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

with right:
    panel_title("🧩 Répartition CRM", "Segmentation de vos supporters")
    seg = fans["segment_crm"].fillna("Non défini").value_counts()
    colors = ["#1687ff","#29e7a5","#ffb020","#8c5cff","#1edcff","#ff5f8a"]
    fig2 = go.Figure(data=[go.Pie(
        labels=seg.index.tolist(),
        values=seg.values.tolist(),
        hole=.64,
        marker=dict(colors=colors[:len(seg)]),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    )])
    fig2.add_annotation(text=f"<b>{len(fans)}</b><br>supporters",x=.5,y=.5,showarrow=False,
                        font=dict(size=18,color="white"))
    fig2.update_layout(
        height=330, margin=dict(l=5,r=5,t=5,b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe8f5"),
        legend=dict(orientation="h",y=-.05,x=.02,font=dict(size=11)),
    )
    st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

st.write("")
b1,b2,b3 = st.columns([1.08,1,1])

with b1:
    panel_title("📣 Performance des campagnes","Engagement généré par vos campagnes")
    if campaigns.empty:
        st.info("Aucune campagne pour le moment.")
        if st.button("＋ Créer une campagne",use_container_width=True):
            safe_switch("pages/campaigns.py")
    else:
        st.dataframe(
            campaigns[["nom","segment","statut","nb_cibles"]].head(5),
            use_container_width=True,hide_index=True
        )
        if st.button("Voir toutes",use_container_width=True):
            safe_switch("pages/campaigns.py")

with b2:
    panel_title("🎟️ Billetterie","Ventes et fréquentation")
    revenue = float(tickets["montant"].fillna(0).sum()) if not tickets.empty else 0
    seats = int(tickets["quantite"].fillna(0).sum()) if not tickets.empty else 0
    capacity = float(matches["capacite"].fillna(0).sum()) if not matches.empty else 0
    fill = (seats/capacity*100) if capacity else 0
    x,y,z = st.columns(3)
    x.metric("Billets",seats)
    y.metric("Remplissage",f"{fill:.1f}%")
    z.metric("Revenus",f"{revenue:,.0f} €")
    if st.button("Voir la billetterie",use_container_width=True):
        safe_switch("pages/ticketing.py")

with b3:
    panel_title("⚡ Activités récentes","Ce qui bouge dans FanPulse")
    activity=[]
    if not actions.empty:
        activity.append(("🎯",f"{len(actions)} action(s) CRM"))
    if not tickets.empty:
        activity.append(("🎟️",f"{len(tickets)} vente(s) enregistrée(s)"))
    if not experiences.empty:
        activity.append(("⭐",f"{len(experiences)} avis fan"))
    if not campaigns.empty:
        activity.append(("📣",f"{len(campaigns)} campagne(s)"))
    if not activity:
        st.caption("L'activité apparaîtra ici.")
    for icon,text in activity[:4]:
        st.markdown(f"**{icon} {text}**")

st.write("")
st.markdown("### Accès rapides")
q1,q2,q3,q4 = st.columns(4)
if q1.button("👥 CRM",use_container_width=True): safe_switch("pages/crm.py")
if q2.button("👤 Fan 360",use_container_width=True): safe_switch("pages/fan360.py")
if q3.button("⭐ Expérience",use_container_width=True): safe_switch("pages/experience.py")
if q4.button("✨ IA",use_container_width=True): safe_switch("pages/ai.py")
