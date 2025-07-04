from langgraph.store.memory import InMemoryStore
import uuid
from langchain_community.utils.math import cosine_similarity



class ContextStore:
    """Store for managing context chunks and their embeddings in memory.

    A class that provides storage and retrieval of context data using an in-memory store.
    Each context entry consists of context chunks and their corresponding embeddings.
    """

    def __init__(self):
        """Initialize ContextStore with an empty in-memory store."""
        self.store = InMemoryStore()

    def save_context(self, context_chunks: list, embeddings: list, key: str | None = None):
        """Save context chunks and their embeddings to the store.

        Args:
            context_chunks (list): List of context chunk objects
            embeddings (list): List of corresponding embeddings for the chunks
            key (str, optional): Custom key for storing the context. Defaults to None,
                               in which case a UUID is generated.

        Returns:
            str: The key used to store the context
        """
        namespace = ("context",)

        if key is None:
            key = str(uuid.uuid4())

        value = {"chunks": context_chunks, "embeddings": embeddings}

        self.store.put(namespace, key, value)
        return key

    def get_context(self, context_key: str):
        """Retrieve context data from the store using a key.

        Args:
            context_key (str): The key used to store the context

        Returns:
            dict: The stored context value containing chunks and embeddings
        """
        namespace = ("context",)
        memory = self.store.get(namespace, context_key)
        return memory.value
    
    def get_relevent_chunks(self,context_key:str,embeddings,query:str):
        context = self.get_context(context_key)
        chunks = context['chunks']
        chunk_embeddings = context['embeddings']
        query = embeddings.embed_query(query)
        similarities = cosine_similarity([query], chunk_embeddings)[0]
        top_3_indices = sorted(range(len(similarities)), 
                         key=lambda i: similarities[i], 
                         reverse=True)[:3]
        relevant_chunks = [chunks[i] for i in top_3_indices]

        return relevant_chunks

