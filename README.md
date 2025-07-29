
---

# 🧾 PDF Heading Extractor

Extract clean, structured outlines from PDF documents using intelligent font, spacing, and pattern-based heading detection — fully containerized via Docker for consistent, offline execution.

### ✅ Fast | 💻 CPU-only | 📂 PDF to JSON | ⚙ Zero setup outside Docker

---

## 🚀 Features

* **Accurate Heading Extraction**:

  * Detects headings based on:

    * Font styles (bold/italic/slanted)
    * Font size hierarchy
    * Vertical spacing and page position
    * Title case and short phrase patterns
  * Filters out:

    * Dates and months (e.g., “March 15, 2022”)
    * Repeated page headers/footers
    * Long content paragraphs

* **Smart Structuring**:

  * Assigns levels like `Title`, `H1`, `H2`, `H3` based on font size frequency
  * Saves results as JSON outlines: `filename.json`

* **Fully Containerized**:

  * Runs in Docker with no Python environment setup required
  * Output and input are handled through a shared `data/` folder

---

## 🧠 Core Techniques & Methodology

> Derived directly from `extract_headings.py` (see source for implementation details)

| Technique                 | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| **Font-Based Heuristics** | Determines body and title size using most common font sizes   |
| **Spacing Analysis**      | Checks vertical gaps above/below text for contextual grouping |
| **Styling Checks**        | Flags headings by presence of bold/italic fonts               |
| **Date & TOC Filtering**  | Excludes date-looking patterns and Table of Contents pages    |
| **Outline Generation**    | Assigns H1–H4 levels based on sorted font size buckets        |
| **Noise Reduction**       | Ignores boilerplate elements repeated across multiple pages   |

---

## 📁 Project Structure

```bash
pdf_heading_extraction/
├── Dockerfile              # Builds the container image
├── requirements.txt        # Python dependencies (PyMuPDF)
├── extract_headings.py     # Main logic for heading extraction
├── data/
│   ├── input.pdf           # 📥 Your input PDF(s)
│   └── input.json          # 📤 JSON output with outline
```

---

## ⚙ How to Run

### 1️⃣ Setup

```bash
# Clone or create your working directory
mkdir pdf_heading_extraction && cd pdf_heading_extraction
# Add the following files: Dockerfile, requirements.txt, extract_headings.py
mkdir data
```

### 2️⃣ Place Your PDFs

Put all PDF files to be processed into the `data/` folder:

```bash
cp your_docs/*.pdf ./data/
```

---

### 3️⃣ Build Docker Image

```bash
docker build -t pdf-heading-extractor .
```

---

### 4️⃣ Run Extraction

#### 🔁 For Linux/macOS:

```bash
docker run --rm -v $(pwd)/data:/app/data pdf-heading-extractor
```

#### 🪟 For Windows PowerShell:

```powershell
docker run --rm -v ${PWD}/data:/app/data pdf-heading-extractor
```

All `.pdf` files will be processed and corresponding `.json` outline files will appear in `./data/`.

---

### 📦 Optional: Save Docker Image

```bash
docker save -o pdf_heading_extractor.tar pdf-heading-extractor
```

Useful for offline transfers or team sharing.

---

## 🧪 Example

Given `sample.pdf` with sections like:

* Introduction
* 1. Background
* 1.1 Objectives
* 2. Methodology

It outputs `sample.json` with:

```json
{
  "title": "Project Report 2025",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H1", "text": "1. Background", "page": 2 },
    { "level": "H2", "text": "1.1 Objectives", "page": 2 },
    { "level": "H1", "text": "2. Methodology", "page": 3 }
  ]
}
```

---

## 🛠 Troubleshooting

| Problem          | Solution                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| Build fails      | Ensure `requirements.txt` and `extract_headings.py` exist. Check line endings (LF preferred).         |
| No output JSON   | Ensure PDFs are **text-based**, not scanned images. Use `fitz.open("file.pdf").get_text()` to verify. |
| Output incorrect | Make sure headings follow standard formatting: bold, short, titled, spaced.                           |

---

## 🧰 Tools Used

* 🐍 **Python 3.9+**
* 📄 **PyMuPDF (fitz)** — Lightweight, fast text extraction
* 🐳 **Docker** — Environment isolation and reproducibility
* 🔍 **Regex & Spacing Heuristics** — Fine-tuned heading rules

---

## 📜 License

This project is MIT-licensed and provided as-is for personal or research use.

---

## 💡 Tip: Run in Colab (Without Docker)

You can also upload PDFs and run `extract_headings.py` in Google Colab using:

```python
!pip install PyMuPDF
```

The rest of the logic remains the same — great for rapid testing.

---


