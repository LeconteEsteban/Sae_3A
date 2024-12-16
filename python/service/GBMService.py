import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

# Exemple de données plus diversifiées
data = {
    'user_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'book_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    'user_age': [25, 35, 45, 20, 30, 40, 22, 28, 33, 50],
    'user_genre_pref': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 1 = préfère fiction, 0 = préfère non-fiction
    'book_genre': [1, 1, 0, 0, 1, 1, 0, 0, 1, 0],  # 1 = fiction, 0 = non-fiction
    'book_rating_avg': [4.5, 4.0, 3.5, 3.0, 4.8, 4.2, 3.9, 3.7, 4.1, 3.8],  # Note moyenne du livre
    'liked': [1, 0, 1, 0, 1, 1, 0, 0, 1, 0]  # 1 = utilisateur a aimé, 0 = utilisateur n'a pas aimé
}

# Charger les données dans un DataFrame
df = pd.DataFrame(data)

# Caractéristiques (features) et cible (target)
X = df[['user_age', 'user_genre_pref', 'book_genre', 'book_rating_avg']]
y = df['liked']

# Diviser les données en ensemble d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Créer un dataset LightGBM
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

# Paramètres du modèle LightGBM
params = {
    'objective': 'binary',       # Classification binaire
    'metric': 'binary_logloss',  # Log loss binaire comme métrique
    'boosting_type': 'gbdt',     # Gradient Boosting Decision Tree
    'learning_rate': 0.1,
    'num_leaves': 31,
    'verbose': -1,
    'is_unbalance': True  # Gérer le déséquilibre des classes
}

# Entraîner le modèle
model = lgb.train(
    params=params,
    train_set=train_data,
    valid_sets=[test_data],
    num_boost_round=100,  # Nombre d'itérations plus élevé
)

# Prédictions
y_pred_prob = model.predict(X_test)

# Calculer AUC et précision
roc_auc = roc_auc_score(y_test, y_pred_prob)
y_pred_binary = (y_pred_prob > 0.5).astype(int)
accuracy = accuracy_score(y_test, y_pred_binary)

print(f"Accuracy: {accuracy:.2f}")
print(f"ROC AUC Score: {roc_auc:.2f}")

# Importance des caractéristiques
importance = model.feature_importance()
feature_names = X.columns
for feature, imp in zip(feature_names, importance):
    print(f"{feature}: {imp}")
