# URL Phishing Checker

## Run locally

Install the Python dependencies and start the API from the project directory:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

In another terminal, start the React app:

```powershell
npm install
npm run dev
```

The API loads `URL_Phishing_model.joblib` from the project directory. During
development, Vite forwards `/api` requests to `http://127.0.0.1:8000`.

The API currently interprets the model's numeric class `1` as phishing and
class `0` as legitimate. Make sure that matches how the model's training labels
were encoded.
