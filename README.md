## ▶️ Running the Application

### Activate Virtual Environment

**Windows**
```bash
venv\Scripts\activate
```

**Linux / Mac**
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI Backend

```bash
uvicorn main:app --reload --port 8075
```

### Start Streamlit Frontend

Open a new terminal and run:

```bash
streamlit run chat_ui.py
```

### Access the Application

```text
http://localhost:8501
```
