import os

from pinecone import Pinecone


class PineconeCl:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        pc = Pinecone(api_key=api_key)
        self.pc_index = pc.Index(os.getenv("PINECONE_INDEX"))

    def query_index(self, query, filters):
        print(self.pc_index.describe_index_stats())
        query_results = self.pc_index.query(vector=query,
                                            top_k=100,
                                            include_metadata=True,
                                            filter=filters
                                            )
        return query_results.get('matches')
