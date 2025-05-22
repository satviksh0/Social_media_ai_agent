import streamlit as st
import asyncio
from social_media_agent import get_transcript, generate_social_media_content, Post
import time
import re

# Set page config
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="📱",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 1.2rem;
    }
    .post-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .platform-header {
        color: #1f77b4;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .error-box {
        background-color: #ffebee;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #ffcdd2;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or return the ID if it's already just the ID."""
    # If it's already just an ID (no special characters)
    if re.match(r'^[\w-]{11}$', url_or_id):
        return url_or_id
    
    # Try to extract from URL
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})',
        r'youtube\.com\/embed\/([\w-]{11})',
        r'youtube\.com\/v\/([\w-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return url_or_id  # Return as is if no pattern matches

# Title and description
st.title("🎥 Social Media Content Generator")
st.markdown("""
    Generate engaging social media content from YouTube videos. 
    Just paste a YouTube video URL or ID and let AI create platform-specific content for you!
""")

# Input section
col1, col2 = st.columns(2)

with col1:
    video_input = st.text_input(
        "YouTube Video URL or ID",
        placeholder="Enter YouTube URL or video ID (e.g., https://youtube.com/watch?v=dQw4w9WgXcQ)",
        help="You can paste either a full YouTube URL or just the video ID"
    )

with col2:
    platforms = st.multiselect(
        "Select Platforms",
        ["LinkedIn", "Twitter", "Facebook", "Instagram"],
        default=["LinkedIn", "Twitter"]
    )

# Generate button
if st.button("Generate Content", type="primary"):
    if not video_input:
        st.error("Please enter a YouTube video URL or ID")
    elif not platforms:
        st.error("Please select at least one platform")
    else:
        try:
            # Extract video ID
            video_id = extract_video_id(video_input)
            
            with st.spinner("Fetching video transcript..."):
                transcript = get_transcript(video_id)
            
            if not transcript:
                st.error("Could not fetch transcript. Please check the video URL/ID.")
            else:
                st.success("Transcript fetched successfully!")
                
                # Create a progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Store generated content
                generated_content = {}
                
                # Generate content for each platform
                for i, platform in enumerate(platforms):
                    status_text.text(f"Generating content for {platform}...")
                    
                    try:
                        # Generate content
                        content = generate_social_media_content(transcript, platform)
                        generated_content[platform] = content
                        
                        # Create a post box
                        st.markdown(f"""
                            <div class="post-box">
                                <div class="platform-header">{platform}</div>
                                <div>{content}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "insufficient_quota" in error_msg.lower():
                            st.markdown(f"""
                                <div class="error-box">
                                    <h3>⚠️ API Quota Exceeded</h3>
                                    <p>Your OpenAI API quota has been exceeded. Please check your billing details or try again later.</p>
                                </div>
                            """, unsafe_allow_html=True)
                            break
                        else:
                            st.error(f"Error generating content for {platform}: {error_msg}")
                            continue
                    
                    # Update progress
                    progress = (i + 1) / len(platforms)
                    progress_bar.progress(progress)
                
                if generated_content:
                    status_text.text("Content generation completed!")
                    
                    # Add a copy button for each post
                    st.markdown("---")
                    st.markdown("### Copy Content")
                    for platform, content in generated_content.items():
                        if st.button(f"Copy {platform} Content", key=f"copy_{platform}"):
                            st.code(content, language="text")
                            st.success(f"{platform} content copied to clipboard!")
                
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower():
                st.markdown("""
                    <div class="error-box">
                        <h3>⚠️ API Quota Exceeded</h3>
                        <p>Your OpenAI API quota has been exceeded. Please check your billing details or try again later.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"An error occurred: {error_msg}")

# Add footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit and OpenAI</p>
    </div>
""", unsafe_allow_html=True) 