# first line: 69
@disk_cache.cache
async def openai_embed(text, model='text-embedding-3-small'):
    response = await async_openai_client().embeddings.create(
        input=text,
        model=model
    )
    return np.array(response.data[0].embedding)
