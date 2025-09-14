# first line: 73
@disk_cache.cache(ignore=['response_model'])
async def complete_raw(model, messages, response_model=None, response_schema=None, mode = 'json' , seed=42,**kwargs):
    """
    This function is used to complete a chat completion with instructor without having basemodels as input or output.
    used for disk caching of results.
    """
    if mode == 'json':
        client = json_client()
    elif mode == 'tools':
        client = tools_client()
    elif mode == 'raw':
        client = raw_client()
        # For raw mode, we use the standard OpenAI client API
        completion = await client.chat.completions.create(
            model=model,
            messages=messages,
            seed=seed,
            **kwargs
        )
        usage = {
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens
        }
        # Return the raw response content and usage
        return completion.choices[0].message.content, usage
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    response, completion = await client.chat.completions.create_with_completion(
        model=model,
        messages=messages,
        response_model=response_model,
        seed=seed,
        **kwargs
    )
    usage = {
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }
    return response.model_dump_json(), usage
