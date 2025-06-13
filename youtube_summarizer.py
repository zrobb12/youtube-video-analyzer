from dotenv import load_dotenv
load_dotenv()
import sys
import os
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import re
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Load API keys ONLY from environment variables (no hardcoded defaults!)
VENICE_API_KEY = os.environ.get("VENICE_API_KEY")
VENICE_BASE_URL = os.environ.get("VENICE_BASE_URL", "https://api.venice.ai/api/v1")
MORPHEUS_API_KEY = os.environ.get("MORPHEUS_API_KEY")
MORPHEUS_BASE_URL = os.environ.get("MORPHEUS_BASE_URL", "https://api.mor.org/api/v1")

def get_llm(provider="venice"):
    if provider == "morpheus":
        if not MORPHEUS_API_KEY:
            raise ValueError("Please set the MORPHEUS_API_KEY environment variable.")
        client = OpenAI(api_key=MORPHEUS_API_KEY, base_url=MORPHEUS_BASE_URL)
        model = "gpt-4o"
    else:
        if not VENICE_API_KEY:
            raise ValueError("Please set the VENICE_API_KEY environment variable.")
        client = OpenAI(api_key=VENICE_API_KEY, base_url=VENICE_BASE_URL)
        model = "gpt-4o"
    return client, model

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([x['text'] for x in transcript])
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        print(f"Could not retrieve transcript: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching transcript: {e}")
        return None

def summarize_with_llm(client, model, text, custom_prompt=None):
    if custom_prompt:
        prompt = f"{custom_prompt}\n\n{text}"
    else:
        prompt = f"Summarize the following YouTube video transcript:\n\n{text}\n\nSummary:"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def answer_question_with_llm(client, model, transcript, question):
    prompt = (
        f"Based on the following YouTube video transcript, answer the user's question as accurately as possible.\n\n"
        f"Transcript:\n{transcript}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    def is_youtube_url_or_id(arg):
        return (
            re.match(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/", arg)
            or re.match(r"^[a-zA-Z0-9_-]{11}$", arg)
        )

    provider = "venice"
    test_transcript = False
    output_file = None
    url = None
    custom_prompt = None
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--test-transcript":
            test_transcript = True
        elif arg.startswith("--provider"):
            parts = arg.split("=")
            if len(parts) == 2:
                provider = parts[1].strip().lower()
            else:
                provider = sys.argv[i+1].strip().lower() if i+1 < len(sys.argv) else "venice"
                i += 1
        elif arg == "--output" and i+1 < len(sys.argv):
            output_file = sys.argv[i+1]
            i += 1
        elif arg.startswith("--prompt"):
            if "=" in arg:
                custom_prompt = arg.split("=", 1)[1].strip()
            elif i+1 < len(sys.argv):
                custom_prompt = sys.argv[i+1]
                i += 1
        elif url is None and is_youtube_url_or_id(arg):
            url = arg
        i += 1
    if not url:
        print("Usage: python youtube_summarizer.py <YouTube URL> [--provider venice|morpheus] [--test-transcript] [--output <filename>] [--prompt <custom prompt>]")
        sys.exit(1)
    video_id = get_video_id(url)
    if test_transcript:
        print("Fetching transcript...")
        transcript = get_transcript(video_id)
        if transcript is None:
            sys.exit(1)
        print("\n--- Transcript ---\n")
        print(transcript)
        if not output_file:
            output_file = f"transcript_{video_id}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"\nTranscript saved to {output_file}")
        sys.exit(0)
    client, model = get_llm(provider)
    print("Fetching transcript...")
    transcript = get_transcript(video_id)
    if transcript is None:
        sys.exit(1)
    print(f"Summarizing with {provider.title()} API...")
    summary = summarize_with_llm(client, model, transcript, custom_prompt=custom_prompt)
    print("\n--- Video Summary ---\n")
    print(summary)

    while True:
        question = input("\nAsk a question about the video (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break
        answer = answer_question_with_llm(client, model, transcript, question)
        print("\nAnswer:", answer)