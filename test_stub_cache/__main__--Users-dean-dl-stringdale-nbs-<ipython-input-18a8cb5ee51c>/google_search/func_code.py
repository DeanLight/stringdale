# first line: 1
@disk_cache.cache
def google_search(q:str,location:str='Austin, Texas',engine:str='google_scholar'):
    """Search the web for information using various search engines.

    This function performs web searches using the SerpAPI client, allowing access to
    information from different search engines including Google Scholar. Results include
    source information for verification.

    Args:
        q (str): The search query string.
        location (str, optional): The location to use for localized search results.
            Defaults to 'Austin, Texas'.
        engine (str, optional): The search engine to use. Defaults to 'google_scholar'.

    Returns:
        dict: A dictionary containing the search results and metadata from the SerpAPI
            response.

    """
    return SerpApiClient({'q':q,'location':location,'engine':engine,'serp_api_key':get_serper_api_key()}).get_dict()
