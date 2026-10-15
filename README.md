# Slyce

A full-stack budgeting app that automatically splits your paycheck using the
**50/30/20 rule** (needs / wants / savings), designed to help young people
build better money habits.

🚧 **Status:** In progress

## Features

- **Split engine:** enter a paycheck and get your 50/30/20 breakdown (custom ratios supported)
- **Accounts:** JWT authentication with bcrypt-hashed passwords
- **History:** every paycheck saved per user so you can track splits over time
- **Savings tracker:** shows how much you *should* have saved since any date, with optional interest, compared with what you've actually saved
- **AI tips:** short, personalised tips from an LLM (falls back to built-in tips without a key)
- **Stock explorer:** browse Trading 212 instruments and see price growth over a chosen period with a plain-English summary (education only, not financial advice)
- **Frontend:** lightweight HTML/CSS/JS served by the backend

## Tech stack

| Layer    | Tech                                   |
|----------|----------------------------------------|
| Backend  | Python, FastAPI                        |
| Database | SQLite (SQLAlchemy 2.0)                |
| Auth     | JWT (PyJWT), bcrypt                    |
| AI       | Anthropic API (optional)               |
| Market   | Trading 212 Public API, yfinance       |
| Frontend | HTML, CSS, JavaScript                  |
| Tests    | pytest                                 |

## Project structure

```
slyce/
├── app/
│   ├── main.py            # creates the app, plugs in routers, serves frontend
│   ├── config.py          # settings from .env
│   ├── database.py        # SQLite connection
│   ├── models.py          # tables: User, Paycheck
│   ├── schemas.py         # request/response shapes
│   ├── auth.py            # password hashing + JWT
│   ├── routers/           # the API endpoints
│   │   ├── auth.py        #   /auth/register, /auth/login, /auth/me
│   │   ├── paychecks.py   #   /split, /paychecks
│   │   ├── savings.py     #   /savings/target
│   │   └── stocks.py      #   /stocks/instruments, /stocks/{ticker}/summary
│   └── services/          # the logic (no web code, easy to test)
│       ├── split.py       #   50/30/20 maths
│       ├── savings.py     #   savings-target maths
│       ├── llm.py         #   LLM wrapper
│       ├── tips.py        #   paycheck tips
│       └── stocks.py      #   Trading 212 + price growth
├── frontend/              # index.html, app.js, style.css
├── tests/                 # pytest tests
├── requirements.txt
└── .env.example
```

## Getting started

### Prerequisites
- Python 3.10+

### Setup

```bash
git clone https://github.com/Abdalamohamed7906/Slyce-Personal-Finance.git
cd Slyce-Personal-Finance
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
```

Edit `.env` and set `SECRET_KEY` (see the comment in the file). **Never commit `.env`.**

### Run

```bash
uvicorn app.main:app --reload
```

- App: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

### Test

```bash
pytest
```

## Disclaimer
The stock explorer is for education only and is not financial advice.
Past performance does not predict future returns.
