import streamlit as st
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import warnings
warnings.filterwarnings('ignore')

# ==============================
# LOAD MODELS (CACHE)
# ==============================
@st.cache_resource
def load_models():
    lr_model = pickle.load(open("saved_models/lr_model.pkl", "rb"))
    tfidf = pickle.load(open("saved_models/tfidf.pkl", "rb"))
    tokenizer = pickle.load(open("saved_models/tokenizer.pkl", "rb"))
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    lstm_model = tf.keras.models.load_model("saved_models/lstm_model.keras")
    return lr_model, tfidf, tokenizer, lstm_model

lr_model, tfidf, tokenizer, lstm_model = load_models()

# ==============================
# CLEAN TEXT
# ==============================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ==============================
# PAGE SETTINGS
# ==============================
st.set_page_config(page_title="Fake News Detector", layout="wide", initial_sidebar_state="collapsed")


st.markdown("""
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body, .main {
        background: linear-gradient(135deg, #1e1e2f, #2b2b5f, #1e1e2f);
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #2b2b5f, #1e1e2f);
    }

    .header-section {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .header-section h1 {
        font-size: 2.8em;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .header-section p {
        color: #cbd5e1;
        font-size: 1.1em;
    }

    textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: white !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-size: 1.1em;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
    }

    .footer {
        text-align: center;
        margin-top: 40px;
        color: #9ca3af;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("""
<div class="header-section">
    <h1>Fake News Detection</h1>
    <p>AI-powered analysis using Machine Learning models</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# INPUT
# ==============================
user_input = st.text_area("Enter News Content", height=150)

# ==============================
# BUTTON
# ==============================
if st.button("Analyze News"):
    if user_input.strip() == "":
        st.warning("Please enter some text")
    else:
        clean = clean_text(user_input)

        # Logistic Regression
        vec = tfidf.transform([clean])
        lr_prob = lr_model.predict_proba(vec)[0][1]

        # LSTM
        seq = pad_sequences(tokenizer.texts_to_sequences([clean]), maxlen=300)
        lstm_prob = float(lstm_model.predict(seq, verbose=0)[0][0])

        # ======================
        # LOGIC (UNCHANGED)
        # ======================
        THRESHOLD = 0.4

        lr_is_fake = lr_prob > THRESHOLD
        lstm_is_fake = lstm_prob > THRESHOLD

        final_score = (lr_prob + lstm_prob) / 2
        final_is_fake = final_score > THRESHOLD

        # ======================
        # DISPLAY
        # ======================
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Logistic Regression")
            st.progress(int(lr_prob * 100))
            if lr_is_fake:
                st.error(f"FAKE ({lr_prob*100:.2f}%)")
            else:
                st.success(f"REAL ({(1-lr_prob)*100:.2f}%)")

        with col2:
            st.subheader("LSTM Model")
            st.progress(int(lstm_prob * 100))
            if lstm_is_fake:
                st.error(f"FAKE ({lstm_prob*100:.2f}%)")
            else:
                st.success(f"REAL ({(1-lstm_prob)*100:.2f}%)")

        st.markdown("---")

        # FINAL RESULT
        if final_is_fake:
            st.error(f"FINAL VERDICT: FAKE NEWS ({final_score*100:.2f}%)")
        else:
            st.success(f"FINAL VERDICT: REAL NEWS ({(1-final_score)*100:.2f}%)")

        # AGREEMENT
        if lr_is_fake == lstm_is_fake:
            st.info("Both models agree")
        else:
            st.warning("Models disagree — review manually")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("<div class='footer'>Made by Adarsh</div>", unsafe_allow_html=True)