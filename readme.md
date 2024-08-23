# Isidore

An app to store property data and store in a database. Named after Isidore the Farmer, the patron saint of land.

## Project structure

```plaintext
Isidore/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── tasks.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── zillow_service.py
│   │   ├── scrapy_service.py
│   ├── db.py
│   ├── utils.py
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_tasks.py
│   ├── integration/
│   └── conftest.py
├── schedule_tasks.py
├── run.py
├── .env
├── requirements.txt
└── Procfile
```
