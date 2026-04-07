"""Quick system check before starting TRISHUL"""
import os
import sys
from dotenv import load_dotenv

print("🔱 TRISHUL System Check")
print("=" * 50)

load_dotenv()

# Check 1: Neo4j connection
print("\n1. Checking Neo4j...")
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
    )
    driver.verify_connectivity()
    
    with driver.session() as s:
        count = s.run("MATCH (n) RETURN count(n) as count").single()["count"]
    
    print(f"   ✅ Connected to Neo4j ({count} nodes)")
    
    if count == 0:
        print("   ⚠️  Database is empty")
        print("   Run: python -m backend.graph_seeder")
        sys.exit(1)
    
    driver.close()
except Exception as e:
    print(f"   ❌ Neo4j error: {e}")
    print("\n   Make sure Neo4j is running:")
    print("   - Neo4j Desktop: Start your database")
    print("   - Docker: docker start trishul-neo4j")
    sys.exit(1)

# Check 2: Checkpoints
print("\n2. Checking RL agent checkpoints...")
if os.path.exists("checkpoints/red_final.zip") and os.path.exists("checkpoints/blue_final.zip"):
    print("   ✅ Checkpoints found")
else:
    print("   ⚠️  Checkpoints missing")
    print("   Run: python create_dummy_checkpoints.py")
    sys.exit(1)

# Check 3: Frontend
print("\n3. Checking frontend...")
if os.path.exists("frontend/node_modules"):
    print("   ✅ Frontend dependencies installed")
else:
    print("   ⚠️  Frontend dependencies missing")
    print("   Run: cd frontend && npm install")
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ All checks passed! Ready to start TRISHUL")
print("\nRun: run_all.bat")
print("=" * 50)
