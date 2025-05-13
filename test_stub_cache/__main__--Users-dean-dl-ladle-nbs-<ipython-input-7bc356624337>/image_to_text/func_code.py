# first line: 1
@disk_cache.cache
async def image_to_text(path:str,model:str="gpt-4o-mini",url=False):
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
