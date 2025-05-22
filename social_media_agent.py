#---------------------------------
# Step 1:Import packages and modules
#---------------------------------
import os
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Any
import json

#---------------------------------
# Step 2: Get OPENAI API key
#---------------------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=openai_api_key)

#---------------------------------
# Step 3: Define data structures and helper functions
#---------------------------------
@dataclass 
class Post:
    platform: str
    content: str

def generate_social_media_content(video_transcript: str, social_media_platform: str) -> str:
    """
    Generate social media content from a video transcript.
    
    Args:
        video_transcript (str): The transcript of the video
        social_media_platform (str): The target social media platform
        
    Returns:
        str: Generated social media content
    """
    print(f"Generating social media content for {social_media_platform}....")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a social media expert. Generate engaging content for social media platforms based on the given video transcript."},
            {"role": "user", "content": f"Video transcript: {video_transcript}\nSocial media platform: {social_media_platform}\n\nPlease generate a post that is engaging, informative, and appropriate for the platform."}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

def get_transcript(video_id: str) -> str:
    """
    Fetch and process transcript from a YouTube video.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        str: The concatenated transcript text
        
    Raises:
        Exception: If there's an error fetching the transcript
    """
    if not video_id:
        raise ValueError("Video ID cannot be empty")
        
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.get_transcript(video_id)
        
        if not fetched_transcript:
            raise Exception("No transcript found for the video")
            
        transcript_text = " ".join(snippet["text"] for snippet in fetched_transcript)
        return transcript_text
        
    except Exception as e:
        raise Exception(f"Error fetching transcript for video {video_id}: {str(e)}")

#---------------------------------
# Step 4: Main execution
#---------------------------------
async def main():
    try:
        # Example video ID
        video_id = "zOFxHmjIhvY"
        
        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            raise ValueError("Failed to get transcript")

        # Generate content for different platforms
        platforms = ["LinkedIn", "Twitter", "Facebook"]
        posts = []
        
        for platform in platforms:
            content = generate_social_media_content(transcript, platform)
            posts.append(Post(platform=platform, content=content))
            print(f"\nGenerated {platform} post:\n{content}\n")
            print("-" * 80)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())