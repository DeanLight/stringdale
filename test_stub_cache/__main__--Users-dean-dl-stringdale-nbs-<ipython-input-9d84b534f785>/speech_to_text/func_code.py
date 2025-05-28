# first line: 1
@disk_cache.cache
async def speech_to_text(audio_path: str, model: str = "whisper-1") -> Dict[str,str]:
    """Extract text from an audio file using OpenAI's Whisper model.
    
    Args:
        audio_path (str): Path to the audio file
        model (str, optional): OpenAI model to use. Defaults to "whisper-1".
    
    Returns:
        dict: A dictionary containing:  
            - role (str): Always "assistant"
            - content (str): Transcribed text from the audio
    """
    
    with open(audio_path, "rb") as audio_file:
        response = await async_openai_client.audio.transcriptions.create(
            model=model,
            file=audio_file
        )
    
    res =  {
        'role':'assistant',
        'content':response.text,
    }
    
    return res
