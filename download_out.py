import gdown
import os

def ddd():
    url = 'https://drive.google.com/uc?id=1BzzdNI_7jkvYXxwLpJ7si4vusj0bbL-C'  # Make sure to replace 'FILE_ID' with the actual file ID
    output = 'daily_active_jobs_v3.csv'  # Optional: specify the name of the file to save it as
    file_exists = os.path.exists(output)
    if file_exists:
        pass
    else:
        gdown.download(url, output, quiet=False)