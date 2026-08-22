import json
import os
import sys
import pandas as pd
import streamlit as st

# Ensure root path is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.actions import ActionEngine
from src.audit import AuditTrailManager
from src.classifier import EmailClassifier
from src.schemas import Email

st.set_page_config(
    page_title="Autonomous Email-to-Action Dashboard",
    page_icon="🤖",
    layout="wide",
)

# Initialize Session State
if "audit_manager" not in st.session_state:
    st.session_state.audit_manager = AuditTrailManager()

# Header Section
st.title("🤖 Autonomous Email-to-Action Agent")
st.caption(
    "Automated classification, action dispatching, and audit logging for corporate finance & AP."
)

# Sidebar Configuration & Tools
st.sidebar.header(" Configuration & Controls")
api_key = st.sidebar.text_input("OpenAI API Key (Optional)", type="password")
model_choice = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])

st.sidebar.markdown("---")
st.sidebar.header("+ Inject Custom Test Email")
with st.sidebar.form("custom_email_form"):
    c_sender = st.text_input("Sender Email", "vendor@example.com")
    c_subject = st.text_input("Subject", "Dispute: Unapplied Credit on Statement")
    c_body = st.text_area("Body", "Please check invoice #9920. We were double charged for shipping.")
    submit_custom = st.form_submit_button("Add Email to Batch")

# Load Emails Data
@st.cache_data
def load_default_emails():
    # Construct an absolute path relative to app.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "data", "mock_emails.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Email(**item) for item in data]
if "emails_list" not in st.session_state:
    st.session_state.emails_list = load_default_emails()

if submit_custom:
    new_email = Email(
        id=f"EML-00{len(st.session_state.emails_list)+1}",
        sender=c_sender,
        subject=c_subject,
        timestamp="2026-08-22T08:30:00Z",
        body=c_body,
    )
    st.session_state.emails_list.append(new_email)
    st.sidebar.success("Custom email added to active batch!")

# Interactive Workspace Tabs
tab1, tab2, tab3 = st.tabs([" Inbox Batch & Processing", " Analytics & Audit Log", "Detailed Inspector"])

with tab1:
    st.subheader(" Current Pending Inbox")
    df_inbox = pd.DataFrame([e.model_dump() for e in st.session_state.emails_list])
    st.dataframe(df_inbox, use_container_width=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        process_btn = st.button(" Run Agent Pipeline", type="primary", use_container_width=True)
    with col2:
        if st.button(" Reset Batch", use_container_width=True):
            st.session_state.emails_list = load_default_emails()
            st.session_state.audit_manager.clear()
            st.rerun()

    if process_btn:
        st.session_state.audit_manager.clear()
        classifier = EmailClassifier(api_key=api_key if api_key else None, model=model_choice)
        engine = ActionEngine()

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, email in enumerate(st.session_state.emails_list):
            status_text.text(f"Processing {email.id}: {email.subject[:30]}...")
            classification = classifier.classify(email)
            audit_entry = engine.execute(email, classification)
            st.session_state.audit_manager.add_entry(audit_entry)
            progress_bar.progress((i + 1) / len(st.session_state.emails_list))

        status_text.text("")
        st.success("Batch execution completed across all incoming emails!")

with tab2:
    logs = st.session_state.audit_manager.get_logs_as_dicts()
    if logs:
        df_logs = pd.DataFrame(logs)

        # Summary KPIs
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Processed", len(df_logs))
        m2.metric("Successful Actions", len(df_logs[df_logs["status"] == "SUCCESS"]))
        m3.metric("Flagged / Ambiguous", len(df_logs[df_logs["status"] == "FLAGGED"]))
        m4.metric("Avg Confidence", f"{df_logs['confidence_score'].mean():.2f}")

        st.markdown("---")
        st.subheader(" Audit Log Trail")
        
        # Filter controls
        selected_intent = st.multiselect(
            "Filter by Intent:",
            options=df_logs["intent"].unique(),
            default=df_logs["intent"].unique()
        )
        filtered_df = df_logs[df_logs["intent"].isin(selected_intent)]
        st.dataframe(filtered_df, use_container_width=True)

        # Download CSV functionality
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            " Export Audit Logs (CSV)",
            data=csv_data,
            file_name="audit_trail.csv",
            mime="text/csv",
        )
    else:
        st.info("No audit logs available yet. Click **Run Agent Pipeline** in the first tab to generate logs.")

with tab3:
    logs = st.session_state.audit_manager.get_logs_as_dicts()
    if logs:
        st.subheader("🔍 Individual Email Classification Inspector")
        selected_id = st.selectbox("Select Email ID:", [l["email_id"] for l in logs])
        selected_entry = next(item for item in logs if item["email_id"] == selected_id)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original Email Payload**")
            st.json({
                "Sender": selected_entry["sender"],
                "Intent": selected_entry["intent"],
                "Confidence Score": selected_entry["confidence_score"]
            })
        with c2:
            st.markdown("**Executed System Response**")
            st.info(f"**Action Taken:** {selected_entry['action_taken']}")
            st.write(f"**Details:** {selected_entry['action_details']}")
            st.caption(f"**AI Reasoning:** {selected_entry['reasoning']}")
    else:
        st.info("Run the processing pipeline to inspect granular decisions.")