from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import recommendations, books, authors, series, users, wishliste, reviews

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from starlette.middleware.base import BaseHTTPMiddleware
import time

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
app.include_router(authors.router, prefix="/authors")
app.include_router(series.router, prefix="/series")
app.include_router(reviews.router, prefix="/reviews")
app.include_router(wishliste.router)
app.include_router(users.router)
# Monter le dossier des fichiers statiques (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="../../../frontend/public"), name="static")

@app.get("/")
def home():
    return FileResponse("../../../frontend/public/index.html")

@app.get("/install")
def home():
    return FileResponse("../../../frontend/public/install.html")

@app.get("/favicon.ico")
def home():
    return FileResponse("../../../frontend/public/favicon.ico")

# Dictionnaire pour stocker les IP et leurs timestamps
request_log = {}
blocked_ips = set()

# Paramètres de limitation
RATE_LIMIT = 20000  # Nombre max de requêtes
TIME_WINDOW = 60  # En secondes
BLOCK_DURATION = 60  # Temps de blocage en secondes

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Vérifie si l'IP est bloquée
        if client_ip in blocked_ips:
            return HTTPException(status_code=403, detail="Votre IP est bloquée temporairement.")

        # Met à jour le log des requêtes
        if client_ip not in request_log:
            request_log[client_ip] = []
        
        request_log[client_ip].append(current_time)

        # Supprime les requêtes hors fenêtre de temps
        request_log[client_ip] = [
            t for t in request_log[client_ip] if current_time - t < TIME_WINDOW
        ]

        # Si l'IP dépasse la limite, elle est bloquée
        if len(request_log[client_ip]) > RATE_LIMIT:
            blocked_ips.add(client_ip)
            time.sleep(BLOCK_DURATION)  # Simule un blocage temporaire
            blocked_ips.remove(client_ip)
            return HTTPException(status_code=403, detail="Trop de requêtes. IP bloquée temporairement.")

        return await call_next(request)

# Ajoute le middleware à l'application
app.add_middleware(RateLimitMiddleware)