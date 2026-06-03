import os
import oracledb
import pandas as pd
from sqlalchemy import create_engine

print("🚀 Starting Data Sync: Oracle (Gold) -> Postgres (Serving Layer)")

# Safely grab the wallet password from the environment variable we set earlier
wallet_pass = os.environ.get('WALLET_PASSWORD')

# 1. Connect to Oracle using your mTLS Wallet configuration
try:
    oracle_conn = oracledb.connect(
        user="ADMIN",
        password="PortfolioLakehouse_2026!",
        dsn="portfoliodb_medium",
        config_dir="/home/opc/.wallet",
        wallet_location="/home/opc/.wallet",
        wallet_password=wallet_pass  # <--- Dynamically pulled from Linux!
    )
    print("✅ Connected to Oracle ADW")
except Exception as e:
    print(f"❌ Oracle connection failed: {e}")
    exit(1)

# 2. Extract the Gold Layer
print("📥 Extracting GOLD_MACRO_ANALYSIS view...")
query = "SELECT * FROM ADMIN.GOLD_MACRO_ANALYSIS"
df = pd.read_sql(query, con=oracle_conn)
oracle_conn.close()

# 3. Connect to local Postgres Container
pg_engine = create_engine('postgresql://admin:supersecretpassword@localhost:5432/postgres')

# 4. Load data into Postgres
print("📤 Loading data into Postgres Serving Layer...")
df.columns = df.columns.str.lower() 
df.to_sql('gold_macro_analysis', pg_engine, if_exists='replace', index=False)

print("🎉 Sync Complete! The data is now available for Grafana.")
