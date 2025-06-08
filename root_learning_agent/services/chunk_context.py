
from semantic_router.encoders import OpenAIEncoder
from semantic_chunkers import StatisticalChunker

def extract_content_from_chunks(chunks):
    """Extract and combine content from chunks with splits attribute.
    
    Args:
        chunks: List of chunk objects that may contain splits attribute
        
    Returns:
        str: Combined content from all chunks joined with newlines
    """
    content = []
    
    for chunk in chunks:
        if hasattr(chunk, 'splits') and chunk.splits:
            chunk_content = ' '.join(chunk.splits)
            content.append(chunk_content)
    
    return '\n'.join(content)


def chunk_context(context:str,embeddings,context_store,context_key = None):
    """Splits context into manageable chunks and generates their embeddings."""
    encoder = OpenAIEncoder(name="text-embedding-3-large")
    chunker = StatisticalChunker(
        encoder=encoder,
        min_split_tokens=128,
        max_split_tokens=512
    )
    
    chunks = chunker([context])
    content = []
    for chunk in chunks:
        content.append(extract_content_from_chunks(chunk))

    chunk_embeddings = embeddings.embed_documents(content)
    context_key = context_store.save_context(
        content,
        chunk_embeddings,
        key=context_key
    )
    return {"context_chunks": content, "context_key": context_key}