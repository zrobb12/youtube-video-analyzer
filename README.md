# youtube-video-analyzer
This is a Python CLI tool to fetch, transcribe, and summarize YouTube videos using OpenAI-compatible large language models via the Venice or Morpheus APIs. You can also ask questions about the video after summarization.

---

## Features

- Fetch and transcribe YouTube videos (English only, if transcripts available).
- Summarize video transcripts using Venice or Morpheus LLMs.
- Ask questions about the video content interactively.
- Fully customizable summary prompt.
- Keeps your API keys safe via `.env` file (not committed to GitHub).

---

## Installation & Setup

### 1. **Clone the Repository**

Open **Command Prompt** (not Bash!) and run:

```cmd
git clone https://github.com/zrobb12/youtube-video-summarizer.git
cd youtube-video-summarizer
```

### 2. **Create and Activate a Virtual Environment (Recommended)**

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. **Install Required Packages**

```cmd
pip install -r requirements.txt
```

### 4. **Setup Your `.env` File**

Create a file named `.env` in the project folder with the following content (replace the dummy values with your real API keys):

```
VENICE_API_KEY=your_venice_api_key
VENICE_BASE_URL=https://api.venice.ai/api/v1
MORPHEUS_API_KEY=your_morpheus_api_key
MORPHEUS_BASE_URL=https://api.mor.org/api/v1
```

**Never share or commit your `.env` file!**

---

## Usage

```cmd
python youtube_summarizer.py "<YouTube URL or ID>" [--provider venice|morpheus] [--test-transcript] [--output <filename>] [--prompt <custom prompt>]
```

### **Examples**

- **Summarize a YouTube video (default: Venice API):**
    ```cmd
    python youtube_summarizer.py "https://www.youtube.com/watch?v=aStf54Vxy24"
    ```

- **Use Morpheus API:**
    ```cmd
    python youtube_summarizer.py "https://www.youtube.com/watch?v=aStf54Vxy24" --provider morpheus
    ```

- **Provide a custom summary prompt:**
    ```cmd
    python youtube_summarizer.py "https://www.youtube.com/watch?v=aStf54Vxy24" --prompt "List the main arguments and counterarguments in this video."
    ```

- **Fetch and save just the transcript:**
    ```cmd
    python youtube_summarizer.py "https://www.youtube.com/watch?v=aStf54Vxy24" --test-transcript --output transcript.txt
    ```
