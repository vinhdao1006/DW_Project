import duckdb
import time
from datetime import datetime


def benchmark_query(con, query, name="Query"):
    start = time.time()
    result = con.execute(query).fetchall()
    end = time.time()
    print(f"{name} execution time: {end - start:.2f} seconds")
    print(f"Rows returned: {len(result)}")
    return result


# Connect to database
con = duckdb.connect('../data/warehouse.duckdb')

# 1. Original query with date index
query1 = """
SELECT Accident_ID, Start_Lat, Start_Lng, Severity 
FROM accident 
WHERE Start_Time >= '2021-10-05' 
AND Start_Time <= '2022-12-31';
"""

# 2. Optimized query using BETWEEN
query2 = """
SELECT Accident_ID, Start_Lat, Start_Lng, Severity 
FROM accident 
WHERE Start_Time BETWEEN '2021-10-05' AND '2022-12-31';
"""


# 3. Materialized view approach
def create_materialized_view(con):
    con.execute("""
    CREATE MATERIALIZED VIEW IF NOT EXISTS recent_accidents AS
    SELECT Accident_ID, Start_Lat, Start_Lng, Severity, Start_Time
    FROM accident
    WHERE Start_Time >= '2021-10-05' 
    AND Start_Time <= '2022-12-31';
    """)


# 4. Partitioned approach
def create_partitioned_table(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS accident_partitioned AS
    SELECT *
    FROM accident
    ORDER BY Start_Time;
    """)

    # Create index on partitioned table
    con.execute("""
    CREATE INDEX IF NOT EXISTS idx_start_time_part 
    ON accident_partitioned(Start_Time);
    """)


# 5. Query with PRAGMA optimization
query_with_pragma = """
PRAGMA enable_optimizer;
PRAGMA enable_profiling;
SELECT Accident_ID, Start_Lat, Start_Lng, Severity 
FROM accident 
WHERE Start_Time BETWEEN '2021-10-05' AND '2022-12-31';
"""


# 6. Query with memory settings
def optimize_memory_settings(con):
    con.execute("SET memory_limit='4GB'")
    con.execute("SET temp_directory='/path/to/fast/storage'")


# Benchmark different approaches
def run_benchmarks():
    print("Running optimization benchmarks...")

    # Test original query
    print("\n1. Original Query:")
    benchmark_query(con, query1, "Original")

    # Test BETWEEN operator
    print("\n2. Using BETWEEN operator:")
    benchmark_query(con, query2, "BETWEEN")

    # Test materialized view
    print("\n3. Using Materialized View:")
    create_materialized_view(con)
    benchmark_query(con, "SELECT * FROM recent_accidents;", "Materialized View")

    # Test partitioned table
    print("\n4. Using Partitioned Table:")
    create_partitioned_table(con)
    benchmark_query(con, """
    SELECT Accident_ID, Start_Lat, Start_Lng, Severity 
    FROM accident_partitioned 
    WHERE Start_Time BETWEEN '2021-10-05' AND '2022-12-31';
    """, "Partitioned")

    # Test with PRAGMA
    print("\n5. Using PRAGMA optimizations:")
    benchmark_query(con, query_with_pragma, "PRAGMA")

    # Cleanup
    def cleanup():
        try:
            con.execute("DROP MATERIALIZED VIEW IF EXISTS recent_accidents")
            con.execute("DROP TABLE IF EXISTS accident_partitioned")
            con.execute("DROP INDEX IF EXISTS idx_start_time_part")
        except:
            pass


if __name__ == "__main__":
    run_benchmarks()