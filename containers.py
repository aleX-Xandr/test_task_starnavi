import psycopg
try:
    conn = psycopg.connect(
        dbname="starnavi",
        user="postgres",
        password="k3s5bv0l2d3n8v36b59m",
        host="localhost",
        port="5432"
    )
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")