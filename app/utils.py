import fitz
import pytesseract
from pytesseract import Output
from PIL import Image
import io
import torch
from transformers import DetrImageProcessor, TableTransformerForObjectDetection

# Load model once
processor = DetrImageProcessor.from_pretrained("microsoft/table-transformer-detection")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-detection")

def is_scanned_page(page):
    return len(page.get_text().strip()) < 10

def extract_tables_with_tatr(page):
    pix = page.get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    width_pdf, height_pdf = page.rect.width, page.rect.height
    width_img, height_img = image.size

    encoding = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**encoding)

    results = processor.post_process_object_detection(
        outputs, threshold=0.5, target_sizes=[image.size[::-1]]
    )[0]

    # Calculate scale factors
    scale_x = width_pdf / width_img
    scale_y = height_pdf / height_img

    tables = []
    for box in results["boxes"]:
        x0, y0, x1, y1 = map(float, box)
        # Scale box to match PDF coordinates
        x0_pdf = x0 * scale_x
        y0_pdf = y0 * scale_y
        x1_pdf = x1 * scale_x
        y1_pdf = y1 * scale_y
        print(f"Detected table bbox: ({x0_pdf}, {y0_pdf}, {x1_pdf}, {y1_pdf})")
        tables.append({"bbox": (x0_pdf, y0_pdf, x1_pdf, y1_pdf)})

    return tables

def group_words_into_cells(words, table_bbox):
    x0, y0, x1, y1 = table_bbox
    margin = 10

    words_in_table = []
    for w in words:
        cx = (w["bbox"][0] + w["bbox"][2]) / 2
        cy = (w["bbox"][1] + w["bbox"][3]) / 2
        if (x0 - margin) <= cx <= (x1 + margin) and (y0 - margin) <= cy <= (y1 + margin):
            words_in_table.append(w)

    if not words_in_table:
        print("No words found inside table bounding box")
        return []

    words_in_table.sort(key=lambda w: (round(w["bbox"][1] / 10) * 10, w["bbox"][0]))

    rows = []
    current_row_y = None
    row = []
    for w in words_in_table:
        wy = w["bbox"][1]
        if current_row_y is None or abs(wy - current_row_y) <= 10:
            row.append(w)
            current_row_y = wy
        else:
            rows.append(row)
            row = [w]
            current_row_y = wy
    if row:
        rows.append(row)

    table_cells = []
    for row_idx, row_words in enumerate(rows):
        row_words.sort(key=lambda w: w["bbox"][0])
        col_idx = 0
        i = 0
        while i < len(row_words):
            # Start of new cell
            cell_words = [row_words[i]]
            x0, y0, x1, y1 = row_words[i]["bbox"]
            i += 1
            # Merge words that are horizontally close (small gap)
            while i < len(row_words):
                prev_x1 = row_words[i-1]["bbox"][2]
                curr_x0 = row_words[i]["bbox"][0]
                if curr_x0 - prev_x1 < 15:  # threshold for word gap
                    cell_words.append(row_words[i])
                    x1 = max(x1, row_words[i]["bbox"][2])
                    y1 = max(y1, row_words[i]["bbox"][3])
                    i += 1
                else:
                    break
            cell_text = " ".join(w["text"] for w in cell_words)
            table_cells.append({
                "row": row_idx,
                "col": col_idx,
                "text": cell_text,
                "bbox": (x0, y0, x1, y1),
                "is_header": 1 if row_idx == 0 else 0
            })
            col_idx += 1

    return table_cells

def extract_pdf(filepath: str):
    doc = fitz.open(filepath)
    results = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        print(f"\nPage {page_number+1} is {'scanned' if is_scanned_page(page) else 'text-based'}")
        width, height = page.rect.width, page.rect.height
        lines = []
        all_words = []

        if is_scanned_page(page):
            pix = page.get_pixmap(dpi=300)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)

            current_line_num = -1
            line_text = ""
            word_list = []
            x0_line = y0_line = x1_line = y1_line = None

            for i in range(len(ocr_data["text"])):
                word = ocr_data["text"][i].strip()
                if not word:
                    continue

                line_num = ocr_data["line_num"][i]
                if line_num != current_line_num and word_list:
                    lines.append({
                        "line_number": current_line_num,
                        "text": line_text.strip(),
                        "bbox": (x0_line, y0_line, x1_line, y1_line),
                        "words": word_list
                    })
                    word_list = []
                    line_text = ""
                    x0_line = y0_line = x1_line = y1_line = None

                current_line_num = line_num
                x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                bbox = (x, y, x + w, y + h)
                word_obj = {"text": word, "bbox": bbox}
                word_list.append(word_obj)
                all_words.append(word_obj)
                line_text += word + " "

                if x0_line is None:
                    x0_line, y0_line, x1_line, y1_line = x, y, x + w, y + h
                else:
                    x0_line = min(x0_line, x)
                    y0_line = min(y0_line, y)
                    x1_line = max(x1_line, x + w)
                    y1_line = max(y1_line, y + h)

            if word_list:
                lines.append({
                    "line_number": current_line_num,
                    "text": line_text.strip(),
                    "bbox": (x0_line, y0_line, x1_line, y1_line),
                    "words": word_list
                })

        else:
            text_blocks = page.get_text("blocks")
            word_boxes = page.get_text("words")

            for i, block in enumerate(text_blocks):
                x0, y0, x1, y1, text, *_ = block
                if not text.strip():
                    continue

                block_words = []
                for w in word_boxes:
                    wx0, wy0, wx1, wy1, wtext, *_ = w
                    if wx0 >= x0 and wy0 >= y0 and wx1 <= x1 and wy1 <= y1:
                        bbox = (wx0, wy0, wx1, wy1)
                        word_obj = {"text": wtext.strip(), "bbox": bbox}
                        block_words.append(word_obj)
                        all_words.append(word_obj)

                lines.append({
                    "line_number": i,
                    "text": text.strip(),
                    "bbox": (x0, y0, x1, y1),
                    "words": block_words
                })

        # Table detection and cell grouping
        table_results = []
        for table in extract_tables_with_tatr(page):
            print(f"\nTable bbox: {table['bbox']}")
            cells = group_words_into_cells(all_words, table["bbox"])
            table_results.append({
                "bbox": table["bbox"],
                "cells": cells
            })

        results.append({
            "page_number": page_number + 1,
            "width": width,
            "height": height,
            "lines": lines,
            "tables": table_results
        })

    return results
