# first line: 1
@disk_cache.cache
def google_search(q:str,location:str='Austin, Texas',engine:str='google_scholar'):
    """Search the web for information,
    useful when you need to find a piece of information that you dont have access to, sources are included
    """
    return SerpApiClient({'q':q,'location':location,'engine':engine,'serp_api_key':get_serper_api_key()}).get_dict()
