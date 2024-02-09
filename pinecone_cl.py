from pinecone import Pinecone


class PineconeCl:
    def __init__(self):
        api_key = "6aebc88c-6cae-490b-b313-571fa563cbfc"
        pin = Pinecone(api_key=api_key, environment='us-west1-gcp')
        self.index_pincecone = pin.Index(name='job-posts')

    def query_index(self, query, filters):
        query_results = self.index_pincecone.query(vector=
                                                   query,
                                                   top_k=100,
                                                   include_metadata=False,
                                                   filter=filters
                                                   )
        return query_results.get('matches')
