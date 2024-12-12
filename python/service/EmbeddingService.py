from sentence_transformers import SentenceTransformer, util

class EmbeddingService:
    """
    Service pour gérer l'embedding.
    """

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Service embedding initialized")

    def embeddingWord(self, word):
        """
        Génère un embedding pour un mot.
        
        :param word: Mot à convertir en embedding.
        :return: Vecteur d'embedding.
        """
        if not word or not isinstance(word, str):
            raise ValueError("Le mot doit être une chaîne de caractères non vide.")
        embedding_vector = self.model.encode(word, convert_to_tensor=True)
        print(f"Embedding du mot '{word}': {embedding_vector}")
        return embedding_vector

    def embeddingText(self, text):
        """
        Génère un embedding pour un texte complet.
        
        :param text: Texte à convertir en embedding.
        :return: Vecteur d'embedding.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Le texte doit être une chaîne de caractères non vide.")
        embedding_vector = self.model.encode(text, convert_to_tensor=True)
        print(f"Embedding du texte '{text}': {embedding_vector}")
        return embedding_vector

    def compare(self, text1, text2):
        """
        Compare deux embeddings de texte et calcule la similarité cosine.
        
        :param text1: Premier texte ou embedding.
        :param text2: Deuxième texte ou embedding.
        :return: Score de similarité.
        """
        similarity = util.cos_sim(text1, text2)
        print(f"Similarité: {similarity.item():.4f}")
        return similarity.item()


# Exemple d'utilisation
if __name__ == "__main__":
    service = EmbeddingService()
    t1 = service.embeddingText("coucou j'adore les phrases. je décoche avec mon arc")
    t2 = service.embeddingText("Bonjour j'aime les mots. Je tire des flèches")
    service.compare(t1, t2)
