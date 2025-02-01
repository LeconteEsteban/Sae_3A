from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import recommendations, books, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Configuration du middleware CORS
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, prefix="/recommandations")
app.include_router(books.router, prefix="/books")
app.include_router(users.router)

# Monter le dossier des fichiers statiques (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="../../../frontend/public"), name="static")

@app.get("/")
def home():
    return FileResponse("../../../frontend/public/index.html")
