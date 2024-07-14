import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib.epub")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib.epub")

import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

from openai import OpenAI
from dotenv import load_dotenv
from docx import Document

# Load environment variables from .env file
load_dotenv()
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to summarize text with specific instructions
def summarize_text_with_chatgpt(text):
    # Create a chat completion
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant, tasked with creating a concise and "
                    "engaging summary of the provided text. The summary should begin with the key takeaway(s), followed by a section labeled 'Recap,' "
                    "and then provide a detailed summary that is approximately two-thirds the length of the original text. "
                    "The tone should be interesting, intelligent, and reflect the writing style of an Enterprise Architect."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return chat_completion.choices[0].message.content.strip()

def read_epub_book(file_name: str) -> epub.EpubBook:
    """Reads an EPUB book from the given file name."""
    return epub.read_epub(file_name)

def list_epub_items(book: epub.EpubBook):
    """Lists all items in the EPUB book for debugging purposes."""
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            print(f"ID: {item.get_id()}, Type: {item.get_type()}, Name: {item.get_name()}")
        else:
            print(f"ID: {item.get_id()}, Type: {item.get_type()}")

def extract_chapters_from_ncx(book: epub.EpubBook) -> List[Tuple[str, str]]:
    """Extracts chapters from an EPUB book using the NCX file."""
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_NAVIGATION:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            for navpoint in soup.find_all("navpoint"):
                title = navpoint.find("navlabel").get_text(strip=True)
                src = navpoint.find("content")["src"]
                chapters.append((title, src.split('#')[0]))
    return chapters

def chapter_to_str(chapter: epub.EpubHtml) -> str:
    """Converts a chapter to a string of text."""
    soup = BeautifulSoup(chapter.get_body_content(), "html.parser")
    text = [para.get_text() for para in soup.find_all("p")]
    return " ".join(text)

def extract_chapters_to_text(book: epub.EpubBook, test_mode: bool = False) -> Dict[str, str]:
    """Extracts chapters from an EPUB book and converts them to text with their titles."""
    chapters = extract_chapters_from_ncx(book)
    texts = {}
    for i, (title, src) in enumerate(chapters):
        if test_mode and i >= 2:
            break
        chapter = book.get_item_with_href(src)
        if chapter is not None:
            chapter_text = chapter_to_str(chapter)
            if chapter_text.strip():  # Ensure the chapter text is not empty
                texts[title] = chapter_text
            else:
                print(f"Warning: Chapter '{title}' is empty.")
        else:
            print(f"Warning: Chapter with href {src} not found.")
    return texts

def count_words(text: str) -> int:
    """Counts the number of words in a given text."""
    words = text.split()
    return len(words)

if __name__ == "__main__":
    # File path
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ThinkinginSystems.epub")

    # Set test_mode to True to process only the first two chapters
    test_mode = True

    book = read_epub_book(file_name)

    # List all items in the EPUB for debugging
    list_epub_items(book)

    chapters_texts = extract_chapters_to_text(book, test_mode)

    if not chapters_texts:
        print("No chapters found or extracted.")
    else:
        # Create a Word document to save the summaries
        document = Document()

        for chapter_name, chapter_text in chapters_texts.items():
            print(f"Processing chapter: {chapter_name}...")  # Debug log
            summarized_text = summarize_text_with_chatgpt(chapter_text)
            print(f"Chapter: {chapter_name}")
            print(f"Original Text: {chapter_text[:500]}...")  # Debug log, first 500 chars
            print(f"Summarized Text: {summarized_text}")

            # Add chapter name
            document.add_heading(chapter_name, level=1)

            # Split the summarized text by sections to avoid repeated headings
            sections = summarized_text.split('\n')
            added_sections = set()
            for section in sections:
                if section.startswith("Key Takeaway(s):") and "Key Takeaway(s):" not in added_sections:
                    document.add_paragraph(section)
                    added_sections.add("Key Takeaway(s):")
                elif section.startswith("Recap:") and "Recap:" not in added_sections:
                    document.add_paragraph(section)
                    added_sections.add("Recap:")
                else:
                    document.add_paragraph(section)

            # Add a section break (next page)
            document.add_page_break()

        # Save the document one folder up from the current directory
        output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Summarized_Chapters.docx")
        document.save(output_file)
        print(f"Summarized chapters saved to {output_file}")
