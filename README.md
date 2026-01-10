# Pastebin-Lite Assignment

# 📁 Project Structure
- pastebin-lite/
├── backend/
│   ├── app/
│   │   └── main.py        # FastAPI backend
│   ├── requirements.txt  # Backend dependencies
│   └── pastes.db         # SQLite database (auto-generated)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   └── main.jsx      # React entry point
│   ├── index.html
│   └── package.json
│
└── README.md

Backend:

- Python FastAPI
- SQLite (SQL persistence)

Frontend:

- React (Vite)

Run Backend:
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

Run Frontend:
cd frontend
npm install
npm run dev

Persistence:

- SQLite database stored on disk

- 🌐 Deployment

This project is optimized for Vercel deployment.
https://frontend-two-snowy-38.vercel.app/







👨‍💻 Author

Virendra Kumar Verma
Full-Stack Developer (Fresher)
Skilled in React, FastAPI, REST APIs, and Database Integration
