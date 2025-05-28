# first line: 1
@disk_cache.cache(ignore=['response_model'])
async def complete_raw(model, messages, response_model=None, response_schema=None, mode = 'json' , **kwargs):
    """
    This function is used to complete a chat completion with instructor without having basemodels as input or output.
    used for disk caching of results.
    """
    if mode == 'json':
        client = json_client()
    elif mode == 'tools':
        client = tools_client()
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    response, completion = await client.chat.completions.create_with_completion(
        model=model,
        messages=messages,
        response_model=response_model,
        **kwargs
    )
    usage = {
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }
    return response.model_dump_json(), usage
