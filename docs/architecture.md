# Architecture

This project is a local-first financial lakehouse built around Stripe test-mode data.

## Current Flow

```mermaid
flowchart TD
    A["Stripe API"] --> B["Python extraction"]
    B --> C["Bronze Parquet files"]
    C --> D["DuckDB Bronze views"]
    D --> E["dbt Silver models"]
    E --> F["dbt Gold marts"]
    F --> G["SQL analysis in DuckDB or VS Code"]

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef python fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef bronze fill:#ffedd5,stroke:#c2410c,color:#7c2d12
    classDef duckdb fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef gold fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef analysis fill:#e5e7eb,stroke:#4b5563,color:#111827

    class A source
    class B python
    class C bronze
    class D,E duckdb
    class F gold
    class G analysis
```

## Technology Roles

Stripe is the source system. The project reads customers, payment intents, charges, payouts, balance transactions, and balance snapshots from the Stripe API.

Python handles extraction, state management, Bronze row creation, validation, and DuckDB Bronze view creation.

Parquet is the Bronze storage format. Bronze keeps raw API JSON plus audit fields such as `load_id`, `source`, and `extracted_at`.

DuckDB is the local analytical database. It reads Parquet files and stores dbt-created Silver and Gold models.

dbt owns the transformation layer. It converts raw Bronze JSON into typed, deduplicated Silver models and business-ready Gold marts.

Airflow orchestrates the pipeline. It runs the extraction, validation, DuckDB view creation, dbt run, and dbt test steps in order.

Docker runs Airflow in isolated local containers.

## Medallion Layers

Bronze is raw and append-only. It is used for replay, auditability, and schema flexibility.

Silver is clean and deduplicated. It is used for reliable source-level analysis.

Gold is business-ready. It is used for reporting and analytics.

## Future Additions

Snowflake can replace or complement DuckDB as the cloud warehouse.

GitHub Actions can run checks in CI/CD.

Great Expectations or Soda can add stronger data quality checks.

Power BI, Tableau, or Evidence can be added as a BI layer.
