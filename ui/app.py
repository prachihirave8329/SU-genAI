

import streamlit as st
import requests
import csv
import sys

from pathlib import Path
from datetime import datetime

# Get the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Add project folder before other import paths
sys.path.insert(0, str(BASE_DIR))

# Import project modules
from app.records import load_records
from app.tools import monthly_savings_calculator


# Page configuration must come first
st.set_page_config(
    page_title="JanAushadhiFinder",
    page_icon="💊",
    layout="wide"
)


# Application settings
API_URL = "http://127.0.0.1:8000"

FEEDBACK_FILE = BASE_DIR / "data" / "feedback.csv"
# Custom CSS
st.markdown("""
<style>

.stApp {
    background-color: #f7faf8;
}

h1, h2, h3 {
    color: #176b45;
}

.stButton button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Save feedback
def save_feedback(question, answer, feedback):

    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "question",
                "answer",
                "feedback",
                "timestamp"
            ])

        writer.writerow([
            question,
            answer,
            feedback,
            datetime.now().isoformat(timespec="seconds")
        ])


# Sidebar
with st.sidebar:

    st.title("💊 JanAushadhiFinder")

    st.write("Your generic medicine information assistant.")

    st.divider()

    st.subheader("About")

    st.write(
        "Find information about affordable generic medicines "
        "and compare illustrative medicine prices."
    )

    if st.button("➕ New Chat", use_container_width=True):

        st.session_state.messages = []
        st.rerun()


# Main heading
st.title("💊 JanAushadhiFinder")

st.write(
    "Find information about affordable generic medicines."
)

st.caption(
    "Explore medicine information and compare estimated costs."
)


# =====================================
# MEDICINE PRICE COMPARISON
# =====================================

st.divider()

st.header("💰 Same Salt, Same Strength Comparison")

st.write(
    "Compare the price of a generic medicine with a branded medicine."
)

medicines = load_records()

medicine_options = [
    f'{m["generic_name"]} - {m["strength"]} ({m["drug_code"]})'
    for m in medicines
    if "tablet" in m["unit_size"].lower()
]

selected_medicine = st.selectbox(
    "Select generic medicine",
    medicine_options
)

drug_code = selected_medicine.split("(")[-1].replace(")", "")

medicine = next(
    m for m in medicines if m["drug_code"] == drug_code
)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Generic Medicine")

    st.write("**Name:**", medicine["generic_name"])

    st.write("**Strength:**", medicine["strength"])

    st.write("**Pack:**", medicine["unit_size"])

    st.write("**Sample price:** ₹", medicine["mrp_inr"])


with col2:

    st.subheader("Branded Medicine")

    branded_name = st.text_input(
        "Branded medicine name"
    )

    branded_ingredient = st.text_input(
        "Active ingredient / salt"
    )

    branded_strength = st.text_input(
        "Branded medicine strength"
    )

    branded_price = st.number_input(
        "Branded strip price (₹)",
        min_value=1.0,
        value=60.0
    )

    branded_pack_size = st.number_input(
        "Tablets in branded strip",
        min_value=1,
        value=10
    )


tablets_per_day = st.number_input(
    "Tablets per day (for cost estimation only)",
    min_value=1,
    value=2
)


if st.button("Compare Prices", use_container_width=True):

    # Check medicine ingredient and strength
    same_ingredient = (
        branded_ingredient.strip().lower()
        == medicine["generic_name"].strip().lower()
    )

    same_strength = (
        branded_strength.strip().lower()
        == medicine["strength"].strip().lower()
    )

    if not branded_name.strip():
        st.error("Enter the branded medicine name.")

    elif not branded_ingredient.strip() or not branded_strength.strip():
        st.error("Enter the branded medicine ingredient and strength.")

    elif not same_ingredient or not same_strength:
        st.error(
            "Medicine mismatch! The active ingredient and strength "
            "must match before comparing prices."
        )

    else:

        result = monthly_savings_calculator(
            drug_code,
            branded_price,
            branded_pack_size,
            tablets_per_day
        )

        if "error" in result:

            st.error(result["error"])

        else:

            st.success("Ingredient and strength match.")

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Generic Medicine")

                st.metric(
                    "Monthly cost",
                    f'₹{result["jan_monthly_cost"]}'
                )

            with col2:

                st.subheader("Branded Medicine")

                st.metric(
                    "Monthly cost",
                    f'₹{result["branded_monthly_cost"]}'
                )

            st.divider()

            if result["monthly_savings"] > 0:

                st.success(
                    f'🎉 You save ₹{result["monthly_savings"]} per month!'
                )

            elif result["monthly_savings"] < 0:

                st.info(
                    f'Generic option costs ₹{abs(result["monthly_savings"])} '
                    'more per month in this comparison.'
                )

            else:

                st.info("Both options have the same estimated monthly cost.")

            st.metric(
                "Estimated yearly difference",
                f'₹{abs(result["yearly_savings"])}'
            )

            if branded_pack_size == int(
                medicine["unit_size"].split()[0]
            ):

                st.caption("Both packs contain the same number of tablets.")

            else:

                st.caption(
                    "Pack sizes differ. Costs are normalized per tablet."
                )

            st.caption(
                "Demo prices are illustrative and not verified official "
                "PMBI prices. Confirm the active ingredient, strength, "
                "dosage form and suitability with a pharmacist. "
                "This comparison does not recommend switching medicines."
            )


# =====================================
# CHAT ASSISTANT
# =====================================

st.divider()

st.header("💬 Ask JanAushadhiFinder")

st.write(
    "Ask questions about Jan Aushadhi and affordable generic medicines."
)


# Display previous chat messages
for i, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.write(message["content"])

        # Display citations
        if message["role"] == "assistant":

            citations = message.get("citations", [])

            if citations:

                with st.expander("📚 View Sources"):

                    # Avoid duplicate citations
                    unique_citations = {
                        (
                            c["title"],
                            c["page"],
                            c["source"]
                        ): c
                        for c in citations
                    }

                    for citation in unique_citations.values():

                        st.caption(
                            f'📄 {citation["title"]} | '
                            f'Page: {citation["page"]} | '
                            f'Source: {citation["source"]}'
                        )

            # Feedback buttons
            if not message.get("feedback"):

                col1, col2 = st.columns(2)

                with col1:

                    if st.button("👍 Helpful", key=f"up_{i}"):

                        save_feedback(
                            message["question"],
                            message["content"],
                            "positive"
                        )

                        message["feedback"] = "positive"

                        st.rerun()

                with col2:

                    if st.button("👎 Not helpful", key=f"down_{i}"):

                        save_feedback(
                            message["question"],
                            message["content"],
                            "negative"
                        )

                        message["feedback"] = "negative"

                        st.rerun()

            else:

                st.caption("Thank you for your feedback!")


# Chat input
question = st.chat_input(
    "Ask about Jan Aushadhi..."
)


if question:

    # Display user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    try:

        response = requests.post(
            API_URL + "/ask",
            json={"question": question},
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        # Store assistant answer
        st.session_state.messages.append({

            "role": "assistant",

            "content": data.get(
                "answer",
                "No answer received."
            ),

            "citations": data.get("citations", []),

            "question": question
        })

    except requests.exceptions.RequestException as error:

        st.session_state.messages.append({

            "role": "assistant",

            "content": (
                "Unable to connect to the backend. "
                "Please check whether FastAPI is running."
            ),

            "citations": [],

            "question": question
        })

    st.rerun()
