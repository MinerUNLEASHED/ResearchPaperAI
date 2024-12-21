import os
from PyPDF2 import PdfReader
from PyPDF2.generic import NameObject
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF


def save_image(image_data, filters, output_dir, image_count):
    """
    Save image data extracted from PDF.

    Args:
        image_data (bytes): The raw image data from the PDF.
        filters (list or NameObject): The image filters used in the PDF.
        output_dir (str): Directory to save the extracted images.
        image_count (int): The index number of the image to be saved.
    """
    # Ensure filters is a list
    if isinstance(filters, NameObject):
        filters = [filters]

    # Check if the image is JPEG (DCTDecode)
    if filters and "/DCTDecode" in filters:
        # It's basically JPEG data
        image_output_path = os.path.join(output_dir, f"image_{image_count}.jpg")
        try:
            with open(image_output_path, "wb") as f:
                f.write(image_data)
            print(f"Image saved: {image_output_path}")
        except Exception as e:
            print(f"Failed to save JPEG image: {e}")
        return

    # For other filters or if None specified, try using Pillow
    try:
        image = Image.open(BytesIO(image_data))
        # Convert image to RGB if needed
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image_output_path = os.path.join(output_dir, f"image_{image_count}.png")
        image.save(image_output_path, "PNG")
        print(f"Image saved: {image_output_path}")
    except Exception as e:
        print(f"Failed to save image: {e}")


def extract_pdf_content(pdf_path):
    """
    Extract all text and images from a PDF file and save them.
    Uses PyPDF2 for text and PyMuPDF for images.
    """
    # Convert to absolute path
    pdf_path = os.path.abspath(pdf_path)

    # Extract the base name and sanitize it
    raw_base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    safe_base_name = "".join(c for c in raw_base_name if c.isalnum() or c in (" ", "_", "-")).strip()
    if len(safe_base_name) > 50:
        safe_base_name = safe_base_name[:50]

    # Create an output directory
    output_dir = os.path.join(os.path.dirname(pdf_path), safe_base_name)
    os.makedirs(output_dir, exist_ok=True)

    # Define the text output path
    text_output_path = os.path.join(output_dir, f"{safe_base_name}.txt")

    # Open the PDF with PyPDF2 for text
    reader = PdfReader(pdf_path)
    # Open the PDF with fitz (PyMuPDF) for images
    doc = fitz.open(pdf_path)

    image_count = 0

    # Extract text and images
    with open(text_output_path, 'w', encoding='utf-8') as text_file:
        for page_num, page in enumerate(reader.pages, start=1):
            # Extract text from the page
            page_text = page.extract_text() or ""
            text_file.write(f"--- Page {page_num} ---\n")
            text_file.write(page_text)
            text_file.write("\n\n")

            # Extract images using PyMuPDF
            pdf_page = doc.load_page(page_num - 1)
            image_list = pdf_page.get_images(full=True)
            for img_index, img in enumerate(image_list, start=1):
                xref = img[0]
                image_info = doc.extract_image(xref)
                imgdata = image_info["image"]
                # Use the same save function, no filters for PyMuPDF extracted images
                image_count += 1
                save_image(imgdata, None, output_dir, image_count)

    # Print completion message
    print(f"Extraction complete. Text saved at: {text_output_path}")
    print(f"{image_count} images saved in: {output_dir}")


# Example usage
# pdf_path = "Letter to the Editor- Depression As The First Symptom Of Frontal Lobe Grade 2 Malignant Glioma.pdf"
# extract_pdf_content(pdf_path)
