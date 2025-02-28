import sys
from pathlib import Path

# Ajouter le chemin parent au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from service.DatabaseService import DatabaseService
from service.CSVService import CSVService
from service.EmbeddingService import EmbeddingService
from service.RecommandationService import RecommendationService
from service.RecomandationHybride import RecomandationHybride
from service.decodageFormatage import DecodageFormatage


bddservice = DatabaseService()
csv_service = CSVService()
embservice = EmbeddingService()
bddservice.initialize_connection()
recommendation_service = RecommendationService(bddservice, csv_service, embservice)
recommendation_hybride = RecomandationHybride(bddservice, csv_service, embservice, recommendation_service)
decodeur = DecodageFormatage()
