import os
import streamlit as st
import base64
import requests

from datetime import datetime
from typing import List
import ast
from typing import List, Dict, Any

import pandas as pd
from rapidfuzz import fuzz, process, utils
import re
import string

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize

STOP_WORDS = set(stopwords.words("english"))


def clean_and_preprocess(paragraph: str):
    # replace html tags (everything inside <>) with '\n'
    paragraph = re.sub(r"<[^>]+>", "\n", paragraph)
    sentences = re.sub(r"<[/^>]+>", "", paragraph)

    sentences = sent_tokenize(sentences)
    sentences = [
        part_lower
        for s in sentences
        for part in s.split("\n")
        if (part_lower := part.strip().lower())
    ]

    cleaned_sentences = []

    for sentence in sentences:
        # remove emails
        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        sentence = re.sub(email_regex, "", sentence)
        # remove URLs
        sentence = re.sub(r"http\S+|www\S+|https\S+", " ", sentence, flags=re.MULTILINE)
        # keep 'x-y years of experience'
        sentence = sentence.replace("-", " rangearange ")
        # remove punctuation
        sentence = re.sub(r"[{}]".format(string.punctuation), " ", sentence)
        # substitute back '-'
        sentence = sentence.replace(" rangearange ", " - ")
        # limit consecutive spaces to one
        sentence = re.sub(r"\s+", " ", sentence)
        # remove stopwords
        sentence = " ".join(word for word in sentence.split() if word not in STOP_WORDS)
        cleaned_sentences.append(sentence)

    return "\n".join(cleaned_sentences)

titles_df = pd.read_csv("16k_titles_with_clusters.csv")  # all titles are unique
choices = titles_df["Title"].tolist()
titles_df["Clusters"] = titles_df["Clusters"].apply(lambda x: ast.literal_eval(x))
titles_df.set_index("Title", inplace=True)
job_levels = [
    "Not Applicable",
    "Internship",
    "Entry level",
    "Associate",
    "Mid-Senior level",
    "Director",
    "Executive"
]


def normalize_title(title: str, top_cls: int = 3) -> dict[str, list[Any]]:
    results = process.extract(
        title,
        choices,
        scorer=fuzz.WRatio,
        limit=2,
        score_cutoff=50,
        processor=utils.default_process,
    )
    clusters = set()
    titles = set()

    if results:
        for tlt, _, _ in results:
            clusters.update(titles_df.at[tlt, "Clusters"])
            titles.add(tlt)

    return {"titles": list(titles), "clusters": list(clusters)}


def get_job_level_filter(years_of_experience: float):
    if years_of_experience < 1:
        return job_levels[:2]
    elif years_of_experience < 2:
        return job_levels[:3]
    elif years_of_experience < 3:
        return job_levels[:4]
    elif years_of_experience < 10:
        return job_levels[:5]
    elif years_of_experience < 12:
        return job_levels[:6]
    else:
        return job_levels


def merge_working_periods(periods: List[dict]) -> List[dict]:
    sorted_periods = sorted(periods, key=lambda x: x["start_date"])
    merged = []
    for period in sorted_periods:
        if not merged or (merged[-1]["end_date"] < period["start_date"]):
            # no overlap
            merged.append(period)
        else:
            # overlap ---> merge the current period with the last period
            merged[-1]['end_date'] = max(merged[-1]['end_date'], period['end_date'])
    return merged


def calculate_total_years_of_experience(periods: List[dict]) -> float:
    merged_periods = merge_working_periods(periods)
    total_experience = 0.0
    for job in merged_periods:
        start_date = datetime.strptime(job["start_date"], "%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.strptime(job["end_date"], "%Y-%m-%dT%H:%M:%SZ")
        total_experience += (end_date - start_date).days / 365
    return total_experience


def find_relevant_work_experiences(
        works, clusters: List[str]
):
    relevant_works = []
    for work in works:
        curr_work_clusters = normalize_title(work.get('title'))["clusters"]
        if any(cl in clusters for cl in curr_work_clusters):
            relevant_works.append(work)
    return relevant_works


def parse_resume(base64_encoded_str):
    # The URL you will be sending the POST request to
    url = os.getenv('RESUME_PARSER_URL')

    # The headers for your request
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'token': os.getenv("RESUME_PARSER_TOKEN")
    }

    # The JSON body of your request
    payload = {
        'base64_data': base64_encoded_str
    }

    # Send a POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        print('Success!')
        user_profile = response.json()
        return user_profile
    else:
        print('An error has occurred')
        return {}


def process_resume(uploaded_file):

    try:
        file_extension = uploaded_file.name.split('.')[-1]
        temp_file_path = f"temp_file.{file_extension}"

        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        with open(temp_file_path, 'rb') as pdf_file:
            # Read the file's content
            binary_pdf = pdf_file.read()
            base64_encoded_pdf = base64.b64encode(binary_pdf)
            base64_encoded_str = base64_encoded_pdf.decode('utf-8')
            os.remove(temp_file_path)
            user_profile = parse_resume(base64_encoded_str)

        target_role = user_profile['profession']
        clusters = normalize_title(target_role)["clusters"]
        work_experiences = user_profile['positions']
        relevant_work_experiences = find_relevant_work_experiences(work_experiences, clusters)
        years_of_experience = calculate_total_years_of_experience(
            [
                {"start_date": we['start_date'], "end_date": we['end_date']}
                for we in relevant_work_experiences if we.get('start_date') and we.get('end_date')
            ]
        )
        work_experience_descriptions = "\n".join(
            [
                work_experience.get('description', '')
                for work_experience in work_experiences
            ]
        )
        work_experience_descriptions = clean_and_preprocess(work_experience_descriptions)

        if user_profile == {}:
            return {}
        return {
            "Desired Position": clusters,
            "Experience Level": get_job_level_filter(years_of_experience)[::-1],
            "experience": work_experience_descriptions,

        }
    except Exception as e:
        st.write(f"Error processing resume: {e}")
        return {}
