from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import nltk

nltk.download('punkt')

#Обработка данных с TF-IDF
async def extract_key_sentences_tfidf(text, num_sentences=3):
    sentences = nltk.sent_tokenize(text)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    sentence_scores = np.array(tfidf_matrix.mean(axis=1)).flatten()

    top_sentence_indices = sentence_scores.argsort()[-num_sentences:]

    key_sentences = [sentences[i] for i in sorted(top_sentence_indices)]

    return ' '.join(key_sentences)

