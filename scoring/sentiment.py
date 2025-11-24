from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def sentiment_score(text):
    polarity = analyzer.polarity_scores(text)['pos']

    if polarity >= 0.9: score = 15
    elif polarity >= 0.7: score = 12
    elif polarity >= 0.5: score = 9
    elif polarity >= 0.3: score = 6
    else: score = 3

    return score, polarity
