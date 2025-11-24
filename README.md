# 🗣️ Communication Skills Scoring Tool

A Streamlit application designed to evaluate and score communication skills from text transcripts. This tool analyzes various aspects of speech such as content, structure, speech rate, grammar, vocabulary, clarity, and engagement based on a customizable rubric.

## 🎯 Problem Statement

In educational and professional settings, evaluating communication skills objectively is challenging. Manual grading is time-consuming, subjective, and often lacks immediate, granular feedback.

**Nirmaan Case Study** solves this by providing an automated, consistent, and instant scoring mechanism. It helps students and professionals understand their strengths and weaknesses in speech structure, clarity, and engagement without needing a human evaluator.

## 🛠️ Tech Stack

*   **Frontend**: [Streamlit](https://streamlit.io/) (Python-based web framework)
*   **NLP & Processing**:
    *   `nltk`: Natural Language Toolkit for tokenization and grammar checking.
    *   `vaderSentiment`: For sentiment and emotion analysis.
    *   `language-tool-python`: For advanced grammar and style checking.
    *   `sentence-transformers`: For semantic similarity matching (optional/advanced usage).
*   **Data Handling**: `pandas`, `numpy`.

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

## 📊 Scoring Breakdown

The final score (0-100) is a weighted sum of the following components. The weights are fully customizable in `scoring/rubric.json`.

| Component | Weight | Description |
| :--- | :--- | :--- |
| **Content & Structure** | **40%** | **Core Message Quality**<br>• **Salutation (5%)**: Opening greetings (e.g., "Good morning").<br>• **Keywords (30%)**: Presence of required topics (Name, Age, School, Hobbies, etc.).<br>• **Flow (5%)**: Logical sequence (Salutation → Details → Closing). |
| **Language & Grammar** | **20%** | **Linguistic Accuracy**<br>• **Grammar (10%)**: Penalizes errors per 100 words.<br>• **Vocabulary (10%)**: Type-Token Ratio (TTR) for lexical diversity. |
| **Clarity** | **15%** | **Fluency**<br>• Penalizes excessive filler words (*um, uh, like, you know*). |
| **Engagement** | **15%** | **Tone & Emotion**<br>• Rewards positive sentiment and enthusiastic tone. |
| **Speech Rate** | **10%** | **Pacing**<br>• Ideal range: **111-140 WPM**.<br>• Penalties for being too fast (>160) or too slow (<80). |

## 📸 Sample Result

*(Add a screenshot of the application here)*

> **Tip**: The application provides a detailed breakdown like the one below:

```text
Content & Structure: 57.5% of 40 -> contribution 23.00.
 - Salutation: Good salutation found (e.g., 'good morning', 'hello everyone').
 - Keywords: Found keywords: school, class, family, fun fact. Sufficient exact keyword matches.
 - Flow: Order follows recommended flow.
Speech Rate: Too fast (173 WPM). (173.1 WPM)
Grammar: 8 / 10 (4 grammar issues)
Vocabulary (TTR): 0.593 -> score 6/10
...
```

## �🛠️ Installation

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
