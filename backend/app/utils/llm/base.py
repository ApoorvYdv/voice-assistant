from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer


class LLMWrapper(object):
    def convert_to_graph_documents(self, chunkId_chunkDoc_list):
        self.llm_transformer = LLMGraphTransformer(llm=self.get_llm())

        documents = self.get_combined_chunks(chunkId_chunkDoc_list)
        graph_document = self.llm_transformer.convert_to_graph_documents(
            documents=documents
        )
        return graph_document

    def add_graph_documents(self, graph, graph_documents):
        graph.add_graph_documents(graph_documents)

    def get_llm(self):
        raise NotImplementedError

    def get_combined_chunks(self, chunkId_chunkDoc_list):
        chunks_to_combine = 20
        combined_chunk_document_list = []
        combined_chunks_page_content = [
            "".join(
                document["chunk_doc"].page_content
                for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
            )
            for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
        ]
        combined_chunks_ids = [
            [
                document["chunk_id"]
                for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
            ]
            for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
        ]

        for i in range(len(combined_chunks_page_content)):
            combined_chunk_document_list.append(
                Document(
                    page_content=combined_chunks_page_content[i],
                    metadata={"combined_chunk_ids": combined_chunks_ids[i]},
                )
            )
        return combined_chunk_document_list

    def load_embedding_model(self):
        return NotImplementedError
