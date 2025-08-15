# CodeReviewer

CodeReviewer is a Flask web application that provides instant AI-powered code reviews, feedback, and suggestions to help users improve their programming skills. It is ideal for students, beginners, and anyone looking to get actionable insights on their code in Python, JavaScript, Java, C/C++, and PHP.

## Features

- **AI Analysis:** Get detailed feedback on code quality, formatting, and best practices using Google Gemini AI.
- **Code Scoring:** Receive a comprehensive score (0-100) based on readability, structure, and best practices.
- **Inline Comments:** AI-generated comments explain your code logic and functionality.
- **Plagiarism Hints:** Detects common patterns and possible plagiarism hints in code submissions.
- **User Dashboard:** Track your code review history, average scores, and languages used.
- **Authentication:** Secure registration, login, and logout for users.
- **History & Filtering:** View and filter your past code submissions by language and score.

## Screenshots

> _Add screenshots of the dashboard, code submission, and feedback pages here._

## Getting Started

### Prerequisites
- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd codereviewer-project
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy or edit `instance/config.py` as needed.
   - Create a `.env` file in the project root or set the following environment variables:
     - `SECRET_KEY` (required)
     - `DATABASE_URL` (optional, defaults to SQLite)
     - `GEMINI_API_KEY` (required for AI features)

   Example `.env`:
   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///app.db
   GEMINI_API_KEY=your-google-gemini-api-key
   ```

5. **Run database migrations:**
   ```bash
   flask db upgrade
   ```

6. **Start the application:**
   ```bash
   python run.py
   ```
   The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage

- Register for a new account or log in.
- Submit code in your preferred language (Python, JavaScript, Java, C/C++, PHP).
- Receive instant AI-powered feedback, score, and inline comments.
- View your submission history and track your progress on the dashboard.

## Project Structure

```
codereviewer project
│
├── app/
│   ├── __init__.py         # App factory and setup
│   ├── models.py           # SQLAlchemy models (User, CodeSubmission)
│   ├── routes/             # Flask blueprints (auth, dashboard, code)
│   ├── templates/          # Jinja2 HTML templates
│   └── utils/              # AI utilities and helpers
│
├── instance/
│   ├── app.db              # SQLite database (default)
│   └── config.py           # Configuration file
│
├── migrations/             # Alembic migrations
├── requirements.txt        # Python dependencies
├── run.py                  # App entry point
└── README.md               # Project documentation
```

## Configuration

All configuration is managed via `instance/config.py` and environment variables. Key settings:
- `SECRET_KEY`: Flask secret key for sessions.
- `SQLALCHEMY_DATABASE_URI` / `DATABASE_URL`: Database connection string.
- `GEMINI_API_KEY`: Google Gemini API key for AI code analysis.

## Dependencies

- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate
- python-dotenv
- psycopg2-binary
- requests
- Werkzeug
- markdown2
- google-generativeai

## License

> _Specify your license here (e.g., MIT, Apache 2.0, etc.)_

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Google Gemini AI](https://ai.google.dev/)
- [markdown2](https://github.com/trentm/python-markdown2)

---

For questions or support, please open an issue or contact the maintainer. 