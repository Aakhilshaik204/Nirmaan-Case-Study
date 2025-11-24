from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_similarity(text, target_phrases):
    text_emb = model.encode(text)
    scores = []

    for phrase in target_phrases:
        phrase_emb = model.encode(phrase)
        sim = float(util.pytorch_cos_sim(text_emb, phrase_emb))
        scores.append(sim)

    return sum(scores) / len(scores)
