from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil, os, uuid
from app import utils, models, database

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = f"./uploads/{filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    data = utils.extract_pdf(filepath)

    doc = models.Document(filename=filename, total_pages=len(data))
    db.add(doc)
    db.commit()
    db.refresh(doc)

    for page_data in data:
        page = models.DocumentPage(
            document_id=doc.id,
            page_number=page_data["page_number"],
            width=page_data["width"],
            height=page_data["height"]
        )
        db.add(page)
        db.commit()
        db.refresh(page)

        for line_data in page_data["lines"]:
            line = models.Line(
                page_id=page.id,
                line_number=line_data["line_number"],
                text=line_data["text"],
                bbox_x0=line_data["bbox"][0],
                bbox_y0=line_data["bbox"][1],
                bbox_x1=line_data["bbox"][2],
                bbox_y1=line_data["bbox"][3]
            )
            db.add(line)
            db.commit()
            db.refresh(line)

            for i, word in enumerate(line_data.get("words", [])):
                word_entry = models.Word(
                    page_id=page.id,
                    word_index=i,
                    text=word["text"],
                    bbox_x0=word["bbox"][0],
                    bbox_y0=word["bbox"][1],
                    bbox_x1=word["bbox"][2],
                    bbox_y1=word["bbox"][3]
                )
                db.add(word_entry)

        for table_data in page_data.get("tables", []):
            table = models.Table(
                page_id=page.id,
                bbox_x0=table_data["bbox"][0],
                bbox_y0=table_data["bbox"][1],
                bbox_x1=table_data["bbox"][2],
                bbox_y1=table_data["bbox"][3]
            )
            db.add(table)
            db.commit()
            db.refresh(table)

            for cell_data in table_data.get("cells", []):
                cell = models.TableCell(
                    table_id=table.id,
                    row=cell_data["row"],
                    col=cell_data["col"],
                    text=cell_data["text"],
                    bbox_x0=cell_data["bbox"][0],
                    bbox_y0=cell_data["bbox"][1],
                    bbox_x1=cell_data["bbox"][2],
                    bbox_y1=cell_data["bbox"][3],
                    is_header=cell_data.get("is_header", 0)  
                )
                db.add(cell)


    db.commit()
    return {"status": "success", "document_id": doc.id}
