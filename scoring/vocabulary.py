def vocabulary_score(words):
    if len(words) == 0:
        return 10, 1.0

    distinct = len(set(words))
    ttr = distinct / len(words)

    if ttr >= 0.9: score = 10
    elif ttr >= 0.7: score = 8
    elif ttr >= 0.5: score = 6
    elif ttr >= 0.3: score = 4
    else: score = 2

    return score, ttr
