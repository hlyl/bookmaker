import pytest
import os
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

# Set the environment variable before importing the main module
os.environ["OPENAI_API_KEY"] = "mocked_api_key"

from src.main import (
    read_epub_book,
    extract_chapters,
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


def test_read_epub_book(mocker):
    mock_read_epub = mocker.patch("ebooklib.epub.read_epub")
    mock_book = mocker.MagicMock(spec=epub.EpubBook)
    mock_read_epub.return_value = mock_book

    file_name = "test.epub"
    book = read_epub_book(file_name)

    mock_read_epub.assert_called_once_with(file_name)
    assert book == mock_book


def test_extract_chapters(mock_epub_book, mock_epub_chapter):
    mock_epub_book.get_items_of_type.return_value = [mock_epub_chapter]

    chapters = extract_chapters(mock_epub_book)
    mock_epub_book.get_items_of_type.assert_called_once_with(ITEM_DOCUMENT)
    assert chapters == [mock_epub_chapter]


def test_chapter_to_str(mock_epub_chapter):
    result = chapter_to_str(mock_epub_chapter)

    assert result == "This is a paragraph. This is another paragraph."


def test_extract_chapters_to_text(mocker, mock_epub_book, mock_epub_chapter):
    mock_read_epub = mocker.patch(
        "src.main.read_epub_book", return_value=mock_epub_book
    )
    mock_extract_chapters = mocker.patch(
        "src.main.extract_chapters", return_value=[mock_epub_chapter]
    )
    mock_chapter_to_str = mocker.patch(
        "src.main.chapter_to_str",
        return_value="This is a paragraph. This is another paragraph.",
    )

    file_name = "test.epub"
    result = extract_chapters_to_text(file_name)

    mock_read_epub.assert_called_once_with(file_name)
    mock_extract_chapters.assert_called_once_with(mock_epub_book)
    mock_chapter_to_str.assert_called_once_with(mock_epub_chapter)
    assert result == {"Chapter 1": "This is a paragraph. This is another paragraph."}


if __name__ == "__main__":
    pytest.main()
