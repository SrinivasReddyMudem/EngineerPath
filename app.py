"""
Streamlit test UI — for manually reviewing agent output quality, not a product UI.
Run with: streamlit run app.py

All generation goes through the Intent/Output Router — pick ONE purpose
and only that generator runs. No "generate everything" default.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from content_agents.router import generate_content, PURPOSE_TO_AGENT
from content_agents.core.base_agent import AgentError
from content_agents.core.renderer import render

st.set_page_config(page_title="Content Agents — Test Console", layout="wide")
st.title("Content Engineering Agents — Test Console")
st.caption("Manual QA tool. Generates content live via Groq — each run costs real API calls.")

with st.sidebar:
    st.header("Generate via Router")
    topic = st.text_input("Skill topic (folder under skills/)", value="git")
    subject = st.text_input("Subject", value="Git Reset", placeholder="e.g. Git Stash, Detached HEAD")
    purpose_options = sorted(PURPOSE_TO_AGENT.keys())
    purpose = st.selectbox("Purpose", purpose_options, index=purpose_options.index("reel"))
    show_raw = st.checkbox("Show raw JSON", value=False)
    run_clicked = st.button("Generate", type="primary", use_container_width=True)

if run_clicked:
    if not subject.strip():
        st.error("Enter a subject first.")
    else:
        with st.spinner(f"Routing purpose='{purpose}'..."):
            result = generate_content(topic, subject, purpose)

        if isinstance(result, AgentError):
            st.error(f"{result.error_type}: {result.message}")
            if result.raw_response:
                with st.expander("Raw model response"):
                    st.code(result.raw_response)
        else:
            st.markdown(render(PURPOSE_TO_AGENT[purpose], result))

            self_eval = getattr(result, "self_evaluation", None)
            if self_eval:
                with st.expander("Self-evaluation (quality gate checklist)"):
                    for line in self_eval:
                        icon = "✅" if line.result == "PASS" else "❌"
                        st.write(f"{icon} **{line.item}** — {line.evidence}")

            quality_score = getattr(result, "quality_score", None)
            if quality_score:
                with st.expander("Quality score (self-rated — gated fields regenerate below threshold)"):
                    cols = st.columns(3)
                    for i, (field, value) in enumerate(quality_score.model_dump().items()):
                        cols[i % 3].metric(field.replace("_", " ").title(), f"{value}/10")

            if show_raw:
                with st.expander("Raw JSON"):
                    st.json(result.model_dump())
else:
    st.info("Set a subject and purpose in the sidebar, then click Generate.")
