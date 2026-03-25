# =============================================================================
# PANELIST BALLOT PAGE
# =============================================================================
# This page is what panelists see when they open their unique link.
# The URL contains a token: /ballot?token=abc123
# The token maps to one row in the panelists table in Supabase,
# which contains their serving order and blinding codes.
# =============================================================================

import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="Sensory Evaluation",
    page_icon="🧪",
    layout="centered"
)

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# -----------------------------------------------------------------------------
# READ TOKEN FROM URL
# Streamlit exposes URL query parameters via st.query_params
# The panelist link looks like: /ballot?token=abc123
# We read the token and use it to look up the panelist in the database
# -----------------------------------------------------------------------------
params = st.query_params
token = params.get("token", None)

if not token:
    st.error("Invalid link. Please ask your session coordinator for your personal ballot link.")
    st.stop()

# Look up the panelist record using their token
result = supabase.table("panelists").select("*").eq("access_token", token).execute()

if not result.data:
    st.error("Link not recognized. Please ask your session coordinator for help.")
    st.stop()

panelist = result.data[0]

# Check if already submitted
if panelist["submitted"]:
    st.success("You have already submitted your responses. Thank you!")
    st.stop()

# Load the trial config
trial_result = supabase.table("trials").select("*").eq("id", panelist["trial_id"]).execute()
if not trial_result.data:
    st.error("Trial not found. Please contact your session coordinator.")
    st.stop()

trial = trial_result.data[0]
config = trial["config"]

# Parse panelist data
serving_order = panelist["serving_order"]
# serving_order is a list of dicts: [{product_name, blinding_code}, ...]

products_in_order = serving_order
attributes = config["attributes"]
scale = config["scale_type"]

# -----------------------------------------------------------------------------
# BALLOT UI
# -----------------------------------------------------------------------------
st.title("🧪 Sensory Evaluation")
st.markdown(f"**Trial:** {config['trial_name']}")
st.markdown(f"**Panelist:** {panelist['panelist_number']}")
st.caption("Evaluate each sample in the order shown. Do not share this page with other panelists.")
st.markdown("---")

# Collect all responses in a dictionary
all_responses = {}

for pos, sample in enumerate(products_in_order):
    blind_code = sample["blinding_code"]

    st.markdown(f"### Sample {pos+1} — Code: **{blind_code}**")
    st.caption("Evaluate this sample before moving to the next.")

    sample_responses = {}

    if scale == "Preference (forced choice: pick one)":
        st.markdown("*(Evaluate this sample, then indicate your preference at the end)*")

    else:
        for attr in attributes:
            if scale == "9-point Hedonic":
                val = st.slider(
                    label=attr,
                    min_value=1, max_value=9, value=5,
                    help="1 = Dislike extremely, 9 = Like extremely",
                    key=f"s{pos}_{attr}"
                )
            elif scale == "100mm Visual Analogue Scale (VAS)":
                val = st.slider(
                    label=attr,
                    min_value=0, max_value=100, value=50,
                    key=f"s{pos}_{attr}"
                )
            elif scale == "5-point Likert":
                val = st.select_slider(
                    label=attr,
                    options=["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
                    key=f"s{pos}_{attr}"
                )
            elif scale == "Just About Right (JAR) — 5-point":
                val = st.select_slider(
                    label=attr,
                    options=["Much too little", "Too little", "Just about right", "Too much", "Much too much"],
                    key=f"s{pos}_{attr}"
                )
            sample_responses[attr] = val

    all_responses[f"sample_{pos+1}"] = {
        "blinding_code": blind_code,
        "position": pos + 1,
        "ratings": sample_responses
    }

    st.markdown("---")

# Forced choice — one question at the end after all samples
if scale == "Preference (forced choice: pick one)":
    st.markdown("### Which sample did you prefer?")
    code_options = [str(s["blinding_code"]) for s in products_in_order]
    preferred = st.radio(
        label="Select one:",
        options=code_options,
        key="preference"
    )
    all_responses["preference"] = preferred

# -----------------------------------------------------------------------------
# SUBMIT BUTTON
# Writes all responses to Supabase and marks panelist as submitted
# -----------------------------------------------------------------------------
st.markdown("---")
submit = st.button("✅ Submit my responses", type="primary", use_container_width=True)

if submit:
    try:
        # Write one row per sample to the responses table
        for pos, sample in enumerate(products_in_order):
            ratings = all_responses.get(f"sample_{pos+1}", {}).get("ratings", {})
            if scale == "Preference (forced choice: pick one)":
                ratings = {"preference": all_responses.get("preference")}

            supabase.table("responses").insert({
                "panelist_id": panelist["id"],
                "trial_id": panelist["trial_id"],
                "sample_position": pos + 1,
                "blinding_code": sample["blinding_code"],
                "ratings": ratings
            }).execute()

        # Mark panelist as submitted so they can't resubmit
        supabase.table("panelists").update(
            {"submitted": True}
        ).eq("id", panelist["id"]).execute()

        st.success("Responses submitted. Thank you for participating!")
        st.balloons()

    except Exception as e:
        st.error(f"Submission failed. Please tell your session coordinator. Error: {e}")