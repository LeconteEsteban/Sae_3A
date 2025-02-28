import chardet

class DecodageFormatage:
    """
    Service intelligent pour détecter et corriger les problèmes d'encodage.
    Compatible avec plusieurs langues et encodages.
    """
    
    def __init__(self):
        # Liste d'encodages à tester si la détection échoue
        self.fallback_encodings = ['latin1', 'windows-1252', 'ISO-8859-1', 'ISO-8859-15']

    def is_text_corrupted(self, text):
        """
        Vérifie si le texte contient des caractères suspects indiquant un problème d'encodage.
        Exemples : "Ø", "Ù", "Ã©", "â€“", "ï»¿"
        """
        corrupted_chars = ["Ø", "Ù", "Ã", "â", "ï", "¿", "�"]  # Caractères fréquents en cas de mauvais encodage
        return any(char in text for char in corrupted_chars)

    def decode(self, text):
        """
        Détecte l'encodage du texte et applique un reformatage si nécessaire.
        """
        try:
            # Détection de l'encodage probable
            detected = chardet.detect(text.encode())
            encoding = detected.get('encoding')

            if encoding:
                # Essai avec l'encodage détecté
                decoded_text = text.encode(encoding, errors='ignore').decode('utf-8', errors='ignore')

                # Vérification si le texte semble encore corrompu
                if not self.is_text_corrupted(decoded_text):
                    return decoded_text

            # Tentative avec d'autres encodages connus
            for fallback in self.fallback_encodings:
                try:
                    decoded_text = text.encode(fallback, errors='ignore').decode('utf-8', errors='ignore')
                    if not self.is_text_corrupted(decoded_text):
                        return decoded_text
                except UnicodeDecodeError:
                    continue  # On essaye l'encodage suivant si ça échoue

            # Dernier recours : remplace les caractères illisibles
            return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')

        except Exception as e:
            print(f"Erreur lors du décodage : {e}")
            return text  # Retourne le texte brut si tout échoue

# Exemple d'utilisation
# decoder = DecodageFormatage()
# bad_text = "Ø¥Ù (Ø¥ÙØ¬ÙØ±) ÙØ¬ÙØ¯ Ø§ÙØ§Ø®ØªØ±Ø§Ù .. (Ø¥ÙØ¬ÙØ±) ..."
# fixed_text = decoder.decode(bad_text)
# print(fixed_text)
# bad_text = "ÙØ¨Ø°Ø© ÙÙÙØ¹ Ø§ÙÙÙÙ ÙØ§ÙÙØ±Ø§Øª: Ø§ÙØ¹ÙÙØ§Ù Ø¹Ø¨Ø§Ø³ ÙØ­ÙÙØ¯ Ø§ÙØ¹ÙØ§Ø¯ .. Ø¥ÙØªÙØ£Øª Ø§ÙÙÙØªØ¨Ø§Øª Ø¨Ø§Ø¨Ø¯Ø§Ø¹Ø§ØªÙ Ø§ÙÙÙØ±ÙØ© ÙÙØ¯ ØºØ²Ø§ Ø§ÙØªØ§Ø±ÙØ® ÙØ§ÙØ´Ø¹Ø± ÙØ§ÙØ£Ø¯Ø¨ ÙØ§ÙØ¯ÙÙ ÙØ§ÙØ³ÙØ§Ø³Ø©.. ÙÙ..."
# fixed_text = decoder.decode(bad_text)
# print(fixed_text)
# bad_text = "Wie wird ein junger Tagedieb, der seine Kindheit in einer HÃ¶hle verbracht hat, zu einem glÃ¼henden Verfechter der Freiheit? Wie wird ein jÃ¼discher BetrÃ¼ger zu einem berÃ¼hmten Arzt? Und wie wird ein junges MÃ¤dchen ohne Perspektive zu einer einflu..."
# fixed_text = decoder.decode(bad_text)
# print(fixed_text)
# bad_text = 'Ø£Ø¨Ø·Ø§Ù ÙØ°Ù Ø§ÙØ±ÙØ§ÙØ© ÙØ²ÙØ¬ ØºØ±ÙØ¨ ÙÙ Ø´Ø®ØµÙØ§Øª ÙØªØ¨Ø§ÙÙØ© Ø§Ø¬ØªÙØ§Ø¹ÙØ§ ÙØ«ÙØ§ÙÙØ§ ÙÙØ§Ø¯ÙØ§ Ø§Ø®ØªØ§Ø±ÙØ§ Ø§ÙÙØ¤ÙÙ Ø¨Ø¹ÙØ§ÙØ© ÙØºØ§Øµ ÙÙ Ø£Ø¹ÙØ§Ù ÙÙ ÙÙÙØ§ Ø ÙØ¬ÙØ¹ÙØ§ ÙÙÙØ§ Ø­Ù Ø§ÙØ²ÙØ§Ù...'
# fixed_text = decoder.decode(bad_text)
# print(fixed_text)
# bad_text = "à´²à´àµà´·à´à´£à´àµà´à´¿à´¨àµ à´®à´²à´¯à´¾à´³à´¿à´à´³àµâ à´à´³àµâà´«à´¿à´²àµâ à´àµà´µà´¿à´àµà´àµà´¨àµà´¨àµ, à´²à´àµà´·à´àµà´à´³àµâ à´àµà´µà´¿à´àµà´àµ à´¤à´¿à´°à´¿à´àµà´àµ à´ªàµà´¯à´¿à´°à´¿à´àµà´àµà´¨àµ..."
# fixed_text = decoder.decode(bad_text)
# print(fixed_text)
