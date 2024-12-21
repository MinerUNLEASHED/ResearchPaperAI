import os
import requests
from bs4 import BeautifulSoup

def download_pdf(doi, save_folder="Original Research Papers"):
    """
    Download a research paper PDF given its DOI and save it in the specified folder.

    Args:
        doi (str): DOI identifier of the research paper.
        save_folder (str): Folder to save the downloaded PDF.

    Returns:
        None
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Construct the URL to resolve the DOI
    url = f"https://doi.org/{doi}"

    try:
        # Make a request to resolve the DOI
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        # Parse the final redirected URL (usually the publisher's page)
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = None

        # Look for links to the PDF file (depends on the publisher's website structure)
        for link in soup.find_all('a', href=True):
            if "pdf" in link['href'].lower():
                pdf_link = link['href']
                break

        if not pdf_link:
            print("Could not find a PDF link on the page.")
            return

        # If the PDF link is relative, make it absolute
        if not pdf_link.startswith("http"):
            pdf_link = requests.compat.urljoin(response.url, pdf_link)

        # Download the PDF
        pdf_response = requests.get(pdf_link)
        pdf_response.raise_for_status()

        # Save the PDF to the specified folder
        filename = f"{doi.replace('/', '_')}.pdf"
        filepath = os.path.join(save_folder, filename)

        with open(filepath, "wb") as file:
            file.write(pdf_response.content)

        print(f"Downloaded: {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Example usage
# doi = "10.5080/u25957"  # Replace with the DOI of the research paper
# download_pdf(doi)
