# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from download_out import ddd
ddd()
import nltk
nltk.download('stopwords')
import streamlit as st
from streamlit.logger import get_logger
from profile_data import process_resume, process_text_field, normalize_job_title
from query_data import create_query


LOGGER = get_logger(__name__)


def run():
   



  st.title('Job Recommendation System')


  # Define options for job type and experience level
  job_type_options = [
      "", "Full-time", "Contract", "Part-time",
      "Volunteer", "Temporary", "Internship"
  ]

  experience_level_options = [
      "", "Entry level", "Mid-Senior level",
      "Director", "Internship", "Executive"
  ]

  profile_information = {}

  # Initialize session state variables if they're not already set
  if 'resume_uploaded' not in st.session_state:
      st.session_state['resume_uploaded'] = False
  if 'manual_entry' not in st.session_state:
      st.session_state['manual_entry'] = False
  if 'show_optional_fields' not in st.session_state:
      st.session_state['show_optional_fields'] = False

  # Initialize or update session state variables
  if 'submitted' not in st.session_state:
      st.session_state['submitted'] = False
  if 'matches' not in st.session_state:
      st.session_state['matches'] = []

  if not st.session_state['submitted']:
      # Main interface for initial choices
      if not st.session_state['show_optional_fields']:
          st.subheader("Please choose one of the following options to proceed:")
          col1, col2 = st.columns(2)
          with col1:
              if st.button("Upload Resume"):
                  st.session_state['resume_uploaded'] = True
          with col2:
              if st.button("Enter Information Manually"):
                  st.session_state['manual_entry'] = True

      # Interface for resume upload
      if st.session_state['resume_uploaded']:
          uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
          if uploaded_file is not None:
              profile_information = process_resume(uploaded_file)
              if profile_information.get('experience'):
                  st.session_state['show_optional_fields'] = True

      # Interface for manual information entry

      if st.session_state['manual_entry']:
          experience_text = st.text_area("Enter your work experience")
          if experience_text:
              profile_information = process_text_field(experience_text)
              st.session_state['show_optional_fields'] = True  # Show optional fields after entering experience

      if st.session_state['show_optional_fields']:
          desired_position = st.text_input("Desired Position", placeholder="Optional")
          job_type = st.selectbox("Job Type", [""] + job_type_options, format_func=lambda x: "Optional" if x == "" else x)
          experience_level = st.selectbox("Experience Level", [""] + experience_level_options,
                                          format_func=lambda x: "Optional" if x == "" else x)

          # Submit button for the optional fields
          if st.button("Submit Optional Information"):
              # Process and display the optional information
              profile_information["Desired Position"] = normalize_job_title(desired_position) if desired_position else []
              profile_information["Job Type"] = job_type if job_type else ""
              profile_information["Experience Level"] = experience_level if experience_level else ""
              # st.write("Optional Information Submitted:", profile_information)
              matches = create_query(profile_information)
              st.session_state['matches'] = matches
              st.session_state['submitted'] = True


  # def display_match(match):
  #     st.subheader(match["title"])
  #     st.write("Date:", match["date"])
  #     st.write("Company:", match["company"])
  #     st.write("Description:", match["description"])
  #     st.write("Job Type:", match["jobtype"])
  #     st.write("Experience Level:", match["experience"])
  #     st.markdown(f"[Apply Here]({match['apply_url']})")


  def display_match(match):
      # Use st.container to create a box-like structure around each job post
      with st.container():
          st.subheader(match["title"])
          st.write(f"**Company:** {match['company']}")
          st.write(f"**Date:** {match['date']}")
          st.write(f"**Job Type:** {match['jobtype']}")
          st.write(f"**Experience Level:** {match['experience']}")

          # Use st.expander to hide the full description and apply link, making them expandable
          with st.expander("View Details"):
              st.write(match["description"])
              st.markdown(f"[Apply Here]({match['apply_url']})", unsafe_allow_html=True)

          # Add a visual separator for clarity between job posts
          st.markdown("---")



  if st.session_state['submitted']:
      st.title("Job Matches")
      for match in st.session_state['matches']:
          display_match(match)

  # Function to display each job match



if __name__ == "__main__":
    run()
