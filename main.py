import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, List


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


if __name__ == "__main__":
    file_name = "ThinkinginSystems.epub"
    chapters_texts = extract_chapters_to_text(file_name)
    for chapter_name, chapter_text in chapters_texts.items():
        print(f"Chapter: {chapter_name}")
        # Print the first 100 characters for brevity
        print(f"Text: {chapter_text[:100]}...")
