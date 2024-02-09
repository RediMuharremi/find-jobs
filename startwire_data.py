import pandas as pd

df = pd.read_xml("output.xml", dtype_backend="numpy_nullable")
df.drop(columns=['remotetype', 'referencenumber', 'city', "postalcode", "additional_info", "repemail", "repfirstname", "replastname"], inplace=True)
df.drop(columns=["custom1", "custom2", "custom3", "url"], inplace=True)
df = df.drop_duplicates(subset=["title", "company", "country", "description", "experience", "jobtype", "salary"])
df.info()


def get_job_posting(postid):
    return df[df['postid'] == postid].to_dict(orient='records')[0]