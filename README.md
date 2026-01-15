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






Sure — here is the clean, realistic 4-week plan we defined for your modern data-engineering portfolio.

This assumes:
	•	You already know data engineering
	•	You’re rebuilding momentum after 1.5 years
	•	You want something that looks like a real fintech / Web3 data platform

⸻

🗓 4-Week Modern Data Platform Plan

You are building:

Stripe (SaaS finance) + Crypto (market streaming) → Snowflake → dbt → Orchestration → Data Quality

⸻

Week 1 — Core data platform (Snowflake + Stripe)

Goal: Real transactional data landing in a real warehouse

You build:
	•	Snowflake account
	•	Medallion schemas:

BRONZE
SILVER
GOLD


	•	Stripe ingestion (Python):
	•	Payment Intents
	•	Charges
	•	Balance Transactions
	•	Payouts
	•	Customers
	•	Data lands in:

BRONZE.STRIPE_PAYMENT_INTENTS
BRONZE.STRIPE_CHARGES
BRONZE.STRIPE_BALANCE_TRANSACTIONS
BRONZE.STRIPE_PAYOUTS
BRONZE.STRIPE_CUSTOMERS


	•	GitHub repo with:
	•	ingestion/
	•	dbt/
	•	pipelines/
	•	warehouse/

Outcome

You already have a real fintech data warehouse.

⸻

Week 2 — Analytics layer (dbt)

Goal: Turn raw Stripe data into business metrics

You build:

SILVER (cleaned)
	•	stg_stripe_payment_intents
	•	stg_stripe_charges
	•	stg_stripe_balance_transactions
	•	stg_stripe_payouts
	•	stg_stripe_customers

GOLD (business layer)
	•	fct_revenue
	•	fct_cash_flow
	•	dim_customers
	•	fct_refunds
	•	fct_fees

You add:
	•	dbt tests
	•	documentation
	•	lineage graph

Outcome

You now have a CFO-grade analytics layer.

⸻

Week 3 — Orchestration + Streaming

Goal: Make it look like a real production system

You add:

Orchestration
	•	Airflow or Prefect
	•	DAG:

Stripe API → Snowflake → dbt → data tests



Streaming
	•	Binance WebSocket
	•	Kafka (Docker)
	•	Stream trades into:

BRONZE.CRYPTO_TRADES



Outcome

You now have batch + streaming in one platform.

⸻

Week 4 — Data quality + polish

Goal: Make it enterprise-grade

You add:
	•	Great Expectations:
	•	revenue not null
	•	no negative amounts
	•	valid currencies
	•	Pipeline checks before dbt runs
	•	Monitoring
	•	README with:
	•	architecture diagram
	•	medallion layers
	•	lineage screenshots
	•	DAG screenshots

Outcome

This now looks like the internal data platform of a fintech or Web3 company.

⸻

What this gives you professionally

This project demonstrates:

✔ Snowflake
✔ dbt
✔ ELT
✔ Medallion architecture
✔ Orchestration
✔ Streaming
✔ Data quality
✔ Financial analytics

Which is exactly what:
	•	fintechs
	•	Web3 companies
	•	SaaS
	•	data platform teams

are hiring for in 2026.

⸻

If you want, the next concrete step is:
	•	Finish the Stripe Bronze layer (we already did 3 of the 5 core tables)
	•	Or start the first dbt Silver model

Just tell me which you want to do next.