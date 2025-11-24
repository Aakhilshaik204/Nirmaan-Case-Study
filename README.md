# 🗣️ Communication Skills Scoring Tool

A Streamlit application designed to evaluate and score communication skills from text transcripts. This tool analyzes various aspects of speech such as content, structure, speech rate, grammar, vocabulary, clarity, and engagement based on a customizable rubric.

## 🚀 Features

*   **Rubric-Based Scoring**: customizable scoring rules defined in `scoring/rubric.json`.
*   **Comprehensive Analysis**:
    *   **Content & Structure**: Evaluates salutation, keyword presence, and logical flow.
    *   **Speech Rate**: Calculates Words Per Minute (WPM) and assesses pacing.
    *   **Language & Grammar**: Checks for grammar errors and vocabulary diversity (Type-Token Ratio).
    *   **Clarity**: Detects filler words to measure speech clarity.
    *   **Engagement**: Analyzes sentiment to gauge engagement levels.
*   **Interactive UI**: User-friendly interface built with Streamlit for easy input and result visualization.
*   **Detailed Feedback**: Provides specific feedback for each scoring criterion.

## 🛠️ Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Set up a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    *Note: You may need to download NLTK data if prompted (e.g., `nltk.download('punkt')`).*

## 🏃‍♂️ Usage

1.  **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

2.  **Open your browser**: The app should automatically open at `http://localhost:8501`.

3.  **Score a Transcript**:
    *   Paste the text transcript into the input area.
    *   (Optional) Enter the duration of the speech in seconds for Speech Rate calculation.
    *   Click **"🔍 Score Transcript"** to see the results.

## 📂 Project Structure

*   `app.py`: Main entry point for the Streamlit application.
*   `requirements.txt`: List of Python dependencies.
*   `scoring/`: Package containing scoring logic and helper modules.
    *   `scorer.py`: Main scoring orchestration logic.
    *   `rubric.json`: Configuration file for scoring weights and rules.
    *   `grammar.py`, `vocabulary.py`, `sentiment.py`, `preprocess.py`, `semantic.py`: Helper modules for specific analysis tasks.

## ⚙️ Configuration

You can adjust the scoring weights, keywords, and rules by editing `scoring/rubric.json`. No code changes are required for tweaking the rubric.
