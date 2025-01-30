```markdown
# README - Projet Escape

## Installation des dépendances

- **Installation automatique des dépendances** : Exécutez le script `auto_install_pip.py` pour installer toutes les dépendances requises.
- **En cas d'erreurs** : Si des erreurs non liées aux droits de l'environnement surviennent, relancez le script plusieurs fois.

---

## Services disponibles

### `DatabaseService`
- Gère la connexion à la base de données. Remplissez le fichier `connection_bdd` avec vos informations de connexion.

### `CSVService`
- Service dédié à la gestion des fichiers CSV (lecture, écriture, etc.).

### `CacheService`
- Optimise les performances via la mise en cache des données.

---

## Scripts disponibles

### Création de la base de données
```bash
python -c "from services.database_service import DatabaseService; DatabaseService.create_database()"
```

### Peuplement de la base de données
```bash
python -c "from peuplement import Peuplement; Peuplement.peuplementTotal()"
```

### Traitement des données
```bash
python -c "from traitement import Traitement; Traitement.traitementTotal()"
```

---

## Fichier principal

### `db_create_fill.py`
- Exécute **automatiquement** la création, le peuplement et le traitement de la base de données :
```bash
python db_create_fill.py
```

---

## Tests

- Utilisez `test.py` pour effectuer des tests.
- **Optimisation** : Le `CacheService` réduit les temps d'exécution lors des tests.

---

## Spécificités

### Fichiers SQL
- `escape.sql` : Script SQL original de création de la base de données. **Ne le modifiez pas** sans validation.
- `create_table.sql` : Téléchargé depuis le dépôt Git principal si absent. Utilisez ce fichier pour vos tests SQL.

---

## Serveur Web

### Mise en place
1. Installez les dépendances :
```bash
npm install
```

2. Lancez le serveur :
```bash
node app.js
```

### À venir
- Script `.sh` pour automatiser la mise à jour des dépendances, l'API Python et le serveur Node.

---

## Notes

- **Environnement** : Assurez-vous que les droits d'accès sont correctement configurés.
- **Contributions** : Pour toute modification, créez une branche dédiée et validez par une pull request.
```
