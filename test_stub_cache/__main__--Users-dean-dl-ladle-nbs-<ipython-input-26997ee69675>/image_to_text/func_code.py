# first line: 1
@disk_cache.cache
async def image_to_text(path:str,model:str="gpt-4o-mini",url=False):
    """
    This function takes an image (either from a local file path or URL) and uses OpenAI's
    vision model to generate a detailed description of the image contents. The results are
    cached using disk_cache to avoid redundant API calls.
        
    Args:
        path (str): Path to the image file or URL of the image
        model (str, optional): OpenAI model to use for image analysis. Defaults to "gpt-4o-mini".
        url (bool, optional): Whether the path is a URL. Defaults to False.
        
    Returns:
        dict: A dictionary containing:
            - role (str): Always "assistant"
            - content (str): Detailed description of the image
            - meta (dict): Usage statistics including input and output tokens
    
    """
    if url:
        image = instructor.Image.from_url(path)
    else:
        image = instructor.Image.from_path(path)

    class ImageAnalyzer(BaseModel):
        description:str

    res,usage = await complete(
        model=model,
        messages=[{"role":"user","content":[
            "What is in this image, please describe it in detail\n",
            image,
            "\n"
        ]}],
        response_model=ImageAnalyzer,
    )
    return {
        'role':'assistant',
        'content':res.description,
        'meta':usage
    }
