
from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def extract_html(file_path):
    """Extract readable text and title from an HTML file."""

    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Remove unnecessary webpage elements
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    # Extract webpage title
    title = soup.title.get_text(strip=True) if soup.title else file_path.stem

    # Extract readable text
    text = soup.get_text(separator=" ", strip=True)

    return title, text


def extract_pdf(file_path):
    """Extract text from a PDF, page by page."""

    reader = PdfReader(file_path)
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        documents.append({
            "source": file_path.name,
            "page": page_number,
            "title": file_path.stem.replace("_", " ").title(),
            "text": text
        })

    return documents


def create_chunks(text, source, page, title, chunk_size=500, overlap=50):
    """Split text into smaller overlapping chunks."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_text = " ".join(words[start:end])

        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "source": source,
                "page": page,
                "title": title
            })

        start += chunk_size - overlap

    return chunks


def load_documents():
    """Extract text from all available source documents."""

    documents = []

    # Process HTML files
    html_files = [
        "about_pmbi.html",
        "faq.html",
        "product_list.html"
    ]

    for filename in html_files:
        file_path = RAW_DIR / filename

        if file_path.exists():
            title, text = extract_html(file_path)

            documents.append({
                "source": filename,
                "page": 1,
                "title": title,
                "text": text
            })

    # Process PDF file
    pdf_path = RAW_DIR / "product_list.pdf"

    if pdf_path.exists():
        documents.extend(extract_pdf(pdf_path))

    return documents


def chunk_documents():
    """Load documents and split them into chunks."""

    documents = load_documents()
    all_chunks = []

    for document in documents:
        chunks = create_chunks(
            text=document["text"],
            source=document["source"],
            page=document["page"],
            title=document["title"]
        )

        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_documents()

    print("Total chunks:", len(chunks))

    for chunk in chunks[:3]:
        print("\n--------------------")
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("Title:", chunk["title"])
        print("Text:", chunk["text"][:200])
