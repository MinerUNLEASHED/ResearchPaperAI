import os
import urllib.parse
import pandas as pd
from DOIDownloader2 import download_pdf  # Make sure this is the correct import

# Path to the CSV file
file_path = 'AllCadimaResearchPapersCSV-V2.csv'
df = pd.read_csv(file_path)

# Create a new column to mark success or failure
download_status = []

# Define the folder where PDFs will be saved
save_folder = "Original Research Papers"
os.makedirs(save_folder, exist_ok=True)

# Helper function to produce the same "safe" filename as in DOIDownloader2
def safe_filename(doi):
    # 1) decode once in case it has %2F, etc.
    decoded = urllib.parse.unquote(str(doi))
    # 2) re-encode to get a consistent safe name
    encoded = urllib.parse.quote(decoded, safe='')
    return f"{encoded}.pdf"

# Loop through the 'DO' column and process each value
for index, raw_doi in enumerate(df['DO'], start=1):
    print(f"Processing Research Paper {index}/{len(df)}")

    # Ensure the value is a valid string
    if not isinstance(raw_doi, str) or pd.isna(raw_doi):
        print(f"Invalid DOI: {raw_doi}")
        download_status.append("N")
        continue

    # Build the final output filename that matches the approach in DOIDownloader2
    output_filename = safe_filename(raw_doi)
    output_filepath = os.path.join(save_folder, output_filename)

    # Check if it already exists
    if os.path.exists(output_filepath):
        print(f"File already exists for DOI '{raw_doi}' -> '{output_filename}', skipping download.")
        download_status.append("Y")  # Mark as downloaded
        continue

    # Try to download
    try:
        success = download_pdf(raw_doi, save_folder=save_folder)
        if success and os.path.exists(output_filepath):
            download_status.append("Y")
        else:
            download_status.append("N")
    except Exception as e:
        print(f"Error downloading DOI {raw_doi}: {e}")
        download_status.append("N")

# Add the new column to the dataframe
df['Download_Status'] = download_status

# Save the updated dataframe to a new CSV file
output_path = 'AllCadimaResearchPapers_Updated.csv'
df.to_csv(output_path, index=False)

print(f"Updated dataset saved to {output_path}")
