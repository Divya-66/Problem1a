import os
import fitz  # PyMuPDF
import json
import re
from collections import Counter

# Regex patterns for numbered headings
numbering_h1 = re.compile(r'^\d+\.\s|^Appendix [A-Z]\s')
numbering_h2 = re.compile(r'^\d+\.\d+\s')
numbering_h3 = re.compile(r'^\d+\.\d+\.\d+\s')
colon_heading = re.compile(r':\s*$')
keywords = {'Summary', 'Background', 'Introduction', 'References', 'Appendix', 'Table of Contents', 'Acknowledgements', 'Overview'}

# Months and date regex patterns
month_keywords = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"
}
date_patterns = [
    re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),               # e.g., 01/01/2022 or 1-1-22
    re.compile(r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'),                 # e.g., 2023-07-25
    re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b\s+\d{1,2}', re.I),  # e.g., March 15
    re.compile(r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*', re.I),      # e.g., 15 March
]

def count_words(text):
    return len([word for word in text.split() if word.strip(".,:;!?")])

def is_bold_or_italic(span):
    if not span.get("font"):
        return False
    font_name = span["font"].lower()
    return 'bold' in font_name or 'italic' in font_name or 'oblique' in font_name or 'slanted' in font_name

def is_heading_candidate(span, body_size, next_span, i, merged_spans, toc_pages):
    text = span["text"].strip()
    words = text.split()
    font_size = span["size"]
    page_num = span["page"]

    #  Exclude text that looks like a date or month
    lower_text = text.lower()
    if any(month in lower_text for month in month_keywords):
        return False
    if any(p.search(text) for p in date_patterns):
        return False

    if (
        not text or
        len(words) > 10 or
        text.lower().startswith("result:")
    ):
        return False

    # Spacing rules skipped on TOC pages
    above_spacing = True
    right_spacing = True
    below_spacing = True

    if page_num not in toc_pages:
        above_spacing = i > 0 and span["page"] == merged_spans[i-1]["page"] and span["y"] - merged_spans[i-1]["y"] > 20
        if next_span:
            span_right = span["bbox"][2]
            next_right = next_span["bbox"][2]
            right_spacing = abs(span_right - next_right) > 50
            below_spacing = next_span["y"] - span["y"] > 20

    # Rule 1: Larger than body size → heading
    if font_size > body_size:
        return True

    # Rule 2: Same size as body, short, and spaced
    if (
        font_size == body_size and
        is_bold_or_italic(span) and
        len(words) <= 10 and
        next_span and
        next_span["size"] == body_size and
        above_spacing and
        right_spacing and
        below_spacing and
        len(next_span["text"].split()) > 10
    ):
        return True

    # Rule 3: Slanted, short, isolated → heading
    if (
        is_bold_or_italic(span) and
        len(words) <= 10 and
        next_span and
        below_spacing and
        above_spacing
    ):
        return True

    # Rule 4: Smaller than body size, short, spaced
    if (
        font_size < body_size and
        is_bold_or_italic(span) and
        len(words) <= 10 and
        next_span and
        above_spacing and
        right_spacing and
        below_spacing
    ):
        return True

    return False

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    spans = []
    page_texts = []

    for page_num, page in enumerate(doc, start=1):
        text_set = set()
        blocks = page.get_text("dict")["blocks"]
        page_spans = []
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                    text_set.add(text)
                    page_spans.append({
                        "text": text,
                        "size": round(span["size"], 1),
                        "font": span["font"],
                        "y": line["bbox"][1],
                        "bbox": line["bbox"],
                        "page": page_num
                    })
        spans.append(page_spans)
        page_texts.append(text_set)

    # Detect TOC pages
    toc_pages = set()
    for page_num, text_set in enumerate(page_texts, start=1):
        if any("table of contents" in t.lower() for t in text_set):
            toc_pages.add(page_num)

    text_occurrences = Counter()
    for page in page_texts:
        for t in page:
            text_occurrences[t] += 1
    repeated_texts = {text for text, count in text_occurrences.items() if count >= len(doc) * 0.8}

    flat_spans = []
    for page in spans:
        for s in page:
            if s["text"] in repeated_texts and len(s["text"].split()) <= 5:
                continue
            flat_spans.append(s)

    flat_spans.sort(key=lambda s: (s["page"], s["y"]))

    merged_spans = []
    prev = None
    for s in flat_spans:
        if prev and s["page"] == prev["page"] and abs(s["y"] - prev["y"]) < 5 and s["size"] == prev["size"]:
            prev["text"] += " " + s["text"]
        else:
            if prev:
                merged_spans.append(prev)
            prev = s
    if prev:
        merged_spans.append(prev)

    sizes = [s["size"] for s in merged_spans]
    body_size = Counter(sizes).most_common(1)[0][0]

    first_page_sizes = [s["size"] for s in merged_spans if s["page"] == 1]
    title_size = max(first_page_sizes) if first_page_sizes else body_size

    heading_sizes = sorted(set(sizes), reverse=True)
    if title_size in heading_sizes:
        heading_sizes.remove(title_size)
    heading_sizes = [title_size] + heading_sizes

    level_names = ["Title", "H1", "H2", "H3", "H4"]
    level_map = {size: level_names[i] for i, size in enumerate(heading_sizes[:5])}

    title = ""
    outline = []
    last_level = None
    last_size = None

    for i, span in enumerate(merged_spans):
        next_span = merged_spans[i + 1] if i + 1 < len(merged_spans) else None
        text = span["text"].strip()
        span_size = span["size"]
        level = level_map.get(span_size)

        if not title and span["page"] == 1 and (span_size == title_size or count_words(text) > 10):
            title = text
            continue

        if is_heading_candidate(span, body_size, next_span, i, merged_spans, toc_pages):
            if level == "Title" and not title:
                title = text
            else:
                outline.append({
                    "level": level if level and level != "Title" else "H2",
                    "text": text.strip(':').strip(),
                    "page": span["page"]
                })
                last_level = level if level and level != "Title" else "H2"
                last_size = span_size
        elif (
            last_level and
            span_size == last_size and
            len(text.split()) <= 10 and
            i > 0 and
            span["page"] == merged_spans[i-1]["page"] and
            span["y"] - merged_spans[i-1]["y"] > 20
        ):
            lower_text = text.lower()
            if any(month in lower_text for month in month_keywords):
                continue
            if any(p.search(text) for p in date_patterns):
                continue
            outline.append({
                "level": last_level,
                "text": text.strip(':').strip(),
                "page": span["page"]
            })

    return {
        "title": title,
        "outline": outline
    }

input_pdf = "sample.pdf"  # Your PDF file name
pdf_files = [input_pdf]

for pdf_file in pdf_files:
    result = extract_headings(pdf_file)
    json_file = os.path.splitext(pdf_file)[0] + ".json"
    with open(json_file, "w") as f:
        json.dump(result, f, indent=2)

print("✅ All done. JSON file created successfully.")
