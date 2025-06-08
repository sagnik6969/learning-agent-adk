from langchain_community.tools.tavily_search import TavilySearchResults

tavily_search = TavilySearchResults(max_results=3)

def search_web(search_queries:list[str],context_store,embeddings,context_key = None):
    """Retrieves and processes web search results based on search queries."""
    
    all_search_docs = []
    for query in search_queries:
        search_docs = tavily_search.invoke(query)
        all_search_docs.extend(search_docs)
    
    formatted_search_docs = [
        f'Context: {doc["content"]}\n Source: {doc["url"]}\n'
        for doc in all_search_docs
    ]

    chunk_embeddings = embeddings.embed_documents(formatted_search_docs)
    context_store.save_context(
        formatted_search_docs,
        chunk_embeddings,
        key=context_key
    )

    return {"context_chunks": formatted_search_docs}