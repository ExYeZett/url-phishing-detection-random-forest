import os
import re
import gdown
import joblib
import pandas as pd
from urllib.parse import urlparse


# =========================
# MODEL CONFIG
# =========================
MODEL_DIR = "Model"
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")

GOOGLE_DRIVE_FILE_ID = "1HihD4o2LOhbEZU552NjtCupRgDIqY8nL"
GOOGLE_DRIVE_URL = f"https://drive.google.com/file/d/1HihD4o2LOhbEZU552NjtCupRgDIqY8nL/view?usp=sharing"


# =========================
# DOWNLOAD MODEL IF NOT EXISTS
# =========================
os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print("Model file not found. Downloading model from Google Drive...")
    gdown.download(GOOGLE_DRIVE_URL, MODEL_PATH, quiet=False)
    print("Model downloaded successfully.")


# =========================
# LOAD MODEL ARTIFACT
# =========================
artifact = joblib.load(MODEL_PATH)

model = artifact["model"]
feature_columns = artifact["feature_columns"]
threshold = artifact["threshold"]

PHISHING_LABEL = 0
LEGITIMATE_LABEL = 1


# =========================
# FEATURE EXTRACTION
# =========================
def extract_url_features(url: str) -> dict:
    url = str(url).lower()
    parsed = urlparse(url)

    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    url_length = len(url)

    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    special_chars = sum(not c.isalnum() for c in url)

    suspicious_words = [
        "login", "verify", "secure", "account", "update",
        "bank", "paypal", "password", "confirm", "signin"
    ]

    shortener_domains = [
        "bit.ly", "tinyurl.com", "t.co", "goo.gl"
    ]

    return {
        "URLLength": url_length,
        "DomainLength": len(domain),
        "PathLength": len(path),
        "QueryLength": len(query),
        "NoOfSubDomain": domain.count("."),
        "NoOfLetters": letters,
        "NoOfDigits": digits,
        "NoOfSpecialChars": special_chars,
        "LetterRatio": letters / url_length if url_length > 0 else 0,
        "DigitRatio": digits / url_length if url_length > 0 else 0,
        "NoOfDots": url.count("."),
        "NoOfDash": url.count("-"),
        "NoOfSlash": url.count("/"),
        "IsHTTPS": 1 if parsed.scheme == "https" else 0,
        "HasIPAddress": 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain) else 0,
        "HasSuspiciousWord": 1 if any(word in url for word in suspicious_words) else 0,
        "IsShortened": 1 if any(short in domain for short in shortener_domains) else 0
    }


# =========================
# PREDICTION FUNCTION
# =========================
def predict_url(url: str) -> str:
    features = extract_url_features(url)
    input_df = pd.DataFrame([features])
    input_df = input_df[feature_columns]

    proba = model.predict_proba(input_df)[0]
    classes = list(model.classes_)

    phishing_prob = proba[classes.index(PHISHING_LABEL)]

    if phishing_prob >= threshold:
        return "Phishing"

    return "Legitimate"


# =========================
# LOCAL TEST
# =========================
if __name__ == "__main__":
    test_urls = [
        "https://www.google.com/",
        "https://www.telkomuniversity.ac.id/",
        "https://www.roblox.com/home",
        "https://web.whatsapp.com/",
        "http://lpmxp2084.com/",
        "http://secure-login-verification.example.com/login",
        "http://paypal-security-check.example.com"
    ]

    for url in test_urls:
        result = predict_url(url)
        print(f"{url} => {result}")