import os
import sys
import time
from dotenv import load_dotenv
load_dotenv()
try:
	import psycopg2
except ImportError:
	print("ERROR: psycopg2 is not installed. Install requirements first.")
	sys.exit(1)


def build_db_config():
	"""Build DB config from .env values used by Django settings."""
	

	cloud_sql_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME", "").strip()
	host = os.getenv("DB_HOST", "").strip()

	# If Cloud SQL connection name is set and DB_HOST is empty, use Unix socket path.
	if cloud_sql_connection_name and not host:
		host = f"/cloudsql/{cloud_sql_connection_name}"

	return {
		"dbname": os.getenv("DB_NAME", "postgres"),
		"user": os.getenv("DB_USER", "postgres"),
		"password": os.getenv("DB_PASSWORD", ""),
		"host": host or "127.0.0.1",
		"port": int(os.getenv("DB_PORT", "5432")),
		"connect_timeout": 10,
	}


def test_connection():
	config = build_db_config()

	print("Testing database connection with:")
	print(f"  DB_NAME: {config['dbname']}")
	print(f"  DB_USER: {config['user']}")
	print(f"  DB_HOST: {config['host']}")
	print(f"  DB_PORT: {config['port']}")

	try:
		with psycopg2.connect(**config) as conn:
			with conn.cursor() as cur:
				cur.execute("SELECT current_database(), version();")
				db_name, db_version = cur.fetchone()

		print("SUCCESS: Connected to database instance.")
		print(f"  Current DB: {db_name}")
		print(f"  PostgreSQL: {db_version.split(',')[0]}")
		return 0
	except Exception as exc:
		print("ERROR: Database connection failed.")
		print(f"  Details: {exc}")
		return 1


def test_db_speed():
	"""Test database response speed with multiple queries."""
	config = build_db_config()

	print("\n" + "="*60)
	print("DATABASE SPEED TEST")
	print("="*60)

	try:
		with psycopg2.connect(**config) as conn:
			with conn.cursor() as cur:
				# Test 1: Simple SELECT (connection speed)
				print("\n[Test 1] Simple SELECT query (connection + response):")
				start = time.time()
				cur.execute("SELECT 1;")
				result = cur.fetchone()
				elapsed = (time.time() - start) * 1000  # Convert to milliseconds
				print(f"  ✓ Result: {result[0]}")
				print(f"  ⏱ Response Time: {elapsed:.2f}ms")

				# Test 2: Database info query
				print("\n[Test 2] Database info query:")
				start = time.time()
				cur.execute("SELECT datname, pg_database.datistemplate, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datname = current_database();")
				result = cur.fetchone()
				elapsed = (time.time() - start) * 1000
				if result:
					print(f"  ✓ Database: {result[0]} | Size: {result[2]}")
				print(f"  ⏱ Response Time: {elapsed:.2f}ms")

				# Test 3: Table count query
				print("\n[Test 3] Count system tables:")
				start = time.time()
				cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
				result = cur.fetchone()
				elapsed = (time.time() - start) * 1000
				print(f"  ✓ Tables Found: {result[0]}")
				print(f"  ⏱ Response Time: {elapsed:.2f}ms")

				# Test 4: Multiple SELECT operations (latency test)
				print("\n[Test 4] Latency test (10 sequential queries):")
				times = []
				for i in range(10):
					start = time.time()
					cur.execute("SELECT 1;")
					cur.fetchone()
					elapsed = (time.time() - start) * 1000
					times.append(elapsed)
				
				avg_time = sum(times) / len(times)
				min_time = min(times)
				max_time = max(times)
				print(f"  ✓ Average Response: {avg_time:.2f}ms")
				print(f"  ✓ Min Response: {min_time:.2f}ms")
				print(f"  ✓ Max Response: {max_time:.2f}ms")

		print("\n" + "="*60)
		print("✅ DATABASE SPEED TEST COMPLETED")
		print("="*60)
		return 0

	except Exception as exc:
		print(f"\n❌ ERROR: Database speed test failed.")
		print(f"  Details: {exc}")
		return 1


if __name__ == "__main__":
	print("="*60)
	print("DATABASE CONNECTION & SPEED TEST")
	print("="*60 + "\n")
	
	# Test connection first
	connection_result = test_connection()
	
	# If connection successful, run speed test
	if connection_result == 0:
		speed_result = test_db_speed()
		raise SystemExit(speed_result)
	else:
		raise SystemExit(connection_result)
