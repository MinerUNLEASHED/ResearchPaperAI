import os
import requests
from bs4 import BeautifulSoup
import subprocess

def download_pdf(doi, save_folder="Original Research Papers"):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_filepath = os.path.join(save_folder, f"{doi.replace('/', '_')}.pdf")

    try:
        print("Trying PyPaperBot...")
        command = [
            "python",
            "-m",
            "PyPaperBot",
            f"--doi={doi}",
            f"--dwn-dir={save_folder}",
            "--use-doi-as-filename"
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        print(f"Downloaded using PyPaperBot: {output_filepath}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyPaperBot failed: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"PyPaperBot encountered an error: {e}")

    try:
        print("Trying direct DOI resolution...")
        url = f"https://doi.org/{doi}"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = None

        for link in soup.find_all('a', href=True):
            if "pdf" in link['href'].lower():
                pdf_link = link['href']
                break

        if not pdf_link:
            print("Could not find a PDF link on the page.")
        else:
            if not pdf_link.startswith("http"):
                pdf_link = requests.compat.urljoin(response.url, pdf_link)

            pdf_response = requests.get(pdf_link)
            pdf_response.raise_for_status()

            with open(output_filepath, "wb") as file:
                file.write(pdf_response.content)

            print(f"Downloaded: {output_filepath}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Direct DOI resolution failed: {e}")

    print(f"Failed to download the paper with DOI {doi} using all methods.")
    return False

# Example usage
# download_pdf("10.48550/arXiv.2203.15556")
