import json
import urllib.request
import streamlit as st

from services.database import initialize_database, dashboard_stats
from services.ui import setup, page_header, safe_switch

setup("IA", "Analyse FanPulse avec la base réelle. Ollama local est utilisé automatiquement s'il est disponible.")
initialize_database()

page_header("✨","FanPulse AI","Analysez les données CRM et préparez les prochaines actions marketing.")

fans, campaigns, actions, tickets, experiences, matches = dashboard_stats()

def ollama_models():
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [m["name"] for m in payload.get("models", [])]
    except Exception:
        return []

def ask_ollama(model, question, context):
    payload = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu es FanPulse AI, assistant CRM et Fan Experience d'un club sportif. "
                    "Réponds en français, de manière concrète et orientée action. "
                    "Base tes recommandations uniquement sur le contexte FanPulse fourni."
                ),
            },
            {"role": "user", "content": f"CONTEXTE:\n{context}\n\nQUESTION:\n{question}"},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result.get("message", {}).get("content", "")

models = ollama_models()

if models:
    st.success("🟢 Ollama local détecté.")
    model = st.selectbox("Modèle Ollama", models)
else:
    st.info("Ollama n'est pas détecté actuellement. L'analyse data FanPulse reste disponible.")

question = st.text_input("Pose une question", "Quels supporters dois-je réengager et pourquoi ?")

if st.button("✨ Analyser", type="primary"):
    text = question.lower()

    if models:
        segment_counts = fans["segment_crm"].value_counts().to_dict()
        top_value = fans.nlargest(5, "total_depense")[["prenom","nom","segment_crm","score_engagement","total_depense"]].to_dict("records")
        low_eng = fans.nsmallest(10, "score_engagement")[["prenom","nom","segment_crm","score_engagement","total_depense"]].to_dict("records")
        context = {
            "nombre_supporters": len(fans),
            "engagement_moyen": round(float(fans["score_engagement"].mean()), 1),
            "segments": segment_counts,
            "campagnes": len(campaigns),
            "actions_crm": len(actions),
            "ventes": len(tickets),
            "avis": len(experiences),
            "top_valeur": top_value,
            "faible_engagement": low_eng,
        }
        try:
            answer = ask_ollama(model, question, json.dumps(context, ensure_ascii=False, indent=2))
            st.markdown(answer)
        except Exception as exc:
            st.warning(f"Ollama est détecté mais n'a pas répondu : {exc}")

    if "réeng" in text or "reeng" in text:
        result = fans[fans["score_engagement"].fillna(0) < 30].sort_values("score_engagement")
        st.subheader("Audience recommandée")
        st.dataframe(result[["prenom","nom","email","score_engagement","total_depense"]], use_container_width=True, hide_index=True)
        if st.button("📣 Préparer la campagne de réengagement"):
            st.session_state["campaign_segment"] = "À réengager"
            safe_switch("pages/campaigns.py")

    elif "vip" in text or "valeur" in text:
        result = fans.sort_values(["score_engagement","total_depense"], ascending=False).head(10)
        st.subheader("Top supporters")
        st.dataframe(result[["prenom","nom","segment_crm","score_engagement","total_depense"]], use_container_width=True, hide_index=True)

    elif "satisf" in text or "nps" in text:
        result = fans[(fans["nb_avis"].fillna(0) > 0) & (fans["satisfaction_moyenne"].fillna(5) < 3)]
        st.subheader("Supporters à faible satisfaction")
        st.dataframe(result[["prenom","nom","satisfaction_moyenne","nps_moyen"]], use_container_width=True, hide_index=True)

    elif not models:
        st.write(
            f"Base actuelle : {len(fans)} supporters, {len(campaigns)} campagnes, "
            f"{len(actions)} actions CRM, {len(tickets)} ventes et {len(experiences)} avis."
        )
