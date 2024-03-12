from sentence_transformers import SentenceTransformer

from pinecone_cl import PineconeCl
from startwire_data import get_job_posting
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('intfloat/multilingual-e5-small', device='cpu')
pinecone_index = PineconeCl()


def create_embedding(text: str):
    embdding_query = model.encode(text, convert_to_tensor=False).tolist()
    return embdding_query


def create_query(profile_information: dict):
    work_experience_descriptions = profile_information.get('experience')
    embdding_query = create_embedding(work_experience_descriptions)
    filters = {}

    cluster_titles = profile_information.get("Desired Position", [])
    job_type = profile_information.get("Job Type", None)
    experience_level = profile_information.get("Experience Level", None)
    if experience_level:
        filters['Job Level'] = {'$in': experience_level}
    if len(cluster_titles) > 0:
        filters['clusters'] = {'$in': cluster_titles}
    if job_type:
        filters['Job Type'] = {'$in': [job_type]}

    print(f"Filters: {filters}")

    matches = pinecone_index.query_index(embdding_query, filters)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(
        [match["metadata"]["clean_description"] for match in matches]
    )
    tf_idf_query_vector = tfidf_vectorizer.transform([work_experience_descriptions])

    cosine_similarities = cosine_similarity(tf_idf_query_vector, tfidf_matrix).flatten()
    top_k_indices = np.argsort(cosine_similarities)[::-1]
    matches_ids = [matches[i]["id"] for i in top_k_indices]

    job_postings = get_job_posting(matches_ids, experience_level)
    return job_postings
