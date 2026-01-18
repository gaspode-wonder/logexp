# Runtime Filesystem Map (Container View)

/opt/logexp
├── logexp/                     # Core application package
│   ├── __init__.py
│   ├── app/                   # Flask app factory + blueprints
│   ├── models/                # SQLAlchemy models
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic
│   ├── config.py
│   └── ...                    # Other runtime modules
│
├── migrations/                # Alembic migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── <timestamp>_*.py
│
├── alembic.ini                # Alembic configuration
├── gunicorn.conf.py           # Gunicorn runtime config
├── wsgi.py                    # WSGI entrypoint for Gunicorn
│
└── entrypoint.sh              # Container startup script

# Runtime Python Environment Map

/usr/local/lib/python3.10/site-packages
├── logexp -> /opt/logexp/logexp/     # Editable install (pip install -e .)
├── flask/
├── flask_sqlalchemy/
├── alembic/
├── sqlalchemy/
├── psycopg2/
├── gunicorn/
└── <all other dependencies from docker-requirements.txt>

# Runtime Process Map

entrypoint.sh
└── validates env
└── optional migrations (RUN_MIGRATIONS=true)
└── execs Gunicorn

gunicorn
└── loads wsgi:app
    └── imports logexp.app:create_app()
        └── initializes Flask app
        └── initializes SQLAlchemy
        └── loads blueprints
        └── connects to Postgres

# Runtime Network & Ports Map

Container
└── Gunicorn binds to 0.0.0.0:5000
    └── Exposed as port 5000 in Dockerfile
        └── Mapped by docker-compose to host port (varies by config)

# Runtime Environment Variable Map

FLASK_APP=logexp.app:create_app
FLASK_ENV=production
DATABASE_URL=postgresql+psycopg2://...
RUN_MIGRATIONS=true|false
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

