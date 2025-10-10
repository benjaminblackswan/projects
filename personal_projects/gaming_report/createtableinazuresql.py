import pyodbc
import cv2
from pathlib import Path
import re  # import regex module

server = 'myfirstserverben.database.windows.net'
database = 'Free_Tier_01'
username = ''
password = ''
driver = '{ODBC Driver 17 for SQL Server}'

# Connect to Azure SQL
conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
IF OBJECT_ID('dbo.Playthrough4') IS NULL
BEGIN
CREATE TABLE dbo.Playthrough4 (
        DateStr NVARCHAR(20),
        PlayID NVARCHAR(10),
        Duration DECIMAL(10,3)
        )
END
""")
conn.commit()
