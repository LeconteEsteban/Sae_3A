from fastapi import FastAPI
from routers import recommendations, books, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
app.include_router(recommendations.router, prefix="/recommandations")
app.include_router(books.router, prefix="/books")
app.include_router(users.router)

# Monter le dossier des fichiers statiques (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="../../../frontend/public"), name="static")

@app.get("/")
def home():
    return FileResponse("../../../frontend/public/index.html")