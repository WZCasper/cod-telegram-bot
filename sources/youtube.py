import feedparser
from datetime import datetime, timezone

CHANNEL_ID = "UCe3VxQ8G85w03MYlE4zWv0A"  # Call of Duty
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

def fetch_new_videos(state):
    feed = feedparser.parse(RSS_URL)
    last_ids = state.get("last_ids", {})
    last_id = last_ids.get("youtube")
    new_posts = []

    if not last_id:
        if feed.entries:
            entry = feed.entries[0]
            new_posts.append(format_video_entry(entry))
            last_ids["youtube"] = entry.id
    else:
        for entry in feed.entries:
            if entry.id == last_id:
                break
            new_posts.append(format_video_entry(entry))
        if feed.entries:
            last_ids["youtube"] = feed.entries[0].id

    return new_posts, last_ids

def format_video_entry(entry):
    video_id = entry.yt_videoid
    image_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return {
        "text": entry.title,
        "link": entry.link,
        "image": image_url,
        "source": "youtube"
    }