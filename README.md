## MART Project – End‑to‑End 

This project shows how to build a  data pipeline end‑to‑end using Python, Spark, MySQL, and AWS S3. It downloads sales CSV files from S3, checks/cleans them, enriches the data with reference tables from MySQL, creates two simple data marts (Customers and Sales Team), writes parquet locally, uploads to S3, writes monthly aggregates back to MySQL, and finally tidies up files.

If you follow this file, you can run the project on your laptop.

### What you’ll get
- Customer data mart and Sales‑team data mart stored locally (parquet) and on S3
- Monthly summary tables written back to MySQL
- A repeatable script you can run when new CSVs arrive in S3

---

## 1) Prerequisites

- **OS**: Windows/Linux/macOS (WSL2 is fine; paths in this README use Linux style)
- **Python**: 3.10.x
- **Java**: JDK 8+ (for Spark)
- **Apache Spark**: Local install
- **MySQL**: Server + a database you can access (e.g., `mart_db`)
- **AWS account**: S3 bucket with folders
- **IDE/Terminal**: PyCharm or VS Code is optional

Install the Python packages listed in `resources/requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r resources/requirements.txt
```

Key packages used: `pyspark`, `boto3`, `mysql-connector-python`, `loguru`, `pycryptodome(x)`.

---

## 2) Project structure (important folders)

```
mart_project/
├── docs/                     
├── resources/
│   ├── config.py                     
│   ├── sql_scripts/
│   │   └── table_scripts.sql         
│   └── requirements.txt
└── src/
    └── main/
        ├── transformations/jobs/main.py   
        ├── read/                          
        ├── write/                         
        ├── upload/                        
        ├── move/                          
        ├── download/                      
        ├── delete/                        
        └── utility/                       
```

---

## 3) One‑time setup

### A) Create MySQL tables and demo data
1. Start MySQL and create a database (example: `mart_db`).
2. Run the SQL in `resources/sql_scripts/table_scripts.sql` against that database.
   - This creates: `customer`, `product`, `store`, `sales_team`, `product_staging_table`, `customers_data_mart`, `sales_team_data_mart`, and a helper `empty_df_create_table`.

### B) Prepare S3 bucket and folders
In your S3 bucket (example: `mart-project-practice-v1`) create folders:
- `sales_data/`              ← put your CSV files here (incoming)
- `sales_data_error/`        ← invalid files move here
- `sales_data_processed/`    ← processed files move here
- `customer_data_mart/`      ← parquet outputs
- `sales_data_mart/`         ← parquet outputs
- `sales_partitioned_data_mart/` (created during run)

CSV format needs these columns at minimum (headers):
`customer_id, store_id, product_name, sales_date, sales_person_id, price, quantity, total_cost`

### C) Local folders for outputs
Make sure these local directories exist (or adjust paths in `resources/config.py`):

```bash
mkdir -p /home/prash/projects/mart_project/mart_project_files/file_from_s3/
mkdir -p /home/prash/projects/mart_project/mart_project_files/error_files/
mkdir -p /home/prash/projects/mart_project/mart_project_files/customer_data_mart/
mkdir -p /home/prash/projects/mart_project/mart_project_files/sales_team_data_mart/
mkdir -p /home/prash/projects/mart_project/mart_project_files/sales_partition_data/
```

### D) Configure credentials and settings
Open `resources/config.py` and set:
- **AWS**: `aws_access_key`, `aws_secret_key`, `bucket_name`
- **S3 folder names**: `s3_source_directory` (incoming), `s3_error_directory`, `s3_processed_directory`, and data mart folders
- **MySQL**: `destination_host`, `destination_port`, `destination_username`, `destination_password`, `destination_database_name`
- **Local paths**: directories shown above

Note: Keys in the repo are placeholders; use your own. Never commit real secrets.

---

## 4) What the pipeline does (in plain words)

1. Looks in S3 `sales_data/` for CSV files.
2. Downloads them to your local `file_from_s3/` folder.
3. Checks each CSV has the required columns. Bad files go to `error_files/` and are moved to `sales_data_error/` in S3.
4. Valid files are combined into one Spark dataframe.
5. Reads reference tables from MySQL (`customer`, `store`, `sales_team`) and joins them to enrich the sales data.
6. Creates two data marts:
   - Customer Data Mart (customer details and total cost per sale)
   - Sales Team Data Mart (sales with month and store, plus partitioned parquet)
7. Writes parquet locally, then uploads the folders to S3.
8. Calculates monthly summaries and writes results to MySQL tables `customers_data_mart` and `sales_team_data_mart`.
9. Moves processed CSVs from `sales_data/` to `sales_data_processed/` in S3 and cleans up local folders.

---

## 5) How to run it

From the project root:

```bash
source .venv/bin/activate                 # if you created a venv
python src/main/transformations/jobs/main.py
```

The script logs progress and will exit on errors (e.g., no files found, missing columns, DB connection issues). On success, it will upload data marts to S3, update MySQL aggregate tables, move processed files, and clean local storage.

---

## 6) Configuration quick reference

All important settings live in `resources/config.py`:
- **S3 bucket name**: `bucket_name`
- **S3 prefixes**: `s3_source_directory`, `s3_error_directory`, `s3_processed_directory`, `s3_customer_datamart_directory`, `s3_sales_datamart_directory`
- **MySQL JDBC (used by Spark)**: `url` and `properties`
- **Local directories**: `local_directory`, `customer_data_mart_local_file`, `sales_team_data_mart_local_file`, `sales_team_data_mart_partitioned_local_file`, `error_folder_path_local`
- **Required CSV columns**: `mandatory_columns`

Database connection helper is in `src/main/utility/my_sql_session.py`.

---

## 7) Troubleshooting

- **No CSV files found**: Put at least one CSV into `s3://<bucket>/sales_data/`.
- **Missing columns**: Make sure your CSV header contains all columns listed in `mandatory_columns`.
- **MySQL connection fails**: Check host/port/user/password in `resources/config.py`. Ensure MySQL is running and your user has access to `mart_db`.
- **Spark errors**: Verify Java is installed and Spark is set up; match Python 3.10 with your Spark/py4j versions.
- **S3 permissions**: The AWS user/key must allow `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, `s3:CopyObject` on your bucket.
- **Paths on Windows**: If using WSL, use Linux paths inside WSL as shown above. If running native Windows, update paths in `resources/config.py` accordingly.

---

## 8) Safe practices (recommended)

- Store secrets in environment variables or a vault; avoid committing real keys.
- Keep `requirements.txt` pinned and use a virtual environment.
- Do a dry run with a tiny CSV first.
- Monitor `product_staging_table.status` (`A`/`I`) to detect incomplete runs.

---

## 9) Run flow in one picture (text version)

S3 sales_data → Download → Validate → Join with MySQL dims → Build data marts → Write parquet locally → Upload to S3 → Write monthly aggregates to MySQL → Move processed files on S3 → Cleanup local

---

## 10) Useful files to read

- `resources/sql_scripts/table_scripts.sql` – create and seed MySQL tables
- `src/main/transformations/jobs/main.py` – the full pipeline logic
- `resources/config.py` – all configuration and paths

---

## 11) License

For learning/demo purposes. Replace credentials with your own and follow your organization’s security policies.


