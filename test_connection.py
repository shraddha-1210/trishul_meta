"""
Quick test script to verify Neo4j connection and basic setup.
Run this after starting Neo4j to ensure everything is configured correctly.
"""
import os
from dotenv import load_dotenv

print("🔱 TRISHUL Connection Test")
print("=" * 50)

# Test 1: Load environment variables
print("\n1. Testing environment variables...")
load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASS")

if not all([uri, user, password]):
    print("❌ FAILED: Missing environment variables in .env file")
    print(f"   NEO4J_URI: {uri}")
    print(f"   NEO4J_USER: {user}")
    print(f"   NEO4J_PASS: {'***' if password else 'None'}")
    exit(1)
else:
    print(f"✅ Environment variables loaded")
    print(f"   URI: {uri}")
    print(f"   User: {user}")

# Test 2: Import Neo4j driver
print("\n2. Testing Neo4j driver import...")
try:
    from neo4j import GraphDatabase
    print("✅ Neo4j driver imported successfully")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    print("   Run: pip install neo4j")
    exit(1)

# Test 3: Connect to Neo4j
print("\n3. Testing Neo4j connection...")
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Connected to Neo4j successfully")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\n   Troubleshooting:")
    print("   - Is Neo4j running? Check http://localhost:7474")
    print("   - Are credentials correct in .env file?")
    print("   - Is port 7687 accessible?")
    exit(1)

# Test 4: Check if database is seeded
print("\n4. Checking if database is seeded...")
try:
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"✅ Database has {count} nodes")
        else:
            print("⚠️  Database is empty - run: python -m backend.graph_seeder")
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Test 5: Check for checkpoints
print("\n5. Checking for RL agent checkpoints...")
import os.path
red_exists = os.path.exists("checkpoints/red_final.zip")
blue_exists = os.path.exists("checkpoints/blue_final.zip")

if red_exists and blue_exists:
    print("✅ Agent checkpoints found")
else:
    print("⚠️  Checkpoints missing - run: python create_dummy_checkpoints.py")
    print(f"   Red agent: {'✓' if red_exists else '✗'}")
    print(f"   Blue agent: {'✓' if blue_exists else '✗'}")

# Test 6: Test imports
print("\n6. Testing Python dependencies...")
try:
    import fastapi
    import stable_baselines3
    import gymnasium
    import networkx
    import reportlab
    print("✅ All Python dependencies installed")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    print("   Run: pip install -r requirements.txt")
    exit(1)

# Summary
print("\n" + "=" * 50)
print("🎉 All tests passed!")
print("\nNext steps:")
print("1. If database is empty: python -m backend.graph_seeder")
print("2. If checkpoints missing: python create_dummy_checkpoints.py")
print("3. Start backend: start_backend.bat (or .sh)")
print("4. Start frontend: start_frontend.bat (or .sh)")
print("5. Open browser: http://localhost:3000")
print("=" * 50)

driver.close()
