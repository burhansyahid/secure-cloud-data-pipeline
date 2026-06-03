# 🏛️ Secure Cloud Data Pipeline (Medallion Lakehouse)

```mermaid
graph LR
    classDef external fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef compute fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef docker fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;

    FRED["🏦 FRED API\n(Macro Data)"]:::external

    subgraph OCI["Oracle Cloud Infrastructure (VCN)"]
        
        subgraph Server["Linux Compute Node (Ampere)"]
            Ingest["🐍 Python Ingestion Worker"]:::compute
            DBT["⚙️ dbt (Data Build Tool)"]:::compute
            Sync["🐍 Python Serving Sync"]:::compute
            
            subgraph Container["Docker Environment"]
                Postgres[("🐘 PostgreSQL\n(Serving Layer)")]:::docker
                Grafana["📊 Grafana\n(BI Dashboard)"]:::docker
            end
        end

        subgraph Lakehouse["Oracle Zero-Copy Lakehouse"]
            Lake[("🪣 OCI Object Storage\n(Bronze Layer)")]:::storage
            ADW[("🏛️ Autonomous Data Warehouse\n(Silver & Gold Layer)")]:::storage
        end
    end

    %% Data Flow
    FRED -->|JSON Payload| Ingest
    Ingest -->|Data Lake Stream| Lake
    Lake -.->|DBMS_CLOUD (Zero-Copy)| ADW
    DBT -->|SQL Transformations| ADW
    ADW -->|mTLS Extraction| Sync
    Sync -->|pandas to_sql()| Postgres
    Postgres -->|Port 5432| Grafana
```

## 📌 Executive Summary
This project is an automated, end-to-end Medallion Architecture (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) data pipeline built on **Oracle Cloud Infrastructure (OCI)**. 

It ingests high-frequency macroeconomic data from the Federal Reserve (FRED API), bypasses traditional ETL bottlenecks using a **Zero-Copy Data Lakehouse architecture**, orchestrates relational transformations using **dbt**, and serves the data to a containerized **PostgreSQL** database for real-time visualization in **Grafana**.

---

## 🛠️ Tech Stack & Architecture
* **Infrastructure as Code (IaC):** Terraform
* **Cloud Provider:** Oracle Cloud Infrastructure (OCI)
* **Compute Engine:** OCI Ampere A1 Compute (Oracle Linux 9)
* **Storage / Data Lake:** OCI Object Storage (Bronze Layer)
* **Data Warehouse:** Oracle Autonomous Data Warehouse (Silver & Gold Layers)
* **Orchestration & Transformation:** dbt (Data Build Tool), Advanced SQL
* **Serving Layer:** PostgreSQL (Dockerized)
* **Visualization:** Grafana (Dockerized)
* **Security:** Cryptographic mTLS Wallets, 1-Way TLS, Virtual Cloud Network (VCN) Firewalls

---

## ⚙️ Data Pipeline Architecture 

### 1. The Ingestion Engine (Python)
A secure Python worker operates on a dedicated OCI Linux compute node. It extracts raw, nested JSON payloads containing historical Federal Funds Rates from the FRED API and streams the unstructured data directly into an OCI Object Storage bucket.

### 2. The Bronze Layer (Zero-Copy Architecture)
Instead of writing an expensive ETL script to copy the data row-by-row into the database, this architecture utilizes Oracle's `DBMS_CLOUD` package. The Autonomous Data Warehouse is tethered directly to the Object Storage bucket via an injected OCI Auth Token, allowing the database to query the massive, unparsed JSON string natively without duplicating the storage footprint.

### 3. The Silver Layer (Data Flattening via dbt)
Using `dbt-oracle` secured by a locally managed mTLS wallet, the pipeline orchestrates the Silver Layer. It utilizes Oracle's `JSON_TABLE` functionality to parse the nested JSON arrays on-the-fly, flattening the unstructured string into a strictly typed relational table (`RECORD_DATE`, `INTEREST_RATE`).

### 4. The Gold Layer (Business Analytics via dbt)
The final dbt stage prepares the data for downstream Business Intelligence consumption using advanced SQL Window Functions:
* **Month-over-Month (MoM) Volatility:** `LAG()` functions calculate the exact basis point change between reporting periods.
* **12-Month Rolling Average:** A sliding window frame (`ROWS BETWEEN 11 PRECEDING AND CURRENT ROW`) smooths macroeconomic volatility for long-term trend analysis.

### 5. The Serving Layer & Visualization
To separate analytical compute from BI querying, a Python sync script extracts the Gold layer and loads it into a lightweight, containerized **PostgreSQL** database. **Grafana** connects directly to this Postgres instance to render real-time dashboards.

---

## 🔒 Enterprise Security Implementation
This pipeline bypasses basic username/password authentication in favor of enterprise zero-trust security:
* **Mutual TLS (mTLS):** The dbt orchestration tool and Python sync scripts communicate with the data warehouse using a downloaded cryptographic wallet (`cwallet.sso`), enforcing two-way SSL verification.
* **Secret Management:** No API keys, database passwords, or `.tfstate` files are hardcoded or tracked in Git. All secrets are managed dynamically via OS environment variables.

---

## 📁 Repository Structure
```text
secure-cloud-data-pipeline/
├── infrastructure/            # Terraform IaC for OCI VCN, Object Storage, and ADW
├── ingestion/                 # Python scripts for FRED API extraction to Object Storage
├── lakehouse_core/            # dbt project containing Medallion SQL models (Bronze/Silver/Gold)
├── sync_gold_layer.py         # Python bridge syncing Oracle ADW to Postgres Serving Layer
├── requirements.txt           # Python dependencies
└── README.md                  
```

---

## 🚀 Reproducibility (How to Run Locally)

### Prerequisites
* Oracle Cloud Account (Free Tier eligible)
* FRED API Key
* Docker & Docker Compose installed
* Python 3.9+

### 1. Environment Setup
Clone the repository and install the required dependencies:
```bash
git clone git@github.com:YourUsername/secure-cloud-data-pipeline.git
cd secure-cloud-data-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Secrets
Set your environment variables (do not commit these to version control):
```bash
export FRED_API_KEY="your_api_key"
export TNS_ADMIN="/path/to/your/oracle/wallet"
export WALLET_LOCATION="/path/to/your/oracle/wallet"
export WALLET_PASSWORD="your_wallet_password"
```

### 3. Deploy Infrastructure
Navigate to the `infrastructure/` directory and deploy the OCI resources:
```bash
cd infrastructure
terraform init
terraform apply -auto-approve
cd ..
```

### 4. Run the Pipeline
Execute the ingestion script, dbt models, and the Postgres sync:
```bash
# 1. Ingest Data to Data Lake
python ingestion/ingest_macro.py

# 2. Run dbt Medallion Transformations
cd lakehouse_core
dbt deps
dbt run
cd ..

# 3. Sync Gold Layer to Postgres
python sync_gold_layer.py
```

---
