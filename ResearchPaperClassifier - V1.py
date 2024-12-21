import os
import urllib.parse
import pandas as pd
from DOIDownloader2 import download_pdf  # Replace 'your_module' with the actual module name

# Load the CSV file
file_path = 'AllCadimaResearchPapersCSV-V2.csv'  # Update with the correct path
df = pd.read_csv(file_path)

# Creating a new column to mark success or failure
download_status = []

# Define the folder where the PDFs will be saved
save_folder = "Original Research Papers"
os.makedirs(save_folder, exist_ok=True)

# Loop through the "DO" column and process each value
for index, raw_doi in enumerate(df['DO'], start=1):
    print(f"Processing Research Paper {index}/{len(df)}")

    # Ensure the value is a string
    if not isinstance(raw_doi, str):
        print(f"Invalid DOI: {raw_doi}")
        download_status.append("N")
        continue

    # 1. Decode in case we already have encoded pieces like %2F, %25, etc.
    decoded_doi = urllib.parse.unquote(raw_doi)

    # 2. Re-encode to get a consistent filename for checking existence.
    #    The `safe=''` ensures that all special characters like '/' become %2F
    encoded_doi = urllib.parse.quote(decoded_doi, safe='')

    # 3. Create the final filename
    output_filename = f"{encoded_doi}.pdf"
    output_filepath = os.path.join(save_folder, output_filename)

    # 4. Check if it already exists
    if os.path.exists(output_filepath):
        print(f"File already exists for DOI '{raw_doi}' -> '{output_filename}', skipping download.")
        download_status.append("Y")  # Mark as downloaded
        continue

    # 5. Attempt to download if it doesn't exist
    try:
        success = download_pdf(raw_doi, save_folder=save_folder)
        if success:
            # Make sure the downloaded file was saved under the same name
            # If your `download_pdf()` function saves to `output_filepath`, you are good.
            # Otherwise, rename or match the naming inside `download_pdf()`.
            download_status.append("Y")
        else:
            download_status.append("N")
    except Exception as e:
        print(f"Error downloading DOI {raw_doi}: {e}")
        download_status.append("N")

# Add the new column to the dataframe
df['Download_Status'] = download_status

# Save the updated dataframe to a new CSV file
output_path = 'AllCadimaResearchPapers_Updated.csv'  # Update as needed
df.to_csv(output_path, index=False)

print(f"Updated dataset saved to {output_path}")
