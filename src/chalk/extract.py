import os
import hashlib
import tempfile
from pathlib import Path
import fitz  # pymupdf

def get_cache_dir(pdf_path: str) -> Path:
    pdf_stat = os.stat(pdf_path)
    # Create a unique hash for the specific PDF file and its mtime
    hash_str = f"{pdf_path}{pdf_stat.st_mtime}{pdf_stat.st_size}".encode()
    folder_name = hashlib.md5(hash_str).hexdigest()
    cache_path = Path(tempfile.gettempdir()) / "chalk" / folder_name
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path

def extract_pages(pdf_path: str, max_page: int, max_long_edge: int = 2048):
    """Extracts PDF pages to PNG, caching results on disk."""
    cache_dir = get_cache_dir(pdf_path)
    doc = fitz.open(pdf_path)
    
    extracted = []
    for i in range(min(max_page, len(doc))):
        page_num = i + 1
        output_path = cache_dir / f"page_{page_num}.png"
        
        if not output_path.exists():
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            if max(pix.width, pix.height) > max_long_edge:
                scale = max_long_edge / max(pix.width, pix.height)
                pix = page.get_pixmap(matrix=fitz.Matrix(scale * 2, scale * 2))
            pix.save(str(output_path))
        
        extracted.append(str(output_path))
    return extracted

def _main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: chalk-extract <pdf_path> <max_page>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_page = int(sys.argv[2])
    pages = extract_pages(pdf_path, max_page)
    print("\n".join(pages))

if __name__ == "__main__":
    _main()
