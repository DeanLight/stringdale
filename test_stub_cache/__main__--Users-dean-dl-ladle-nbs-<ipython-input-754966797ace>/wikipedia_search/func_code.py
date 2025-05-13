# first line: 1
@disk_cache.cache
def wikipedia_search(q:str):
    """
    A tool to query wikipedia, useful when you need to find information about a specific topic or person that is well known.
    Useful when you dont have enough context to reason about how to answer the question.

    Args:
        q (str): The query string to search for

    Returns:
        str: The wikipedia search results
    """

    return wikipedia.page(q).content
