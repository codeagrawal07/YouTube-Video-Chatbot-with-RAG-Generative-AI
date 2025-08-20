# import streamlit as st
import pathlib
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(youtube_url):
    try:
        query = urlparse(youtube_url)
        if query.hostname == "youtu.be":
            return query.path[1:]
        if query.hostname in ("www.youtube.com","youtube.com"):
            return parse_qs(query.query)["v"][0]
        return None
    except Exception as e:
        # st.error(f"Could not extract video ID: {e}")
        print(f"Could not extract video ID: {e}")
        return None

def extract_transcript_details(youtube_url):
    try:
        video_id = get_video_id(youtube_url)
        print(video_id)
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        clear_text=""
            # is iterable
        for snippet in fetched_transcript:
                clear_text+=" "+snippet.text
        return clear_text
    except Exception as e:
        # st.error(f"Transcript could not be fetched: {e}")
        print(f"Transcript could not be fetched: {e}")
        return None
