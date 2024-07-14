import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, List

from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from docx.enum.text import WD_BREAK
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib.epub")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib.epub")

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
                    "You are an assistant with expertise in prompt engineering, tasked with creating a concise and "
                    "engaging summary of the provided text. The summary should begin with the key takeaway(s), "
                    "followed by a section labeled 'Recap,' and then provide a detailed summary that is approximately "
                    "two-thirds the length of the original text. The tone should be interesting, intelligent, and reflect the "
                    "writing style of an Enterprise Architect at a global pharma company transitioning from an old IT "
                    "setup to a modern agile and cloud-based development methodology."
                ),
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

def extract_chapters_to_text(file_name: str, test_mode: bool = False) -> Dict[str, str]:
    """Extracts chapters from an EPUB book and converts them to text."""
    book = read_epub_book(file_name)
    chapters = extract_chapters(book)
    if test_mode:
        chapters = chapters[:2]
    texts = {chapter.get_name(): chapter_to_str(chapter) for chapter in chapters}
    return texts

def count_words(text: str) -> int:
    """Counts the number of words in a given text."""
    words = text.split()
    return len(words)

if __name__ == "__main__":
    # File path
#    file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ThinkinginSystems.epub")
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ThinkinginSystems.epub")

    # Set test_mode to True to process only the first two chapters
    test_mode = True

    chapters_texts = extract_chapters_to_text(file_name, test_mode)
    
    # Create a Word document to save the summaries
    document = Document()

    for chapter_name, chapter_text in chapters_texts.items():
        summarized_text = summarize_text_with_chatgpt(chapter_text)

        # Add chapter name
        document.add_heading(chapter_name, level=1)

        # Add summarized text
        document.add_paragraph("Key Takeaway(s):")
        document.add_paragraph(summarized_text.split('\n')[0])
        
        document.add_paragraph("Recap:")
        document.add_paragraph('\n'.join(summarized_text.split('\n')[1:]))

        # Add a section break (next page)
        document.add_page_break()

    # Save the document
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Summarized_Chapters.docx")
    #output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Summarized_Chapters.docx")
    document.save(output_file)
    print(f"Summarized chapters saved to {output_file}")
