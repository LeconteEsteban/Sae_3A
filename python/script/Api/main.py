from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import recommendations, books, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Configuration du middleware CORS pour autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

app.include_router(recommendations.router, prefix="/recommandations")
app.include_router(books.router, prefix="/books")
app.include_router(users.router)

# Monter le dossier des fichiers statiques (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="../../../frontend/public"), name="static")

@app.get("/")
def home():
    return FileResponse("../../../frontend/public/index.html")