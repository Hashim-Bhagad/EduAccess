from django import template
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    Convert any YouTube URL to a clean embed URL.
    Handles:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&other=params
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID?si=tracking
    Removes all query parameters for clean embedding.
    """
    if not url:
        return ''
    
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',  # Standard watch URL
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',              # Short URL
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',    # Already embed URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
    
    # If no pattern matches, return original URL
    return url
