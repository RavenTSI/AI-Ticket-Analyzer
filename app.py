import streamlit as st
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Core Imports
# -----------------------------
from core.loader import load_excel_tickets
from core.grouping import group_by_similarity
from core.analysis import analyse_group
from core.embeddings import embed_texts


# -----------------------------
# Config
# -----------------------------
MAX_DISTANCE = 0.35
MAX_DESCRIPTIONS_PER_GROUP = 8
OFFLINE_RESULTS_PATH = Path("data/offline/offline_results.json")


# -----------------------------
# Responsible AI Sanitiser
# -----------------------------
def sanitize_text(text: str) -> str:
    """
    Removes sensitive information before sending to LLM.
    """

    # Emails
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED_EMAIL]', text)

    # IP Addresses
    text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[REDACTED_IP]', text)

    # Server / Hostnames (basic pattern)
    text = re.sub(r'\b(?:srv|server|host)[\w\-\.]*\b', '[REDACTED_HOST]', text, flags=re.IGNORECASE)

    # Password-like fields
    text = re.sub(r'password\s*[:=]\s*\S+', 'password=[REDACTED]', text, flags=re.IGNORECASE)

    return text


# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="AI Ticket Analyzer", layout="wide")
st.title("🧠 AI Ticket Analyzer")


# -----------------------------
# Mode Selector (Default = Offline)
# -----------------------------
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Offline (Pre-generated Results)", "Online (Live OpenAI)"],
    index=0
)

# -----------------------------
# NEW: Minimum Group Size Slider
# -----------------------------
min_group_size = st.sidebar.slider(
    "Minimum tickets required per group",
    min_value=2,
    max_value=10,
    value=2
)


# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload service ticket Excel file (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to begin.")
    st.stop()

if not st.button("🚀 Run Analysis"):
    st.stop()


# -----------------------------
# Load Tickets
# -----------------------------
tickets = load_excel_tickets(uploaded_file)
st.success(f"Loaded {len(tickets)} tickets")


# =====================================================
# OFFLINE MODE  ✅ DO NOT TOUCH STRUCTURE
# =====================================================
if mode == "Offline (Pre-generated Results)":

    if not OFFLINE_RESULTS_PATH.exists():
        st.error("offline_results.json not found in data/offline/")
        st.stop()

    with open(OFFLINE_RESULTS_PATH, "r", encoding="utf-8") as f:
        offline_results = json.load(f)

    if not isinstance(offline_results, list):
        st.error("offline_results.json format invalid.")
        st.stop()

    # Apply minimum group size filter
    meaningful_groups = [
        g for g in offline_results
        if len(g.get("tickets", [])) >= min_group_size
    ]

    st.success(f"Found {len(meaningful_groups)} meaningful groups")

    for group_data in meaningful_groups:

        group_number = group_data.get("group_number", "?")
        tickets_in_group = group_data.get("tickets", [])
        analysis = group_data.get("analysis", {})

        with st.expander(
            f"📌 Group {group_number} ({len(tickets_in_group)} tickets)",
            expanded=False
        ):

            st.subheader("🧠 LLM Analysis")

            if analysis:
                st.markdown(f"### 📌 {analysis.get('group_label', 'No label')}")
                st.markdown("**Summary**")
                st.write(analysis.get("summary", ""))

                if analysis.get("common_patterns"):
                    st.markdown("**Common Patterns**")
                    for item in analysis["common_patterns"]:
                        st.write(f"- {item}")

                if analysis.get("hypotheses"):
                    st.markdown("**Hypotheses**")
                    for item in analysis["hypotheses"]:
                        st.write(f"- {item}")

                if analysis.get("recommended_checks"):
                    st.markdown("**Recommended Checks**")
                    for item in analysis["recommended_checks"]:
                        st.write(f"- {item}")
            else:
                st.warning("LLM analysis unavailable.")

            st.subheader("📄 Tickets in this group")

            for ticket in tickets_in_group:
                st.markdown("---")
                st.text(ticket.get("display_text", "No display text"))


# =====================================================
# ONLINE MODE
# =====================================================
else:

    st.info("Running in ONLINE mode (OpenAI required)")

    embedding_texts = [t["embedding_text"] for t in tickets]
    embeddings = embed_texts(embedding_texts)

    groups, _ = group_by_similarity(embeddings, tickets, MAX_DISTANCE)

    meaningful_groups = [
        g for g in groups
        if len(g) >= min_group_size
    ]

    st.success(f"Found {len(meaningful_groups)} meaningful groups")

    for idx, group in enumerate(meaningful_groups, start=1):

        with st.expander(
            f"📌 Group {idx} ({len(group)} tickets)",
            expanded=False
        ):

            # Apply sanitisation BEFORE sending to LLM
            descriptions = [
                sanitize_text(tickets[i]["embedding_text"])
                for i in group[:MAX_DESCRIPTIONS_PER_GROUP]
            ]

            try:
                analysis = analyse_group(descriptions)
            except Exception as e:
                st.error(f"LLM Error: {str(e)}")
                analysis = None

            st.subheader("🧠 LLM Analysis")

            if isinstance(analysis, dict) and "error" not in analysis:
                st.markdown(f"### 📌 {analysis.get('group_label', 'No label')}")
                st.markdown("**Summary**")
                st.write(analysis.get("summary", ""))

                if analysis.get("common_patterns"):
                    st.markdown("**Common Patterns**")
                    for item in analysis["common_patterns"]:
                        st.write(f"- {item}")

                if analysis.get("hypotheses"):
                    st.markdown("**Hypotheses**")
                    for item in analysis["hypotheses"]:
                        st.write(f"- {item}")

                if analysis.get("recommended_checks"):
                    st.markdown("**Recommended Checks**")
                    for item in analysis["recommended_checks"]:
                        st.write(f"- {item}")

            elif isinstance(analysis, dict) and "error" in analysis:
                st.error("LLM returned parsing error.")
                st.text(analysis.get("raw_response", ""))
            else:
                st.warning("LLM analysis unavailable.")

            st.subheader("📄 Tickets in this group")

            for i in group:
                st.markdown("---")
                st.text(tickets[i]["display_text"])
