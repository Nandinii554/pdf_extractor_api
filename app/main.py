from fastapi import FastAPI
from app.routes import pdf
from app.database import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(pdf.router, prefix="/pdf", tags=["PDF Upload"])
