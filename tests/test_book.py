import pytest
import os
from ebooklib import epub, ITEM_DOCUMENT, ITEM_NAVIGATION
from bs4 import BeautifulSoup

# Set the environment variable before importing the main module
os.environ["OPENAI_API_KEY"] = "mocked_api_key"

from src.main import (
    read_epub_book,
    extract_chapters_from_ncx,
    chapter_to_str,
    extract_chapters_to_text,
)

# Sample data for tests
sample_html_content = """
<html>
    <body>
        <p>This is a paragraph.</p>
        <p>This is another paragraph.</p>
    </body>
</html>
"""

sample_ncx_content = """
<navMap>
    <navPoint>
        <navLabel>
            <text>Chapter 1</text>
        </navLabel>
        <content src="chapter1.xhtml"/>
    </navPoint>
    <navPoint>
        <navLabel>
            <text>Chapter 2</text>
        </navLabel>
        <content src="chapter2.xhtml"/>
    </navPoint>
</navMap>
"""

@pytest.fixture
def mock_epub_book(mocker):
    mock_book = mocker.MagicMock(spec=epub.EpubBook)
    return mock_book

@pytest.fixture
def mock_epub_chapter(mocker):
    mock_chapter = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter.get_body_content.return_value = sample_html_content
    mock_chapter.get_name.return_value = "Chapter 1"
    return mock_chapter

@pytest.fixture
def mock_epub_ncx(mocker):
    mock_ncx = mocker.MagicMock(spec=epub.EpubNav)
    mock_ncx.get_content.return_value = sample_ncx_content
    return mock_ncx

def test_read_epub_book(mocker):
    mock_read_epub = mocker.patch("ebooklib.epub.read_epub")
    mock_book = mocker.MagicMock(spec=epub.EpubBook)
    mock_read_epub.return_value = mock_book

    file_name = "test.epub"
    book = read_epub_book(file_name)

    mock_read_epub.assert_called_once_with(file_name)
    assert book == mock_book

def test_extract_chapters_from_ncx(mock_epub_book, mock_epub_ncx):
    mock_epub_book.get_items.return_value = [mock_epub_ncx]
    mock_epub_ncx.get_type.return_value = ITEM_NAVIGATION

    chapters = extract_chapters_from_ncx(mock_epub_book)
    mock_epub_book.get_items.assert_called_once_with()
    assert chapters == [("Chapter 1", "chapter1.xhtml"), ("Chapter 2", "chapter2.xhtml")]

def test_chapter_to_str(mock_epub_chapter):
    result = chapter_to_str(mock_epub_chapter)

    assert result == "This is a paragraph. This is another paragraph."

def test_extract_chapters_to_text(mocker, mock_epub_book, mock_epub_chapter, mock_epub_ncx):
    mock_read_epub = mocker.patch(
        "src.main.read_epub_book", return_value=mock_epub_book
    )
    mock_extract_chapters_from_ncx = mocker.patch(
        "src.main.extract_chapters_from_ncx", return_value=[("Chapter 1", "chapter1.xhtml")]
    )
    mock_chapter_to_str = mocker.patch(
        "src.main.chapter_to_str",
        return_value="This is a paragraph. This is another paragraph.",
    )
    mock_epub_book.get_item_with_href.return_value = mock_epub_chapter

    file_name = "test.epub"
    result = extract_chapters_to_text(read_epub_book(file_name), test_mode=True)

    mock_read_epub.assert_called_once_with(file_name)
    mock_extract_chapters_from_ncx.assert_called_once_with(mock_epub_book)
    mock_chapter_to_str.assert_called_once_with(mock_epub_chapter)
    assert result == {"Chapter 1": "This is a paragraph. This is another paragraph."}

if __name__ == "__main__":
    pytest.main()
