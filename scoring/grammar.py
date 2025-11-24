import language_tool_python

tool = language_tool_python.LanguageTool('en-US')

def grammar_score(text, total_words):
    matches = tool.check(text)
    errors = len(matches)
    
    if total_words == 0:
        return 10, 0

    errors_per_100 = (errors / total_words) * 100
    score_ratio = 1 - min(errors_per_100 / 10, 1)

    if score_ratio >= 0.9: score = 10
    elif score_ratio >= 0.7: score = 8
    elif score_ratio >= 0.5: score = 6
    elif score_ratio >= 0.3: score = 4
    else: score = 2

    return score, errors
