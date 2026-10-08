import streamlit as st
import plotly.graph_objects as go

from services.database import initialize_database, dashboard_stats
from services.ui import setup, page_header, kpi_card, panel_title, safe_switch

setup("Tableau de bord")
initialize_database()
fans,campaigns,actions,tickets,experiences,matches = dashboard_stats()

page_header("📊","Tableau de bord","Performance CRM, billetterie et expérience de la communauté.")

c1,c2,c3,c4 = st.columns(4)
with c1: kpi_card("Supporters",str(len(fans)),"👥","blue","Communauté totale")
with c2:
    eng=float(fans["score_engagement"].mean()) if not fans.empty else 0
    kpi_card("Engagement",f"{eng:.1f}/100","⚡","green","Score moyen")
with c3:
    rev=float(tickets["montant"].fillna(0).sum()) if not tickets.empty else 0
    kpi_card("CA billetterie",f"{rev:,.0f} €","🎟️","purple","Revenus enregistrés")
with c4:
    valid=fans.loc[fans["nb_avis"].fillna(0)>0,"satisfaction_moyenne"]
    sat=f"{valid.mean():.2f}/5" if not valid.empty else "—"
    kpi_card("Satisfaction",sat,"⭐","orange","Avis supporters")

st.write("")
l,r=st.columns([1.45,1])
with l:
    panel_title("⚡ Engagement par segment","Priorisez les audiences à activer")
    grp=fans.groupby("segment_crm",dropna=False)["score_engagement"].mean().sort_values()
    fig=go.Figure(go.Bar(
        x=grp.values,y=[str(x) for x in grp.index],orientation="h",
        marker=dict(color="#29e7a5")
    ))
    fig.update_layout(height=340,margin=dict(l=10,r=10,t=5,b=5),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c9dc"),
        xaxis=dict(range=[0,100],gridcolor="rgba(120,160,200,.09)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with r:
    panel_title("🧩 Répartition CRM","Volume de supporters par segment")
    seg=fans["segment_crm"].fillna("Non défini").value_counts()
    fig2=go.Figure(go.Pie(labels=seg.index,values=seg.values,hole=.62,
        marker=dict(colors=["#1687ff","#29e7a5","#ffb020","#8c5cff","#1edcff","#ff5f8a"]),
        textinfo="none"))
    fig2.update_layout(height=340,margin=dict(l=5,r=5,t=5,b=5),
        paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#dbe8f5"))
    st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

risk=fans[fans["score_engagement"].fillna(0)<30]
low=fans[(fans["nb_avis"].fillna(0)>0)&(fans["satisfaction_moyenne"].fillna(5)<3)]
opened=actions[actions["statut"]!="Terminée"] if not actions.empty else actions
st.markdown("### 🚨 Priorités")
a,b,c=st.columns(3)
a.metric("À réengager",len(risk))
b.metric("Insatisfaits",len(low))
c.metric("Actions ouvertes",len(opened))
if not risk.empty:
    st.dataframe(risk[["prenom","nom","email","segment_crm","score_engagement","total_depense"]].head(12),
                 use_container_width=True,hide_index=True)

x,y,z=st.columns(3)
if x.button("📣 Campagne de réengagement",use_container_width=True):
    st.session_state["campaign_segment"]="À réengager"; safe_switch("pages/campaigns.py")
if y.button("👥 Ouvrir le CRM",use_container_width=True): safe_switch("pages/crm.py")
if z.button("✨ Demander à l'IA",use_container_width=True): safe_switch("pages/ai.py")
