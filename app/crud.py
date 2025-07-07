from sqlalchemy.orm import Session
from . import models

def save_document(db: Session, filename: str, parsed_data: dict):
    doc = models.Document(filename=filename)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    for page in parsed_data["pages"]:
        db_page = models.DocumentPage(
            page_number=page["page_number"],
            document_id=doc.id
        )
        db.add(db_page)
        db.commit()
        db.refresh(db_page)

        for line in page["lines"]:
            db_line = models.Line(
                content=line["content"],
                page_id=db_page.id
            )
            db.add(db_line)
            db.commit()
            db.refresh(db_line)

            for word in line["words"]:
                db_word = models.Word(
                    text=word,  
                    line_id=db_line.id
                )
                db.add(db_word)

        db.commit()

    return doc
