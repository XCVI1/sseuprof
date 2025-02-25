import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from data.datasets import datasets

keys = list(datasets.keys())
lengths = {key: len(datasets[key]) for key in keys}

print("Длины списков в datasets:")
for key, length in lengths.items():
    print(f"{key}: {length}")

unique_lengths = set(lengths.values())
if len(unique_lengths) > 1:
    print("\nОшибка: В datasets списки разной длины!")
    exit()

df = pd.DataFrame(datasets)
print("\nЗагруженные данные:")
print(df.head())

print("\nПропущенные значения в колонках:")
print(df.isnull().sum())

profession_labels = {profession: idx for idx, profession in enumerate(df['profession'].unique())}
df['profession_label'] = df['profession'].map(profession_labels)

df['combined_text'] = df['description'].fillna('') + ' ' + df['interests'].fillna('')

class_counts = df['profession_label'].value_counts()
rare_classes = class_counts[class_counts < 2].index 

df = df[~df['profession_label'].isin(rare_classes)]

if df.empty:
    print("Ошибка: после удаления редких классов данных не осталось.")
    exit()

print("Данные после удаления редких классов:")
print(df.head())

vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(df['combined_text'])
y = df['profession_label']

test_size = 0.1
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=test_size, random_state=42, stratify=y
    )
except ValueError:
    print("Warning: Недостаточно данных для стратификации. Используется случайное разбиение.")
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=test_size, random_state=42
    )

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, zero_division=0))

joblib.dump(model, 'profession_model_ru.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer_ru.pkl')

print("\nМодель и векторизатор успешно сохранены.")
