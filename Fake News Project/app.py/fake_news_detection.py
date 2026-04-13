import os
import re
import pickle
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.utils import class_weight

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# =========================
# CONFIG
# =========================
DATASET_PATH = "News_Cleaned.csv"
SAVE_DIR = "saved_models"
os.makedirs(SAVE_DIR, exist_ok=True)

MAX_WORDS = 10000
MAX_LEN = 300

# =========================
# CLEAN TEXT (IMPROVED)
# =========================
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)

    # REMOVE SHORT WORDS (IMPORTANT)
    text = " ".join([w for w in text.split() if len(w) > 2])

    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(DATASET_PATH)

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError("CSV must contain 'text' and 'label' columns")

print("Dataset Loaded")
print("Dataset size:", len(df))

df["text_clean"] = df["text"].apply(clean_text)

X = df["text_clean"]
y = df["label"]

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =========================
# CLASS WEIGHTS (NEW)
# =========================
class_weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))
print("Class Weights:", class_weights)

# =========================
# MODEL 1: LOGISTIC REGRESSION
# =========================
print("\n🔧 Training Logistic Regression...")

tfidf = TfidfVectorizer(
    max_features=50000,
    ngram_range=(1,2),
    stop_words='english'
)

X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

lr_model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced'
)

lr_model.fit(X_train_vec, y_train)

print(f"✅ LR Train Accuracy: {lr_model.score(X_train_vec, y_train):.4f}")
print(f"✅ LR Test Accuracy: {lr_model.score(X_test_vec, y_test):.4f}")

print("\n📊 Classification Report (LR):")
print(classification_report(y_test, lr_model.predict(X_test_vec)))

pickle.dump(lr_model, open(f"{SAVE_DIR}/lr_model.pkl", "wb"))
pickle.dump(tfidf, open(f"{SAVE_DIR}/tfidf.pkl", "wb"))

# =========================
# MODEL 2: LSTM
# =========================
print("\n🔧 Training LSTM...")

tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
tokenizer.fit_on_texts(X_train)

X_train_seq = pad_sequences(tokenizer.texts_to_sequences(X_train), maxlen=MAX_LEN)
X_test_seq = pad_sequences(tokenizer.texts_to_sequences(X_test), maxlen=MAX_LEN)

model = Sequential([
    Embedding(MAX_WORDS, 128, input_length=MAX_LEN),

    Bidirectional(LSTM(64, return_sequences=True)),
    Dropout(0.5),

    Bidirectional(LSTM(32)),
    Dropout(0.5),

    Dense(64, activation="relu"),
    Dropout(0.5),

    Dense(1, activation="sigmoid")
])

model.compile(
    loss="binary_crossentropy",
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0003),
    metrics=["accuracy"]
)

# =========================
# EARLY STOPPING (IMPROVED)
# =========================
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',   # BETTER
    patience=3,
    restore_best_weights=True
)

history = model.fit(
    X_train_seq, y_train,
    validation_split=0.2,
    epochs=10,
    batch_size=16,
    class_weight=class_weights,   # IMPORTANT ADD
    callbacks=[early_stopping],
    verbose=1
)

# =========================
# EVALUATION
# =========================
train_loss, train_acc = model.evaluate(X_train_seq, y_train, verbose=0)
test_loss, test_acc = model.evaluate(X_test_seq, y_test, verbose=0)

print("\n✅ LSTM Results:")
print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

# SAVE
model.save(f"{SAVE_DIR}/lstm_model.keras")
pickle.dump(tokenizer, open(f"{SAVE_DIR}/tokenizer.pkl", "wb"))

print("\n🎉 Models trained & saved successfully!")