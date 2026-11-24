
import re
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def extract_html(file_path):
    """Extract meaningful page content while removing website noise."""

    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    for element in soup([
        "script", "style", "noscript", "header",
        "footer", "nav", "aside", "iframe", "svg"
    ]):
        element.decompose()

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else file_path.stem.replace("_", " ").title()
    )

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="content")
        or soup.find(class_="content")
        or soup.find(id="main-content")
        or soup.body
        or soup
    )

    for element in main_content.select(
        ".breadcrumb, .breadcrumbs, .navbar, .menu, "
        ".sidebar, .navigation, .footer, .header, "
        ".social-links, .pagination"
    ):
        element.decompose()

    content_parts = []

    for element in main_content.find_all(
        ["h1", "h2", "h3", "h4", "p", "li", "td"],
        recursive=True
    ):
        element_text = element.get_text(" ", strip=True)

        if not element_text:
            continue

        if element.name in ["h1", "h2", "h3", "h4"]:
            content_parts.append(f"\n{element_text}\n")
        else:
            content_parts.append(element_text)

    if content_parts:
        text = " ".join(content_parts)
    else:
        text = main_content.get_text(separator=" ", strip=True)

    text = re.sub(r"\s+", " ", text).strip()

    return title, text


def extract_pdf(file_path):
    """Extract text from a PDF, page by page."""

    reader = PdfReader(file_path)
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            continue

        documents.append({
            "source": file_path.name,
            "page": page_number,
            "title": file_path.stem.replace("_", " ").title(),
            "text": text
        })

    return documents


def create_chunks(
    text,
    source,
    page,
    title,
    chunk_size=500,
    overlap=50
):
    """Split text into overlapping chunks using sentence boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_words = []

    for sentence in sentences:
        sentence_words = sentence.split()

        if not sentence_words:
            continue

        if len(sentence_words) > chunk_size:
            if current_words:
                chunks.append(" ".join(current_words))
                current_words = []

            for start in range(
                0,
                len(sentence_words),
                chunk_size - overlap
            ):
                part = sentence_words[start:start + chunk_size]

                if part:
                    chunks.append(" ".join(part))

            continue

        if len(current_words) + len(sentence_words) > chunk_size:
            chunks.append(" ".join(current_words))
            current_words = current_words[-overlap:] if overlap else []

        current_words.extend(sentence_words)

    if current_words:
        chunks.append(" ".join(current_words))

    return [
        {
            "text": chunk,
            "source": source,
            "page": page,
            "title": title
        }
        for chunk in chunks
        if chunk.strip()
    ]


def create_faq_chunks(text, source, page, title):
    """Create one searchable chunk for each numbered FAQ question."""

    question_pattern = re.compile(
        r"(?<!\d)(\d{1,2})\.\s+"
    )

    matches = list(question_pattern.finditer(text))

    if not matches:
        return create_chunks(
            text=text,
            source=source,
            page=page,
            title=title
        )

    chunks = []

    for index, match in enumerate(matches):
        start = match.start()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        question_answer = text[start:end].strip()

        if not question_answer:
            continue

        chunks.append({
            "text": question_answer,
            "source": source,
            "page": page,
            "title": title
        })

    return chunks


def load_documents():
    """Extract text from all available source documents."""

    documents = []

    html_files = [
        "about_pmbi.html",
        "faq.html"
    ]

    for filename in html_files:
        file_path = RAW_DIR / filename

        if file_path.exists():
            title, text = extract_html(file_path)

            if text:
                documents.append({
                    "source": filename,
                    "page": 1,
                    "title": title,
                    "text": text
                })

    pdf_path = RAW_DIR / "product_list.pdf"

    if pdf_path.exists():
        documents.extend(extract_pdf(pdf_path))

    return documents


def chunk_documents(chunk_size=500, overlap=50):
    """Load documents and convert them into searchable chunks."""

    documents = load_documents()
    all_chunks = []

    for document in documents:

        if document["source"] == "faq.html":
            chunks = create_faq_chunks(
                text=document["text"],
                source=document["source"],
                page=document["page"],
                title=document["title"]
            )
        else:
            chunks = create_chunks(
                text=document["text"],
                source=document["source"],
                page=document["page"],
                title=document["title"],
                chunk_size=chunk_size,
                overlap=overlap
            )

        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":

    documents = load_documents()

    print("Total documents:", len(documents))

    for document in documents:
        print(
            f"\nDocument: {document['source']}"
            f"\nTitle: {document['title']}"
            f"\nCharacters: {len(document['text'])}"
            f"\nPreview: {document['text'][:300]}"
        )

    chunks = chunk_documents()

    print("\nTotal chunks:", len(chunks))

    faq_chunks = [
        chunk for chunk in chunks
        if chunk["source"] == "faq.html"
    ]

    print("\nTotal FAQ question chunks:", len(faq_chunks))

    for index, chunk in enumerate(faq_chunks, start=1):
        print(f"\nFAQ Chunk {index}")
        print("Text:", chunk["text"][:500])

    print("\nFirst three overall chunks:")

    for chunk in chunks[:3]:
        print("\n--------------------")
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("Title:", chunk["title"])
        print("Text:", chunk["text"][:300])
