from sentence_transformers import SentenceTransformer

from pinecone_cl import PineconeCl
from startwire_data import get_job_posting

model = SentenceTransformer('intfloat/multilingual-e5-small', device='cpu')
pinecone_index = PineconeCl()


def create_embedding(text: str):
    embdding_query = model.encode(text, convert_to_tensor=False).tolist()
    return embdding_query


def create_query(profile_information: dict):
    embdding_query = create_embedding(profile_information.get('experience'))
    filters = {}


    hard_skills = profile_information.get("hard_skills", [])
    soft_skills = profile_information.get("soft_skills", [])
    cluster_titles = profile_information.get("Desired Position", [])
    job_type = profile_information.get("Job Type", "")
    experience_level = profile_information.get("Experience Level", "")
    if experience_level != "":
        filters['experience_level'] = {'$in': [experience_level, "Not Applicable"]}
    if len(hard_skills) > 0:
        filters['hard_skills'] = {'$in': hard_skills}
    if len(soft_skills) > 0:
        filters['soft_skills'] = {'$in': soft_skills}
    if len(cluster_titles) > 0:
        filters['cluster_titles'] = {'$in': cluster_titles}
    if job_type:
        filters['jobtype'] = {'$in': [job_type]}

    print(f"Filters: {filters}")

    matches = pinecone_index.query_index(embdding_query, filters)
    job_postings = [get_job_posting(match['id']) for match in matches]
    return job_postings
