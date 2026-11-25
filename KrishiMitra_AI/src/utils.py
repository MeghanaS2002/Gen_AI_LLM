from io import BytesIO
import re

SUPPORTED_LANGUAGES = {
    "English": "English",
    "ಕನ್ನಡ (Kannada)": "Kannada",
    "हिन्दी (Hindi)": "Hindi",
    "తెలుగు (Telugu)": "Telugu",
    "தமிழ் (Tamil)": "Tamil",
    "मराठी (Marathi)": "Marathi",
}

def split_text(text, max_chars=1100, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def load_documents(filename, content):
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix == "txt":
        text = content.decode("utf-8", errors="ignore")
    elif suffix == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError("PDF extraction failed. Check that it is a readable, text-based PDF.") from exc
    else:
        raise ValueError("Only PDF and TXT files are supported.")
    return [{"title": filename, "text": chunk} for chunk in split_text(text)]
