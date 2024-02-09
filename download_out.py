import gdown
import os

def ddd():
    url = 'https://drive.google.com/uc?id=1equYNAaqV75mv3oNzmM6yCU_w6MLLFG8'  # Make sure to replace 'FILE_ID' with the actual file ID
    output = 'output.xml'  # Optional: specify the name of the file to save it as
    file_exists = os.path.exists(output)
    if file_exists:
        pass
    else:
        gdown.download(url, output, quiet=False)