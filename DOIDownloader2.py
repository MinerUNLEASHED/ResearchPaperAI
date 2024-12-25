import os
import sys
import requests
import subprocess
import urllib.parse
from bs4 import BeautifulSoup

def download_pdf(doi, save_folder="Original Research Papers"):
    """
    Attempt to download a PDF from a DOI using PyPaperBot, and if that fails,
    attempt direct scraping of the DOI landing page for a PDF link.
    Returns True if download succeeded, False otherwise.
    """

    # Make sure the folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Use URL-encoded filename to avoid special character issues on Windows
    safe_doi = urllib.parse.quote(doi, safe='')
    output_filepath = os.path.join(save_folder, f"{safe_doi}.pdf")

    # --- Step 1: Try PyPaperBot ---------------------------------------------
    try:
        print(f"Trying PyPaperBot for DOI: {doi}")

        # Use a temporary download directory so we can rename the file ourselves
        temp_download_dir = os.path.join(save_folder, "_temp")
        if not os.path.exists(temp_download_dir):
            os.makedirs(temp_download_dir)

        command = [
            sys.executable,               # safer than "python" on Windows
            "-m",
            "PyPaperBot",
            f"--doi={doi}",
            f"--dwn-dir={temp_download_dir}",
            # Do NOT use --use-doi-as-filename if you have slashes in the DOI
            # as Windows cannot handle them in filenames.
        ]

        # Run PyPaperBot with a timeout to avoid hanging
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )

        # If we get here, PyPaperBot ran without throwing CalledProcessError
        print("PyPaperBot completed successfully.")

        # Find the file PyPaperBot downloaded in temp_download_dir
        downloaded_file = None
        for fname in os.listdir(temp_download_dir):
            if fname.lower().endswith(".pdf"):
                downloaded_file = os.path.join(temp_download_dir, fname)
                break

        if downloaded_file and os.path.exists(downloaded_file):
            # Rename/move to our final filename
            os.rename(downloaded_file, output_filepath)
            # Clean up the temp folder
            os.rmdir(temp_download_dir)
            print(f"Downloaded using PyPaperBot -> {output_filepath}")
            return True
        else:
            print("PyPaperBot did not produce a PDF file.")
    except subprocess.CalledProcessError as e:
        print("PyPaperBot failed with error code:", e.returncode)
        print("PyPaperBot stderr:", e.stderr.decode().strip())
    except Exception as e:
        print(f"PyPaperBot encountered an error: {e}")

    # --- Step 2: Try direct PDF resolution -----------------------------------
    try:
        print(f"Trying direct DOI resolution for: {doi}")
        url = f"https://doi.org/{doi}"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = None

        # Attempt to find a link with 'pdf' in the href
        for link in soup.find_all('a', href=True):
            if "pdf" in link['href'].lower():
                pdf_link = link['href']
                break

        if not pdf_link:
            print("Could not find a PDF link on the landing page.")
        else:
            # If the link is relative, convert to absolute
            if not pdf_link.startswith("http"):
                pdf_link = requests.compat.urljoin(response.url, pdf_link)

            pdf_response = requests.get(pdf_link)
            pdf_response.raise_for_status()

            with open(output_filepath, "wb") as file:
                file.write(pdf_response.content)

            print(f"Downloaded by direct resolution -> {output_filepath}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Direct DOI resolution failed: {e}")
    except Exception as e:
        print(f"Unexpected error while scraping: {e}")

    print(f"Failed to download the paper with DOI={doi} using all methods.")
    return False
