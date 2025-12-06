    import duckdb

    # Connect to an in-memory database
    con = duckdb.connect(database=':memory:', read_only=False)

    # Or connect to a persistent file
    # con = duckdb.connect(database='my_database.duckdb', read_only=False)

    # Execute SQL queries
    con.execute("CREATE TABLE my_table (id INTEGER, name VARCHAR);")
    con.execute("INSERT INTO my_table VALUES (1, 'Alice'), (2, 'Bob');")

    # Fetch results
    result = con.execute("SELECT * FROM my_table;").fetchall()
    print(result)

    con.close()