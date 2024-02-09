from pyresparser import ResumeParser
import os
import streamlit as st

import pandas as pd
from flashtext import KeywordProcessor

from sockit.title import clean, search, sort
import json


def title_to_soc(title: str, top_cls: int = 3) -> list[str]:
    cleaned_title = clean(title)
    soc_codes = search(cleaned_title)
    results = sort(soc_codes)[:top_cls]
    soc_titles = [result.get('title', '') for result in results]
    return soc_titles


skills_df = pd.read_csv('skills-46k.csv')
hard_skills = skills_df[skills_df['type'] == 'Hard Skill']['skill'].tolist()
soft_skills = skills_df[skills_df['type'] == 'Soft Skill']['skill'].tolist()


def _keyword_search(keywords: list[str], text: str) -> list[str]:
    keyword_processor = KeywordProcessor()

    # Add your list of skills to the keyword processor
    for skill in keywords:
        keyword_processor.add_keyword(skill)

    # Process a job posting
    extract_keywords = list(set(keyword_processor.extract_keywords(text)))
    return extract_keywords


def extract_hard_skills(text: str):
    extracted_hard_skills = _keyword_search(hard_skills, text)
    return extracted_hard_skills


def extract_soft_skills(text: str):
    extracted_soft_skills = _keyword_search(soft_skills, text)
    return extracted_soft_skills


def process_resume(uploaded_file):
    try:
        file_extension = uploaded_file.name.split('.')[-1]
        temp_file_path = f"temp_file.{file_extension}"

        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        data = ResumeParser(temp_file_path).get_extracted_data()
        os.remove(temp_file_path)
        skills = " ".join(data.get('skills', []))

        return {
            "experience": " ".join(data.get('experience', [])),
            "hard_skills": extract_hard_skills(skills),
            "soft_skills": extract_soft_skills(skills)
        }
    except Exception as e:
        st.write(f"Error processing resume: {e}")
        return {}


def process_text_field(experience_text):
    return {
        "experience": experience_text,
        "hard_skills": extract_hard_skills(experience_text),
        "soft_skills": extract_soft_skills(experience_text)
    }


def normalize_job_title(job_title):
    return title_to_soc(job_title)
