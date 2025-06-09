"""
Extract & clean PDF text to plain text files using OCR (pytesseract + pdf2image).
"""
import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(pdf_path, output_path):
    text = ""
    print(f"[Extract] Processing: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ''
            if not page_text.strip():
                print(f"[Extract] Page {i+1}: No text found, using OCR...")
                images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1, dpi=300)
                for img in images:
                    ocr_text = pytesseract.image_to_string(img)
                    print(f"[Extract] OCR text (first 100 chars): {ocr_text[:100]}")
                    text += ocr_text + "\n"
            else:
                print(f"[Extract] Page {i+1}: Extracted text (first 100 chars): {page_text[:100]}")
                text += page_text + "\n"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"[Extract] Written to: {output_path}\n---")

def batch_extract(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.lower().endswith('.pdf'):
            extract_text_from_pdf(
                os.path.join(input_dir, fname),
                os.path.join(output_dir, fname.replace('.pdf', '.txt'))
            )

if __name__ == "__main__":
    # batch_extract("data/raw_pdfs", "data/extracted_texts")
    pass
