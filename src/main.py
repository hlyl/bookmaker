import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, List

from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from docx.enum.text import WD_BREAK

# Load environment variables from .env file
load_dotenv()
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Function to correct text with specific instructions
def correct_text_with_chatgpt(text):
    # Create a chat completion
    chat_completion = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that corrects text. Your task is to correct typos, spelling errors, and small grammatical errors without altering the meaning of the text. To display a more readable format to the user, your answer must be formatted for readability",
            },
            {"role": "user", "content": text},
        ],
    )
    return chat_completion.choices[0].message.content




def read_epub_book(file_name: str) -> epub.EpubBook:
    """Reads an EPUB book from the given file name."""
    return epub.read_epub(file_name)


def extract_chapters(book: epub.EpubBook) -> List[epub.EpubHtml]:
    """Extracts chapters from an EPUB book."""
    return list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))


def chapter_to_str(chapter: epub.EpubHtml) -> str:
    """Converts a chapter to a string of text."""
    soup = BeautifulSoup(chapter.get_body_content(), "html.parser")
    text = [para.get_text() for para in soup.find_all("p")]
    return " ".join(text)


def extract_chapters_to_text(file_name: str) -> Dict[str, str]:
    """Extracts chapters from an EPUB book and converts them to text."""
    book = read_epub_book(file_name)
    chapters = extract_chapters(book)
    texts = {chapter.get_name(): chapter_to_str(chapter) for chapter in chapters}
    return texts

def count_words(text: str) -> int:
    """Counts the number of words in a given text."""
    words = text.split()
    return len(words)

if __name__ == "__main__":
    #file_name = "ThinkinginSystems.epub"
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ThinkinginSystems.epub")
    print(file_name)
    chapters_texts = extract_chapters_to_text(file_name)
    for chapter_name, chapter_text in chapters_texts.items():
        print(f"Chapter: {chapter_name}")
        # Print the first 100 characters for brevity
        print(f"word count for the chapter: {count_words(chapter_text)}")
