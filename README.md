PDF Heading Extractor
This project provides a Python script to extract headings from PDF files and save them as JSON outlines, running in a Docker container for portability. The script uses PyMuPDF to process PDFs and generates a structured outline with titles and headings, saved in a JSON file.
Prerequisites

Docker: Ensure Docker is installed (e.g., Docker Desktop for Windows/Mac or Docker for Linux). Install Docker.
PDF Files: Place the PDF files you want to process in the data folder.

Project Structure
pdf_heading_extraction/
├── Dockerfile
├── requirements.txt
├── extract_headings.py
├── data/
│   ├── input.pdf  (place your PDF files here)
│   ├── output.json (JSON outputs will be saved here)


Dockerfile: Defines the Docker image setup.
requirements.txt: Lists Python dependencies (PyMuPDF).
extract_headings.py: The main script to extract headings from PDFs.
data/: Folder for input PDFs and output JSON files.

Setup Instructions

Clone or Set Up the Project:

Create a folder named pdf_heading_extraction.
Save the following files in this folder:
Dockerfile
requirements.txt
extract_headings.py


Create a data subfolder:mkdir data




Place PDF Files:

Copy the PDF files you want to process into the data folder.


Build the Docker Image:

Open a terminal and navigate to the pdf_heading_extraction folder:cd path/to/pdf_heading_extraction


Build the Docker image:docker build -t pdf-heading-extractor .




Run the Docker Container:

Run the container, mounting the data folder to process PDFs and save JSON outputs:docker run -v $(pwd)/data:/app/data pdf-heading-extractor


On Windows PowerShell, use:docker run -v ${PWD}/data:/app/data pdf-heading-extractor




The script will process all .pdf files in the data folder and save JSON outputs (e.g., input.pdf → input.json) in the same folder.


Save the Docker Image:

Save the built image to a .tar file in the project folder:docker save -o pdf_heading_extractor.tar pdf-heading-extractor


This creates pdf_heading_extractor.tar in the pdf_heading_extraction folder.



Notes

Input/Output: The script reads PDFs from the data folder and saves JSON files with the same base name in the same folder.
Dependencies: The script uses PyMuPDF (version 1.24.10) for PDF processing, installed via requirements.txt.
File Line Endings: On Windows, ensure Dockerfile, requirements.txt, and extract_headings.py use LF (Unix-style) line endings to avoid build errors. Use a text editor like VS Code to convert line endings if needed.
Troubleshooting:
If the build fails, verify that requirements.txt and extract_headings.py exist in the project folder.
Check for hidden file extensions (e.g., requirements.txt.txt) on Windows.
Clear the Docker build cache if issues persist:docker builder prune





Example Usage

Place sample.pdf in the data folder.
Build and run the container as described above.
Check the data folder for sample.json, which contains the extracted title and outline.

License
This project is for personal use and provided as-is. Ensure you have the necessary permissions to process the PDF files used.
