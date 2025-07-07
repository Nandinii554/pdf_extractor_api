# 📄 PDF Extraction API

A **FastAPI-based service** to upload PDF files, detect text and tables, extract their content, and save them in a MySQL database in a fully structured format. It uses a combination of **PyMuPDF**, **Tesseract OCR**, and a **Transformer-based Table Detector** to process both scanned and text-based PDFs.

---

## 🚀 Features

- 📤 Upload PDFs via API
- 🔍 Detect scanned vs text-based pages automatically
- 📝 Extract lines and words with their bounding boxes
- 📊 Detect tables using Microsoft’s Table Transformer
- 📦 Extract tables in **tabular format** (rows, columns, headers)
- 🗄️ Store all data in a MySQL database
- 🖥️ Interactive API documentation at `/docs`
- ✅ Supports multi-page PDFs and mixed content

---

## 🛠️ Tech Stack

| Component            | Technology                                |
|----------------------|--------------------------------------------|
| API Framework        | FastAPI                                   |
| Database ORM         | SQLAlchemy                                |
| Database             | MySQL                                     |
| PDF Parsing          | PyMuPDF (fitz)                            |
| OCR (for scanned PDFs) | Tesseract OCR                           |
| Table Detection      | Table Transformer (DETR)                  |
| Image Processing     | Pillow (PIL)                              |
| Language             | Python 3.10+                              |

---

## 📦 Requirements

- Python 3.10+
- MySQL 8.0+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- HuggingFace `microsoft/table-transformer-detection`
- Pip packages (see `requirements.txt`)

---

## 🧪 Example SQL Queries

📌 Get all tables in a document:
SELECT * FROM `table`
WHERE page_id IN (
  SELECT id FROM document_page WHERE document_id = 27
);
![Screenshot 2025-07-01 at 5 46 10 PM](https://github.com/user-attachments/assets/e8ecd744-c0c1-40c2-9e09-7c6f86dffcb3)

📌 Get all words in a page:
SELECT * FROM word WHERE page_id = 27;
![Screenshot 2025-06-30 at 7 20 06 PM](https://github.com/user-attachments/assets/f2404583-52e8-4c2d-b3af-32551a6c5f88)

---

## 📸 Screenshots

- 📂 Upload API (Swagger UI)
![Screenshot I](https://github.com/user-attachments/assets/6ad7385c-75d0-44ee-813c-526a7acb6704)



- 📊 Extracted Table Cells in Database
![Screenshot 2025-07-02 at 12 46 04 PM](https://github.com/user-attachments/assets/6a1df656-8702-45c4-a0e8-4eb71fef0c63)

---

## 📄 Example Table Extraction

| Row | Col | Text  | is_header |
|-----|-----|-------|-----------|
| 0   | 0   | Item  | 1         |
| 0   | 1   | Qty   | 1         |
| 0   | 2   | Price | 1         |
| 1   | 0   | Pen   | 0         |
| 1   | 1   | 2     | 0         |
| 1   | 2   | 10.00 | 0         |

---

## 🔥 Highlights

- Detects and extracts multi-line text and tabular data
- Uses OCR for scanned documents
- Marks header rows (is_header = 1) in tables
- Works with both simple invoices and complex financial reports

---
