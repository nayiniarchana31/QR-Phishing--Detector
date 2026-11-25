# QR Code Phishing Detector

A web app that scans a QR code image, extracts the URL inside it, and predicts whether that URL is **phishing** or **legitimate** using a Gradient Boosting classifier trained on 20 URL-based features.

**Pipeline:** QR Upload → Decode QR → Extract URL → 20 Features → Gradient Boosting → Prediction

## Features

- Upload a QR code image (PNG, JPG, WEBP) by drag and drop or file browser
- Decodes the QR code with `pyzbar` (falls back to OpenCV if ZBar is unavailable)
- Extracts 20 lexical features from the URL (length, dots, hyphens, `@` signs, IP address, HTTPS, suspicious words, entropy, and more)
- Shows the verdict, confidence, safe/phishing probabilities, and the full 20-feature breakdown
- FastAPI backend with interactive API docs at `/docs`

## Tech Stack

| Part | Technology |
|------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Machine learning | scikit-learn (Gradient Boosting), NumPy, joblib |
| QR decoding | pyzbar, OpenCV, Pillow |
| Frontend | HTML, CSS, JavaScript |

## Folder Structure

```text
QR_Phishing_Detector/
├── backend/
│   ├── main.py                 # FastAPI app and /api/predict endpoint
│   ├── qr_decoder.py           # Decodes QR images to text
│   ├── feature_extractor.py    # Extracts the 20 URL features
│   ├── train_model.py          # Trains and saves the model
│   └── model/
│       └── gb_phishing_model.pkl   # Trained model bundle
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── README.md
```

## Setup and Run (Windows)

1. Install Python 3.10 or newer and open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   If PowerShell blocks the script, run this once and try again:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

3. Install the packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Make sure the trained model exists at `backend/model/gb_phishing_model.pkl`. If it does not, follow **Training the Model** below.
5. Start the backend:

   ```powershell
   cd backend
   uvicorn main:app --reload
   ```

6. Open the app at <http://127.0.0.1:8000/>
   API docs: <http://127.0.0.1:8000/docs>

## Training the Model

The model was trained on the **PhiUSIIL Phishing URL Dataset** from the UCI Machine Learning Repository.

1. Download the dataset from UCI (dataset ID 967) and save the CSV in the `backend` folder as `phishing_site_urls.csv`.
2. Run:

   ```powershell
   cd backend
   python train_model.py
   ```

3. The script samples 60,000 URLs, extracts the 20 features using `feature_extractor.py`, trains a Gradient Boosting classifier (200 estimators), prints a classification report, and saves the model to `backend/model/gb_phishing_model.pkl`.

**Label convention:** class `0` = SAFE and class `1` = PHISHING. The dataset uses the opposite labels (1 = legitimate, 0 = phishing), so `train_model.py` flips them.

**Result:** about 99% accuracy on a held-out 20% test split (12,000 URLs).

## Testing with Sample QR Codes

Create test QR codes locally (nothing is visited, the URL is only stored as text):

```powershell
pip install "qrcode[pil]"
python -c "import qrcode; qrcode.make('https://www.wikipedia.org').save('safe.png')"
python -c "import qrcode; qrcode.make('http://secure-login-verify.paypal-account.xyz/update?id=123').save('phish.png')"
```

| QR content | Result |
|------------|--------|
| `https://www.wikipedia.org` | Legitimate (about 99.8% confidence) |
| `http://secure-login-verify.paypal-account.xyz/update?id=123` | Phishing detected (about 100% confidence) |

## Notes and Limitations

- `pyzbar` may need the native ZBar library on Windows. If it cannot be imported, the decoder falls back to OpenCV.
- The QR code must contain a full `http://` or `https://` URL. QR codes from some online generators contain a short redirect link without the scheme and will be rejected.
- This is a URL-feature classifier. It does not visit the site, so it is **not a guarantee that a site is safe**.
- The very high accuracy reflects patterns in this particular dataset. Performance on real-world URLs is expected to be lower.
- Only the URL text is analysed. Page content, domain age, and SSL certificate details are not checked.

## Possible Improvements

- Add a text box to check a pasted URL directly
- Add more features (domain age, WHOIS, page content)
- Train on a more recent and more varied dataset
- Compare against other models (Random Forest, XGBoost)
