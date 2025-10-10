import pandas as pd
import pyodbc
from pathlib import Path

# --- Excel file path ---
excel_path = Path(r"C:\Users\benja\OneDrive\Onedrive\Entertainment\Gaming\playthrough log.xlsx")

# --- Read Excel ---
df = pd.read_excel(excel_path, sheet_name=0)  # Reads first sheet
print(f"✅ Excel loaded: {len(df)} rows")

# --- Azure SQL connection ---
server = 'myfirstserverben.database.windows.net'
database = 'Free_Tier_01'
username = 'benjamin_blackswan'
password = ''
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# --- Create table Playlog (if not exists) ---
# Convert all column names to NVARCHAR(255)
columns_sql = ", ".join([f"[{col}] NVARCHAR(255)" for col in df.columns])
create_table_sql = f"""
IF OBJECT_ID(N'dbo.Playlog', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Playlog (
        {columns_sql}
    )
END
"""
cursor.execute(create_table_sql)
conn.commit()
print("✅ Table dbo.Playlog ensured in Azure SQL")

# --- Insert Excel data into SQL ---
cursor.fast_executemany = True  # Enable fast bulk insert
data = df.astype(str).values.tolist()  # Convert all data to string

# Escape column names to handle reserved words or spaces
columns_escaped = [f"[{col}]" for col in df.columns]
placeholders = ", ".join(["?"] * len(df.columns))
insert_sql = f"INSERT INTO dbo.Playlog ({', '.join(columns_escaped)}) VALUES ({placeholders})"

cursor.executemany(insert_sql, data)
conn.commit()

print(f"✅ {len(df)} rows inserted into dbo.Playlog")

# --- Close connection ---
cursor.close()
conn.close()
