from pydantic import BaseModel,Field

class SearchQuery(BaseModel):
    """Structure for search query collection"""
    search_queries: list = Field(None, description="Search queries for retrieval.")
