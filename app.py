import streamlit as st
import json
import nltk

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

from scoring.scorer import compute_scores, load_rubric

# Page setup
st.set_page_config(page_title="Communication Skills Scoring Tool", layout="wide")

st.title("🗣️ Communication Skills Scoring Tool (Intern Case Study)")
st.write("Paste your transcript below and get a full rubric-based score (0-100).")


# Load rubric once
rubric = load_rubric()

# User Input Section
st.header("📥 Input Transcript")

transcript = st.text_area(
    "Paste the transcript text here:",
    height=200,
    placeholder="Example: Hello everyone, my name is..."
)

duration = st.number_input(
    "Optional: Enter speech duration in seconds (for WPM calculation)",
    min_value=0.0,
    step=0.5
)

if st.button("🔍 Score Transcript"):
    if not transcript.strip():
        st.warning("Please paste a transcript before scoring.")
    else:
        with st.spinner("Scoring in progress..."):
            results = compute_scores(transcript, duration_seconds=duration, rubric=rubric)

        st.success("Scoring completed!")


        # ==============================
        # Display Overall Score
        # ==============================
        st.header("🏆 Overall Score")
        st.metric(
            label="Final Score (0–100)",
            value=f"{results['overall_score']}"
        )


        # ==============================
        # Display Basic Stats
        # ==============================
        st.subheader("📊 Basic Transcript Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Word Count", results["word_count"])
        col2.metric("Sentence Count", results["sentence_count"])
        col3.metric("Duration (seconds)", results["duration_seconds"] if duration else "Not Provided")


        # ==============================
        # Per-Component Scores
        # ==============================
        st.header("🧩 Per-Criterion Breakdown (Rubric Components)")

        for comp_name, comp_data in results["components"].items():
            with st.expander(f"📌 {comp_name.replace('_', ' ').title()}"):
                st.write(f"**Weight:** {comp_data['weight']}")
                st.write(f"**Score Contribution:** {comp_data['contribution']} points")
                st.write("---")

                # If subscores exist
                if "subscores" in comp_data:
                    for sub_name, sub_data in comp_data["subscores"].items():
                        st.write(f"### 🔹 {sub_name.replace('_', ' ').title()}")
                        st.write(f"**Raw Score:** {sub_data['raw']} / {sub_data['max']}")
                        if "feedback" in sub_data:
                            st.write(f"**Feedback:** {sub_data['feedback']}")
                        if "found" in sub_data:
                            st.write(f"**Matched Keywords:** {', '.join(sub_data['found'])}")
                        if "errors" in sub_data:
                            st.write(f"**Grammar Errors:** {sub_data['errors']}")
                        if "ttr" in sub_data:
                            st.write(f"**TTR:** {sub_data['ttr']}")
                        st.write("---")

                # Other components (speech rate, clarity, engagement)
                else:
                    st.write(f"**Raw Score:** {comp_data['raw']} / {comp_data['max']}")
                    if "feedback" in comp_data:
                        st.write(f"**Feedback:** {comp_data['feedback']}")
                    st.write("---")


        # ==============================
        # Overall Feedback Summary
        # ==============================
        st.header("📝 Summary Feedback")
        st.text_area(
            "Automatic feedback summary:",
            value=results["feedback_summary"],
            height=200
        )
