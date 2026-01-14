# finance-data-platform-mds


# GitHub folder structure
data-platform/
├── pyproject.toml
├── README.md
├── docker-compose.yml
├── .env.example
│
├── ingestion/
│   ├── stripe/
│   │   └── extract.py
│   ├── crypto/
│   │   └── stream.py
│   └── common.py
│
├── pipelines/
│   ├── daily_batch.py
│   └── streaming.py
│
├── dbt/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       └── marts/
│
├── warehouse/
│   └── snowflake.sql
│
└── quality/
    └── expectations.yml



Bronze -> isomorphic relationship with source data (source fidelity).

Silver -> unification and standardisation across sources.

Gold -> isomorphic relationship with destination (presentation fidelity).