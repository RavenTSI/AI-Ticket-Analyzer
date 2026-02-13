import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# -----------------------------
# Imports from your core app
# -----------------------------
from core.loader import load_excel_tickets
from core.embeddings import embed_texts
from core.grouping import group_by_similarity
from core.analysis import analyse_group

# -----------------------------
# Config
# -----------------------------
MAX_DISTANCE = 0.35
MAX_DESCRIPTIONS_PER_GROUP = 8

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="AI Ticket Analyzer",
    layout="wide"
)

st.title("🧠 AI Ticket Analyzer")

# -----------------------------
# Sidebar Mode Selector (UNCHANGED)
# -----------------------------
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Online (LLM Live)", "Offline (Pre-generated Results)"]
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

# -----------------------------
# Run Button
# -----------------------------
if not st.button("🚀 Run Analysis"):
    st.info("Click **Run Analysis** to process the uploaded file.")
    st.stop()

# -----------------------------
# Load Tickets
# -----------------------------
with st.spinner("Loading tickets..."):
    tickets = load_excel_tickets(uploaded_file)

st.success(f"Loaded {len(tickets)} tickets")

# -----------------------------
# Generate Embeddings
# -----------------------------
with st.spinner("Generating embeddings..."):
    embedding_texts = [t["embedding_text"] for t in tickets]
    embeddings = embed_texts(embedding_texts)

st.success("Embeddings generated")

# -----------------------------
# Grouping
# -----------------------------
with st.spinner(f"Grouping tickets (distance ≤ {MAX_DISTANCE})..."):
    groups, _ = group_by_similarity(embeddings, MAX_DISTANCE)

meaningful_groups = [g for g in groups if len(g) > 1]

st.success(f"Found {len(meaningful_groups)} meaningful groups")

# -----------------------------
# Load Offline Results (CORRECT LOCATION)
# -----------------------------
offline_results = []

if mode == "Offline (Pre-generated Results)":

    project_root = Path(__file__).parent
    offline_file = project_root / "data" / "offline" / "offline_results.json"

    if not offline_file.exists():
        st.error(f"offline_results.json not found at: {offline_file}")
        st.stop()

    with open(offline_file, "r") as f:
        offline_results = json.load(f)

# -----------------------------
# Display Groups
# -----------------------------
for idx, group in enumerate(meaningful_groups, start=1):

    with st.expander(f"📌 Group {idx} ({len(group)} tickets)", expanded=False):

        st.subheader("🧠 LLM Analysis")

        analysis = None

        if mode == "Online (LLM Live)":
            descriptions = [
                tickets[i]["embedding_text"]
                for i in group[:MAX_DESCRIPTIONS_PER_GROUP]
            ]
            with st.spinner("Analysing group with LLM..."):
                analysis = analyse_group(descriptions)

        else:
            match = next(
                (g for g in offline_results if g.get("group_number") == idx),
                None
            )
            if match:
                analysis = match.get("analysis")

        # -----------------------------
        # Structured Display
        # -----------------------------
        if analysis:
            st.markdown(f"### 🔖 {analysis.get('group_label', 'No label')}")

            st.markdown("**Summary**")
            st.write(analysis.get("summary", ""))

            st.markdown("**Common Patterns**")
            for item in analysis.get("common_patterns", []):
                st.write(f"- {item}")

            st.markdown("**Hypotheses**")
            for item in analysis.get("hypotheses", []):
                st.write(f"- {item}")

            st.markdown("**Recommended Checks**")
            for item in analysis.get("recommended_checks", []):
                st.write(f"- {item}")
        else:
            st.warning("LLM analysis unavailable.")

        # -----------------------------
        # Ticket Details
        # -----------------------------
        st.subheader("📄 Tickets in this group")
        for i in group:
            st.markdown("---")
            st.text(tickets[i]["display_text"])

st.write("✅ App execution completed successfully")
