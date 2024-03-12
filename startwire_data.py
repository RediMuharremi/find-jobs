import pandas as pd

chunk_size = 10000
chunk_gen = pd.read_csv("daily_active_jobs_v3.csv", chunksize=chunk_size)

data = None
i = 0
for chunk in chunk_gen:
    i += 1
    if data is None:
        data = chunk.copy(deep=True)
    else:
        data = pd.concat([data, chunk])
data.drop_duplicates(subset=["Job Title", "Job Description"], inplace=True)
data = data[[
    'Id',
    'Company',
    'Job Title',
    'Job Description',
    'Job Level'
]]
print("Loaded dataframe...")


def get_job_posting(matches_ids, job_levels_filter):
    filtered_data = data[data['Id'].isin(matches_ids)]
    id_order = {id: index for index, id in enumerate(matches_ids)}
    filtered_data['Job Level'] = pd.Categorical(
        filtered_data['Job Level'], categories=job_levels_filter, ordered=True)
    filtered_data['id_order'] = filtered_data['Id'].map(id_order)
    filtered_data.sort_values(['Job Level', 'id_order'], inplace=True)
    filtered_data.drop('id_order', axis=1, inplace=True)
    filtered_data.reset_index(drop=True, inplace=True)

    return filtered_data.to_dict(orient='records')
