import stripe
import json
import uuid
from snowflake import connector
from dotenv import load_dotenv
import os

load_dotenv()

stripe.api_key = os.environ["STRIPE_API_KEY"]

con = connector.connect(
    user=os.environ["STRIPE_PIPELINE_SNOWFLAKE_USER"],
    password=os.environ["STRIPE_PIPELINE_SNOWFLAKE_USER_PASSWORD"],
    account=os.environ["STRIPE_PIPELINE_SNOWFLAKE_ACCOUNT"],
    warehouse=os.environ["STRIPE_PIPELINE_SNOWFLAKE_WAREHOUSE"],
    database=os.environ["STRIPE_PIPELINE_SNOWFLAKE_DATABASE"],
    schema="BRONZE"
)

cur = con.cursor()
cur.execute(f"USE WAREHOUSE {os.environ['STRIPE_PIPELINE_SNOWFLAKE_WAREHOUSE']}")
cur.execute(f"USE DATABASE {os.environ['STRIPE_PIPELINE_SNOWFLAKE_DATABASE']}")
cur.execute("USE SCHEMA BRONZE")

# ------------------------
# Customers
# ------------------------
customers = stripe.Customer.list(limit=100).data
for c in customers:
    cur.execute("""
        INSERT INTO BRONZE.STRIPE_CUSTOMERS
        (CUSTOMER_ID, OBJECT_TYPE, RAW_PAYLOAD)
        SELECT %s, %s, PARSE_JSON(%s)
    """, (c["id"], c["object"], json.dumps(c)))

# ------------------------
# Payment Intents
# ------------------------
payment_intents = stripe.PaymentIntent.list(limit=100).data
for pi in payment_intents:
    cur.execute("""
        INSERT INTO BRONZE.STRIPE_PAYMENT_INTENTS
        (PAYMENT_INTENT_ID, OBJECT_TYPE, RAW_PAYLOAD)
        SELECT %s, %s, PARSE_JSON(%s)
    """, (pi["id"], pi["object"], json.dumps(pi)))

# ------------------------
# Charges
# ------------------------
charges = stripe.Charge.list(limit=100).data
for ch in charges:
    cur.execute("""
        INSERT INTO BRONZE.STRIPE_CHARGES
        (CHARGE_ID, OBJECT_TYPE, RAW_PAYLOAD)
        SELECT %s, %s, PARSE_JSON(%s)
    """, (ch["id"], ch["object"], json.dumps(ch)))

# ------------------------
# Balance Transactions (Ledger)
# ------------------------
balance_txns = stripe.BalanceTransaction.list(limit=100).data
for bt in balance_txns:
    cur.execute("""
        INSERT INTO BRONZE.STRIPE_BALANCE_TRANSACTIONS
        (BALANCE_TRANSACTION_ID, OBJECT_TYPE, RAW_PAYLOAD)
        SELECT %s, %s, PARSE_JSON(%s)
    """, (bt["id"], bt["object"], json.dumps(bt)))

# ------------------------
# Balance
# ------------------------
balance = stripe.Balance.retrieve()
snapshot_id = str(uuid.uuid4())

cur.execute("""
    INSERT INTO BRONZE.STRIPE_BALANCE
    (BALANCE_SNAPSHOT_ID, OBJECT_TYPE, RAW_PAYLOAD)
    SELECT %s, %s, PARSE_JSON(%s)
""", (
    snapshot_id,
    balance["object"],      # "balance"
    json.dumps(balance)
))

# ------------------------
# Payouts
# ------------------------
payouts = stripe.Payout.list(limit=100).data
for p in payouts:
    cur.execute("""
        INSERT INTO BRONZE.STRIPE_PAYOUTS
        (PAYOUT_ID, OBJECT_TYPE, RAW_PAYLOAD)
        SELECT %s, %s, PARSE_JSON(%s)
    """, (p["id"], p["object"], json.dumps(p)))

con.commit()
cur.close()
con.close()