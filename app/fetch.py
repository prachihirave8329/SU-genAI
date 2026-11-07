
from pathlib import Path
import requests


# Project's raw data folder
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Official PMBI webpages
URLS = {
    "product_list": "https://www.pmbi.co.in/ProductList.aspx",
    "faq": "https://www.pmbi.co.in/FAQ.aspx",
    "about_pmbi": "https://www.pmbi.co.in/aboutbppi.aspx"
}


def download_page(name, url):
    try:
        print(f"Downloading {name}...")

        response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})

        # Check whether the request was successful
        response.raise_for_status()

        # Save the webpage as an HTML file
        file_path = RAW_DIR / f"{name}.html"
        file_path.write_text(
            response.text,
            encoding="utf-8"
        )

        print(f"Saved successfully: {file_path}")

    except requests.exceptions.Timeout:
        print(f"Timeout error while downloading {name}")

    except requests.exceptions.HTTPError as error:
        print(f"HTTP error for {name}: {error}")

    except requests.exceptions.RequestException as error:
        print(f"Request failed for {name}: {error}")

    except OSError as error:
        print(f"File saving error for {name}: {error}")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in URLS.items():
        download_page(name, url)


if __name__ == "__main__":
    main()
