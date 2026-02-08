from dotenv import load_dotenv
import requests
import os
import sys
import re
import asyncio
from typing import List, Dict, Optional


# ==========================
# CONFIG
# ==========================
API_URL = "https://api.k2think.ai/v1/chat/completions"
MODEL_NAME = "MBZUAI-IFM/K2-Think-v2"

# Read API key from environment variable
load_dotenv()
API_KEY = os.getenv("K2THINK_API_KEY")

if not API_KEY:
    print("❌ Error: K2THINK_API_KEY environment variable not set.")
    print("Run this first:")
    print('  export K2THINK_API_KEY="your-api-key-here"')
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def generate_story(user_prompt):
    payload = {
        "model": "MBZUAI-IFM/K2-Think-v2",
        "messages": [
            {
                "role": "system",
                "content": (
                    """
                    You are a professional children’s storybook writer with 20 years of experience writing for children ages 4–8.
                    Write a whimsical, gentle, and encouraging children’s storybook with the following requirements:
                    - 6 pages total.
                    - Don't use any name for the characters.
                    - Don't use any pronouns for the characters.
                    - Each page contains 1–2 short sentences.
                    - Clear beginning, middle, and end.
                    - Light rhyming throughout.
                    - Easy to read aloud.
                    - Focus on ONE clear child-friendly lesson.

                    Formatting rules:
                    - Label each section as "Page 1:", "Page 2:", etc.
                    - The output must begin with "Page 1:" and end with the final page.
                    - No text is allowed before or after the story.

                    Restrictions:
                    - Do NOT include explanations, analysis, reasoning, planning, or commentary.
                    - Do NOT mention being an AI or following instructions.
                    - Output ONLY the story text.

                    """
                )
            },
            {
                "role": "user",
                "content": f'Write a story centered around the following topic: "{user_prompt}"'
            }
        ],
        "stream": False
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def extract_final_story(text):
    """
    Extracts the final story starting from the LAST occurrence of 'Page 1:'.
    Assumes the correct formatted story is at the end of the output.
    """
    matches = list(re.finditer(r"Page\s*1:", text))
    if not matches:
        return None  # or return text.strip()

    start_index = matches[-1].start()
    return text[start_index:].strip()

def story_to_pages_json(story_text):
    """
    Converts a story formatted as:
    Page 1: ...
    Page 2: ...
    into a list of JSON-ready dicts.
    """

    pattern = r"Page\s+(\d+):\s*(.*?)(?=\nPage\s+\d+:|\Z)"
    matches = re.findall(pattern, story_text, re.DOTALL)

    pages = []
    for page_num, content in matches:
        cleaned_content = " ".join(content.split())
        pages.append({
            "page": int(page_num),
            "text": cleaned_content
        })

    return pages

def generate_full_story(user_input):
    story = generate_story(user_input)
    story = extract_final_story(story)
    story = story_to_pages_json(story)
    return story


# ==========================
# ASYNC WRAPPERS FOR FASTAPI
# ==========================

async def generate_story_pages(prompt: str, style: str = "fantasy") -> List[Dict]:
    """
    Async wrapper: calls existing generate_full_story() asynchronously.
    Used for FastAPI backend integration.

    Args:
        prompt: User-provided story topic/keywords
        style: Story style (currently unused but reserved for future extension)

    Returns:
        List[Dict]: Story per page
        [
            {"page": 1, "text": "Once upon a time..."},
            {"page": 2, "text": "The brave robot..."},
            ...
        ]

    Example:
        >>> pages = await generate_story_pages("brave robot in magical forest")
        >>> print(pages[0])
        {"page": 1, "text": "Once upon a time, in a magical forest..."}
    """
    # Run synchronous function in async context
    loop = asyncio.get_event_loop()
    pages = await loop.run_in_executor(None, generate_full_story, prompt)
    return pages


async def get_page_text(pages: List[Dict], page_number: int) -> Optional[str]:
    """
    Extract text for a specific page only.

    Args:
        pages: List of pages
        page_number: Page number (1-based)

    Returns:
        Text for that page, or None if not found
    """
    for page in pages:
        if page.get("page") == page_number:
            return page.get("text")
    return None


def get_full_story_text(pages: List[Dict]) -> str:
    """
    Concatenate page list into a single text.

    Args:
        pages: List of pages

    Returns:
        Full story text (no page boundaries)
    """
    return " ".join([page.get("text", "") for page in pages])


