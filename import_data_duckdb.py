import duckdb
import pandas as pd

# 1. เชื่อม DuckDB (ไฟล์ db หรือ in-memory)
con = duckdb.connect('dads5001.duckdb')  # หรือ ':memory:' สำหรับ in-memory
con.execute("DROP TABLE PIN ")
# 2. อ่าน CSV ด้วย pandas
df = pd.read_csv('tariff_20251207.csv')

# 3. สร้าง table ใน DuckDB จาก DataFrame
con.execute("CREATE TABLE IF NOT EXISTS PIN AS SELECT * FROM df")

# 4. ตรวจสอบข้อมูล
result = con.execute("SELECT * FROM PIN LIMIT 5").fetchdf()
print(result)


