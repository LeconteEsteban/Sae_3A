from fastapi import FastAPI
from routers import recommendations, books

app = FastAPI()
app.include_router(recommendations.router, prefix="/recommandations")
app.include_router(books.router, prefix="/books")