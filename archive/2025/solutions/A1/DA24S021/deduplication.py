# # Module 5: De-duplication Check
# # deduplication.py

import psycopg2
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import numpy as np

# Load a sentence embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_existing_headlines(db_config):
    """Fetch all existing headlines from the database."""
    try:
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, headline FROM headlines;")
        existing_headlines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return existing_headlines  # List of (id, headline)
    
    except Exception as e:
        logging.error(f"Database error while fetching headlines: {e}")
        return []

def cosine_similarity_tfidf(text1, text2):
    """Compute cosine similarity between two headlines using TF-IDF."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = np.dot(tfidf_matrix[0].toarray(), tfidf_matrix[1].toarray().T)[0][0]
    return similarity

def semantic_similarity(text1, text2):
    """Compute semantic similarity using sentence embeddings."""
    emb1 = embedding_model.encode(text1, convert_to_tensor=True)
    emb2 = embedding_model.encode(text2, convert_to_tensor=True)
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity.item()

def is_duplicate(story, db_config, threshold=0.85):
    """Check if a story is already in the database using NLP-based similarity."""
    existing_headlines = get_existing_headlines(db_config)
    dups = 0
    for _, existing_headline in existing_headlines:
        tfidf_sim = cosine_similarity_tfidf(story["headline"], existing_headline)
        sem_sim = semantic_similarity(story["headline"], existing_headline)

        # Consider it duplicate if either similarity measure is above the threshold
        if tfidf_sim > threshold or sem_sim > threshold:
            dups += 1
            # logging.info(f"Duplicate found based on similarity: {story['headline']}")
            return True
    logging.info(f"{dups} duplicates found")

    return False



# def is_duplicate(story, db_config):
#     """Check if a story is already in the database."""
#     try:
#         conn = psycopg2.connect(
#             dbname=db_config["dbname"],
#             user=db_config["user"],
#             password=db_config["password"],
#             host=db_config["host"],
#             port=db_config["port"]
#         )
#         cursor = conn.cursor()
        
#         cursor.execute("SELECT id FROM headlines WHERE url = %s OR headline = %s;", (story["url"], story["headline"]))
#         result = cursor.fetchone()
        
#         cursor.close()
#         conn.close()
#         return result is not None
#     except Exception as e:
#         logging.error(f"Database error while checking duplication: {e}")
#         return False

