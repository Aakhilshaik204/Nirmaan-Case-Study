"""
scoring/scorer.py

Combines preprocessing, grammar, vocabulary, sentiment, and semantic modules
to compute per-criterion scores and an overall normalized score (0-100).

Assumes the following modules/files exist in the scoring/ package:
- preprocess.py (clean_text, get_word_count, get_sentence_count, count_filler_words)
- grammar.py (grammar_score)
- vocabulary.py (vocabulary_score)
- sentiment.py (sentiment_score)
- semantic.py (semantic_similarity)
- rubric.json (created in Phase 1; contains weights & rules)
"""

import json
import os
from typing import Dict, Any, List, Tuple

from scoring.preprocess import clean_text, get_word_count, get_sentence_count, count_filler_words
from scoring.grammar import grammar_score
from scoring.vocabulary import vocabulary_score
from scoring.sentiment import sentiment_score
from scoring.semantic import semantic_similarity

# Path to rubric JSON (make sure this file exists)
RUBRIC_PATH = os.path.join(os.path.dirname(__file__), "rubric.json")


def load_rubric(path: str = RUBRIC_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(subscore: float, max_score: float) -> float:
    """Normalize a subscore to a 0-1 range given its maximum possible score."""
    if max_score <= 0:
        return 0.0
    return max(0.0, min(1.0, subscore / max_score))


def _map_range_score(value: float, ranges: List[Tuple[float, float, float]]) -> float:
    """
    Map a numeric 'value' into a discrete score by ranges.
    ranges: list of (low_inclusive, high_inclusive, score)
    Returns the mapped score or 0 if not matched.
    """
    for low, high, score in ranges:
        if low <= value <= high:
            return score
    return 0.0


def score_salutation(text: str, rubric_salutation: Dict[str, Any]) -> Tuple[float, str]:
    """
    Score salutation based on rubric rules.
    Returns (score, feedback)
    """
    txt = text.lower()
    rules = rubric_salutation.get("rules", {})
    feedback = []
    sal_score = 0.0

    # Check excellent first
    if any(kw in txt for kw in rules.get("excellent", {}).get("keywords", [])):
        sal_score = rules["excellent"]["score"]
        feedback.append("Excellent salutation found (e.g., 'excited to introduce').")
    elif any(kw in txt for kw in rules.get("good", {}).get("keywords", [])):
        sal_score = rules["good"]["score"]
        feedback.append("Good salutation found (e.g., 'good morning', 'hello everyone').")
    elif any(kw in txt for kw in rules.get("normal", {}).get("keywords", [])):
        sal_score = rules["normal"]["score"]
        feedback.append("Normal salutation found (e.g., 'hi', 'hello').")
    else:
        sal_score = rules.get("no_salutation", {}).get("score", 0)
        feedback.append("No clear salutation detected.")

    return float(sal_score), " ".join(feedback)


def score_keyword_presence(words: List[str], text: str, rubric_kw: Dict[str, Any]) -> Tuple[float, List[str], str]:
    """
    Score keyword presence according to must-have and good-to-have lists.
    We also supplement with semantic matching for robustness.
    Returns (raw_score, found_keywords_list, feedback)
    """
    must_have = rubric_kw.get("must_have", {})
    good_to_have = rubric_kw.get("good_to_have", {})

    mw = must_have.get("keywords", [])
    gw = good_to_have.get("keywords", [])

    found = []
    raw_score = 0.0

    # simple exact match (word boundaries)
    wordset = set(words)
    text_lower = text.lower()
    
    # Check Must Have
    for kw in mw:
        # handle multi-word keywords
        if " " in kw:
            if kw in text_lower:
                found.append(kw)
                raw_score += must_have.get("score_each", 4)
        else:
            if kw in wordset:
                found.append(kw)
                raw_score += must_have.get("score_each", 4)

    # Check Good to Have
    for kw in gw:
        if " " in kw:
            if kw in text_lower:
                found.append(kw)
                raw_score += good_to_have.get("score_each", 2)
        else:
            if kw in wordset:
                found.append(kw)
                raw_score += good_to_have.get("score_each", 2)

    # If few matches found, use semantic similarity against "must have" phrase list
    if len(found) < max(1, len(mw) // 2):
        # compute semantic similarity between text and each must-have keyword/phrase
        target_phrases = mw + gw
        try:
            sim = semantic_similarity(text, target_phrases)
        except Exception:
            sim = 0.0
        # If average similarity is reasonably high, give partial credit
        if sim >= 0.6:
            bonus = 0.5 * sum([must_have.get("score_each", 4) for _ in mw])
            raw_score += bonus
            found.append("semantic-match")
            sem_msg = f"Semantic match detected (avg similarity {sim:.2f}); awarded partial credit."
        else:
            sem_msg = f"Semantic match weak (avg similarity {sim:.2f})."
    else:
        sem_msg = "Sufficient exact keyword matches."

    feedback = f"Found keywords: {', '.join(found) if found else 'none'}. {sem_msg}"
    return float(raw_score), found, feedback


def score_flow(text: str, rubric_flow: Dict[str, Any]) -> Tuple[float, str]:
    """
    Check whether basic order is followed: salutation -> basic details -> optional -> closing
    We'll approximate by checking indices of place-holder tokens in text.
    """
    order_spec = rubric_flow.get("rules", {}).get("correct_order", {}).get("order", [])
    # Map placeholder tokens to example indicators based on new rubric
    indicators = {
        "salutation": ["hello", "hi", "good morning", "good afternoon", "good evening", "good day", "excited to introduce"],
        "basic_details": ["my name is", "i am", "i'm", "age", "years old", "class", "grade", "school", "studying in", "student of"],
        "optional_details": ["family", "parents", "father", "mother", "hobby", "hobbies", "interest", "like to", "ambition", "goal", "dream", "strength", "weakness", "achievement", "fun fact"],
        "closing": ["thank you", "thanks", "that's all", "bye"]
    }

    text_l = text.lower()
    positions = {}
    
    # Find the FIRST occurrence of any indicator for each category
    for key, tokens in indicators.items():
        pos_list = [text_l.find(tok) for tok in tokens if text_l.find(tok) != -1]
        positions[key] = min(pos_list) if pos_list else None

    # Check if positions are in increasing order ignoring None
    seq = []
    for item in order_spec:
        pos = positions.get(item)
        if pos is not None:
            seq.append((item, pos))
        
    # If we found fewer than 2 components, it's hard to judge flow, but let's say it's bad if we don't have at least salutation and closing or basic details
    if len(seq) < 2:
         # lenient: if only 1 component found, we can't say order is WRONG, but it's not a full flow. 
         # Rubric says "Order followed" vs "Order Not followed". 
         # Let's require at least 2 components to be present and in order to give points.
         is_correct = False
    else:
        is_correct = all(seq[i][1] <= seq[i+1][1] for i in range(len(seq)-1))

    score = rubric_flow.get("rules", {}).get("correct_order", {}).get("score", 5) if is_correct else 0
    feedback = "Order follows recommended flow." if is_correct else "Order does not follow the recommended flow (Salutation -> Basic Details -> Optional Details -> Closing)."
    return float(score), feedback


def score_speech_rate(word_count: int, duration_seconds: float, rubric_sr: Dict[str, Any]) -> Tuple[float, str]:
    """
    Compute WPM and map to score.
    If duration_seconds is 0 or None, we cannot compute WPM — return neutral/low points.
    """
    if not duration_seconds or duration_seconds <= 0 or word_count == 0:
        return float(rubric_sr.get("rules", {}).get("ideal", {}).get("score", 10) / 2), "Duration not provided; speech rate estimated as neutral."

    wpm = (word_count / duration_seconds) * 60.0
    # find which bracket it falls into (we can parse rubric_sr rules)
    rules = rubric_sr.get("rules", {})
    # manual mapping according to rubric ranges:
    if wpm > 161:
        score = rules.get("too_fast", {}).get("score", 2)
        msg = f"Too fast ({wpm:.0f} WPM)."
    elif 141 <= wpm <= 160:
        score = rules.get("fast", {}).get("score", 6)
        msg = f"Fast ({wpm:.0f} WPM)."
    elif 111 <= wpm <= 140:
        score = rules.get("ideal", {}).get("score", 10)
        msg = f"Ideal ({wpm:.0f} WPM)."
    elif 81 <= wpm <= 110:
        score = rules.get("slow", {}).get("score", 6)
        msg = f"Slow ({wpm:.0f} WPM)."
    else:
        score = rules.get("too_slow", {}).get("score", 2)
        msg = f"Too slow ({wpm:.0f} WPM)."

    return float(score), msg + f" ({wpm:.1f} WPM)"


def score_filler_words(filler_count: int, total_words: int, rubric_clarity: Dict[str, Any]) -> Tuple[float, str]:
    """
    Map filler word rate to clarity score.
    """
    if total_words == 0:
        return float(rubric_clarity.get("filler_words", {}).get("scoring", {}).get("0-3", 15)), "No words."

    rate_percent = (filler_count / total_words) * 100.0
    scoring = rubric_clarity.get("filler_words", {}).get("scoring", {})

    # Translate rubric buckets (they were defined as 0-3, 4-6 etc counted absolute filler counts,
    # but we receive filler_count absolute. We'll directly use counts to map.)
    # We'll use counts (not percent) because rubric uses absolute counts.
    fc = filler_count
    if fc <= 3:
        score = scoring.get("0-3", 15)
    elif 4 <= fc <= 6:
        score = scoring.get("4-6", 12)
    elif 7 <= fc <= 9:
        score = scoring.get("7-9", 9)
    elif 10 <= fc <= 12:
        score = scoring.get("10-12", 6)
    else:
        score = scoring.get("13+", 3)

    feedback = f"{filler_count} filler words detected ({rate_percent:.2f}% of words)."
    return float(score), feedback


def compute_scores(transcript: str, duration_seconds: float = None, rubric: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main entrypoint:
    - transcript: the text to evaluate
    - duration_seconds: optional speech duration (seconds) to compute WPM
    - rubric: optional preloaded rubric dict (otherwise loads from file)
    Returns a dict containing per-criterion raw scores, normalized contributions, feedbacks, and overall score (0-100).
    """
    if rubric is None:
        rubric = load_rubric()

    # Preprocess
    text = clean_text(transcript)
    word_count, words = get_word_count(text)
    sentence_count = get_sentence_count(text)
    filler_count = count_filler_words(words)

    results = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "duration_seconds": duration_seconds,
        "components": {}
    }

    total_weight = 0.0
    weighted_score_sum = 0.0

    # --- Content & Structure (composed of salutation, keywords, flow)
    cs = rubric.get("content_and_structure", {})
    cs_weight = cs.get("weight", 0)
    total_weight += cs_weight
    cs_subscores = {}

    # Salutation
    sal_score_raw, sal_feedback = score_salutation(transcript, cs.get("salutation", {}))
    cs_subscores["salutation"] = {"raw": sal_score_raw, "max": cs.get("salutation", {}).get("weight", 5), "feedback": sal_feedback}

    # Keyword presence
    kw_raw, found_kws, kw_feedback = score_keyword_presence(words, text, cs.get("keyword_presence", {}))
    # The rubric had keyword presence weight 30 (split across must & good) — interpret raw as points up to sum of must/good totals.
    kw_max = cs.get("keyword_presence", {}).get("weight", 30)
    # If raw exceeds kw_max, clip
    kw_raw_clipped = min(kw_raw, kw_max)
    cs_subscores["keyword_presence"] = {"raw": kw_raw_clipped, "max": kw_max, "found": found_kws, "feedback": kw_feedback}

    # Flow
    flow_raw, flow_feedback = score_flow(text, cs.get("flow", {}))
    flow_max = cs.get("flow", {}).get("rules", {}).get("correct_order", {}).get("score", 5)
    cs_subscores["flow"] = {"raw": flow_raw, "max": flow_max, "feedback": flow_feedback}

    # Normalize content & structure subcomponent to the CS weight proportionally
    # Sum raw and max for CS subcomponents, then scale to cs_weight
    cs_raw_sum = cs_subscores["salutation"]["raw"] + cs_subscores["keyword_presence"]["raw"] + cs_subscores["flow"]["raw"]
    cs_max_sum = cs_subscores["salutation"]["max"] + cs_subscores["keyword_presence"]["max"] + cs_subscores["flow"]["max"]
    cs_fraction = _normalize(cs_raw_sum, cs_max_sum)
    cs_contribution = cs_fraction * cs_weight
    weighted_score_sum += cs_contribution

    results["components"]["content_and_structure"] = {
        "weight": cs_weight,
        "subscores": cs_subscores,
        "raw_sum": cs_raw_sum,
        "max_sum": cs_max_sum,
        "fraction": round(cs_fraction, 4),
        "contribution": round(cs_contribution, 3)
    }

    # --- Speech Rate
    sr = rubric.get("speech_rate", {})
    sr_weight = sr.get("weight", 0)
    total_weight += sr_weight
    sr_score_raw, sr_feedback = score_speech_rate(word_count, duration_seconds, sr)
    # sr rule max is 10 (per rubric)
    sr_fraction = _normalize(sr_score_raw, 10.0)
    sr_contribution = sr_fraction * sr_weight
    weighted_score_sum += sr_contribution
    results["components"]["speech_rate"] = {
        "weight": sr_weight,
        "raw": sr_score_raw,
        "max": 10.0,
        "fraction": round(sr_fraction, 4),
        "contribution": round(sr_contribution, 3),
        "feedback": sr_feedback
    }

    # --- Language & Grammar (grammar + vocabulary)
    lang = rubric.get("language_and_grammar", {})
    lang_weight = lang.get("weight", 0)
    total_weight += lang_weight
    lang_subscores = {}

    # Grammar
    gram_score_raw, gram_errors = grammar_score(transcript, word_count)
    gram_max = lang.get("grammar", {}).get("weight", 10)
    lang_subscores["grammar"] = {"raw": gram_score_raw, "max": gram_max, "errors": gram_errors}

    # Vocabulary (TTR)
    vocab_score_raw, ttr_val = vocabulary_score(words)
    vocab_max = lang.get("vocabulary", {}).get("weight", 10)
    lang_subscores["vocabulary"] = {"raw": vocab_score_raw, "max": vocab_max, "ttr": round(ttr_val, 3)}

    lang_raw_sum = lang_subscores["grammar"]["raw"] + lang_subscores["vocabulary"]["raw"]
    lang_max_sum = lang_subscores["grammar"]["max"] + lang_subscores["vocabulary"]["max"]
    lang_fraction = _normalize(lang_raw_sum, lang_max_sum)
    lang_contribution = lang_fraction * lang_weight
    weighted_score_sum += lang_contribution

    results["components"]["language_and_grammar"] = {
        "weight": lang_weight,
        "subscores": lang_subscores,
        "raw_sum": lang_raw_sum,
        "max_sum": lang_max_sum,
        "fraction": round(lang_fraction, 4),
        "contribution": round(lang_contribution, 3)
    }

    # --- Clarity (filler words)
    clarity = rubric.get("clarity", {})
    clarity_weight = clarity.get("weight", 0)
    total_weight += clarity_weight
    filler_score_raw, filler_feedback = score_filler_words(filler_count, word_count, clarity)
    filler_max = 15.0  # per rubric
    filler_fraction = _normalize(filler_score_raw, filler_max)
    filler_contribution = filler_fraction * clarity_weight
    weighted_score_sum += filler_contribution

    results["components"]["clarity"] = {
        "weight": clarity_weight,
        "raw": filler_score_raw,
        "max": filler_max,
        "fraction": round(filler_fraction, 4),
        "contribution": round(filler_contribution, 3),
        "feedback": filler_feedback,
        "filler_count": filler_count
    }

    # --- Engagement (sentiment)
    engagement = rubric.get("engagement", {})
    engagement_weight = engagement.get("weight", 0)
    total_weight += engagement_weight
    sent_score_raw, polarity = sentiment_score(transcript)
    sent_max = 15.0
    sent_fraction = _normalize(sent_score_raw, sent_max)
    sent_contribution = sent_fraction * engagement_weight
    weighted_score_sum += sent_contribution

    results["components"]["engagement"] = {
        "weight": engagement_weight,
        "raw": sent_score_raw,
        "max": sent_max,
        "fraction": round(sent_fraction, 4),
        "contribution": round(sent_contribution, 3),
        "feedback": f"Positive polarity (pos) = {polarity:.3f}"
    }

    # Final overall normalization to 0-100
    if total_weight <= 0:
        overall_pct = 0.0
    else:
        # weighted_score_sum is already on the rubric-weight scale; divide by total_weight to get 0-1 then *100
        overall_frac = weighted_score_sum / total_weight
        overall_pct = round(overall_frac * 100.0, 2)

    results["total_weight"] = total_weight
    results["weighted_score_sum"] = round(weighted_score_sum, 3)
    results["overall_score"] = overall_pct

    # Build textual feedback summary
    feedback_lines = []
    # Content
    cs_feedback = results["components"]["content_and_structure"]
    feedback_lines.append(f"Content & Structure: {cs_feedback['fraction']*100:.1f}% of {cs_weight} -> contribution {cs_feedback['contribution']:.2f}.")
    feedback_lines.append(f" - Salutation: {cs_subscores['salutation']['feedback']}")
    feedback_lines.append(f" - Keywords: {cs_subscores['keyword_presence']['feedback']}")
    feedback_lines.append(f" - Flow: {cs_subscores['flow']['feedback']}")
    # Speech rate
    feedback_lines.append(f"Speech Rate: {results['components']['speech_rate']['feedback']}")
    # Grammar & Vocab
    feedback_lines.append(f"Grammar: {lang_subscores['grammar']['raw']} / {lang_subscores['grammar']['max']} ({lang_subscores['grammar']['errors']} grammar issues)")
    feedback_lines.append(f"Vocabulary (TTR): {lang_subscores['vocabulary']['ttr']:.3f} -> score {lang_subscores['vocabulary']['raw']}/{lang_subscores['vocabulary']['max']}")
    # Clarity and engagement
    feedback_lines.append(f"Filler words: {filler_feedback}")
    feedback_lines.append(f"Engagement: {results['components']['engagement']['feedback']}")

    results["feedback_summary"] = "\n".join(feedback_lines)

    return results


if __name__ == "__main__":
    # quick local test harness
    
    rubric = load_rubric()
    out = compute_scores(sample, duration_seconds=20.0, rubric=rubric)
    import pprint
    pprint.pprint(out)
