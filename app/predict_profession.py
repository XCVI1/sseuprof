import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Загрузка данных
df = pd.read_csv('it_professions_dataset_ru.csv')

# Маппинг профессий
profession_labels = {profession: idx for idx, profession in enumerate(df['profession'].unique())}

# Загрузка модели и векторизатора
model = joblib.load('profession_model_ru.pkl')
vectorizer = joblib.load('tfidf_vectorizer_ru.pkl')

def load_model_and_predict(user_description):
    # Преобразование текста в TF-IDF
    user_description_tfidf = vectorizer.transform([user_description]).toarray()
    
    # Печать текста и его вектора
    print(f"User description: {user_description}")
    print(f"User description vector: {user_description_tfidf[0]}")
    
    # Прогнозирование вероятностей
    predicted_proba = model.predict_proba(user_description_tfidf)
    
    # Печать вероятностей
    print(f"Predicted probabilities: {predicted_proba}")
    
    # Получение топ-2 профессий
    top_two_indices = predicted_proba[0].argsort()[-2:][::-1]
    profession_labels_reverse = {idx: profession for profession, idx in profession_labels.items()}
    top_two_professions = [profession_labels_reverse[idx] for idx in top_two_indices]

    return top_two_professions
