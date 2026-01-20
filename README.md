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





Absolutely. Here is the clean, final 4-week plan, aligned with what you already built and how real data platform teams would execute it.

This is not aspirational — it’s realistic, scoped, and credible.

⸻

🗓 4-Week Data Platform Plan (Stripe + Snowflake + dbt)

Week 1 — Core data platform (FOUNDATION)

Goal: Real financial data landing automatically in a cloud warehouse.

What you build
	•	Snowflake setup:
	•	Account, warehouse, database
	•	Schemas: BRONZE, SILVER, GOLD
	•	Service user + role
	•	Stripe ingestion (Python):
	•	Customers
	•	Payment Intents
	•	Charges
	•	Balance Transactions
	•	Payouts
	•	Balance (snapshot)
	•	Bronze tables (append-only, JSON):
	•	BRONZE.STRIPE_CUSTOMERS
	•	BRONZE.STRIPE_PAYMENT_INTENTS
	•	BRONZE.STRIPE_CHARGES
	•	BRONZE.STRIPE_BALANCE_TRANSACTIONS
	•	BRONZE.STRIPE_PAYOUTS
	•	BRONZE.STRIPE_BALANCE
	•	GitHub:
	•	Repo structure
	•	Secrets configured
	•	GitHub Actions scheduled daily ingestion

Outcome

✔ Real Stripe data in Snowflake
✔ Fully automated
✔ Replayable and auditable Bronze layer

Status: ✅ Completed

⸻

Week 2 — Analytics layer with dbt (TRANSFORMATION)

Goal: Turn raw Stripe JSON into clean, queryable business tables.

What you build

Silver (staging models)
	•	stg_stripe_customers
	•	stg_stripe_payment_intents
	•	stg_stripe_charges
	•	stg_stripe_balance_transactions
	•	stg_stripe_payouts
	•	stg_stripe_balance_snapshots

Features:
	•	Deduplication (latest record per ID)
	•	JSON flattening
	•	Type casting
	•	dbt tests (not_null, unique)

Gold (business models)
	•	dim_customers
	•	fct_revenue
	•	fct_cash_flow
	•	fct_fees
	•	fct_refunds

dbt extras
	•	Documentation (dbt docs generate)
	•	Lineage graph
	•	Column descriptions

Outcome

✔ CFO-grade analytics tables
✔ Tested, documented models
✔ Clear lineage from Stripe → metrics

⸻

Week 3 — Orchestration + Streaming (REALISM)

Goal: Make it look like a production data platform.

Orchestration
	•	Add Airflow or Prefect
	•	DAG:

Stripe ingestion
      ↓
   dbt run
      ↓
   dbt test


	•	Backfill capability
	•	Failure visibility

Streaming
	•	Binance WebSocket
	•	Kafka (Docker)
	•	Stream trades into:
	•	BRONZE.CRYPTO_TRADES
	•	Optional dbt model:
	•	stg_crypto_trades

Outcome

✔ Batch + streaming in one platform
✔ Event-driven ingestion
✔ Modern data stack credibility

⸻

Week 4 — Data quality + polish (ENTERPRISE)

Goal: Make the project interview- and production-ready.

Data quality
	•	Great Expectations:
	•	revenue ≥ 0
	•	no null customer IDs
	•	valid currencies
	•	Run checks before dbt models
	•	Fail pipeline on violations

Monitoring
	•	Pipeline success/failure visibility
	•	Row count checks
	•	Schema drift awareness

Documentation
	•	README:
	•	Architecture diagram
	•	Medallion layers
	•	Tech stack explanation
	•	Screenshots:
	•	Snowflake tables
	•	dbt lineage graph
	•	GitHub Actions runs

Outcome

✔ Enterprise-grade data platform
✔ Clear narrative for interviews
✔ Strong portfolio signal

⸻

What this gives you professionally

This single project demonstrates:

✔ Snowflake
✔ Python ELT
✔ dbt
✔ Medallion architecture
✔ CI/CD (GitHub Actions)
✔ Orchestration
✔ Streaming (Kafka)
✔ Data quality
✔ Financial analytics

This is exactly what fintech, Web3, and data platform teams are hiring for in 2026.

⸻

Where you are right now

You have fully completed Week 1
and laid the foundation for Week 2.

The correct next step is:
👉 Create stg_stripe_customers in dbt and run it

When you’re ready, we’ll write that model together and review it like a real PR.