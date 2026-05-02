import ollama  

def get_mood_playlist(mood):
    prompt = f"""
    You are a music expert and DJ. 
    Someone is feeling: "{mood}"
    
    Suggest 5 songs that perfectly match this mood.
    For each song give:
    - Song name
    - Artist  
    - One sentence on why it fits this mood
    
    Format each as:
    🎵 [Song] - [Artist]
    Why: [reason]
    """
    
    response = ollama.chat(
        model='gemma3',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return response['message']['content']

print("🎵 Welcome to MoodPlay")
print("Tell me how you're feeling and I'll find your songs.\n")

while True:
    mood = input("How are you feeling? (or 'quit'): ")
    if mood.lower() == 'quit':
        break
    
    print("\nFinding your playlist...\n")
    playlist = get_mood_playlist(mood)
    print(playlist)
    print("\n" + "="*50 + "\n")