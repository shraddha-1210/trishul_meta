from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from dotenv import load_dotenv
import asyncio, json, os

load_dotenv()
app = FastAPI(title="TRISHUL API")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"])

# Initialize globals
red_agent = None
blue_agent = None
scorer = None
active_connections = []
driver = None

@app.on_event("startup")
async def startup_event():
    """Initialize connections and load models on startup."""
    global red_agent, blue_agent, scorer, driver
    
    # Connect to Neo4j
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
        )
        driver.verify_connectivity()
        print("✅ Connected to Neo4j")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        driver = None
    
    # Load RL agents
    try:
        from stable_baselines3 import PPO
        red_agent = PPO.load("checkpoints/red_final")
        blue_agent = PPO.load("checkpoints/blue_final")
        print("✅ Loaded trained agents")
    except Exception as e:
        print(f"⚠️  Warning: Could not load agents: {e}")
        print("   Run: python create_dummy_checkpoints.py")
        red_agent = None
        blue_agent = None
    
    # Initialize risk scorer
    try:
        from backend.risk_scorer import RiskScorer
        scorer = RiskScorer()
        print("✅ Risk scorer initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize risk scorer: {e}")
        scorer = None

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    if driver:
        driver.close()
        print("✅ Neo4j connection closed")

@app.get("/api/health")
def health_check():
    """Check if everything is working."""
    try:
        node_count = 0
        if driver:
            with driver.session() as s:
                node_count = s.run("MATCH (n) RETURN count(n) as count").single()["count"]
        
        return {
            "status": "ok",
            "neo4j_connected": driver is not None,
            "node_count": node_count,
            "agents_loaded": red_agent is not None and blue_agent is not None,
            "scorer_loaded": scorer is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/graph")
def get_graph():
    """Return full graph as nodes + edges for Cytoscape."""
    if not driver:
        return {"nodes": [], "edges": [], "error": "Neo4j not connected"}
    
    try:
        with driver.session() as s:
            nodes = s.run("""
                MATCH (n) RETURN 
                    elementId(n) as id, labels(n)[0] as type,
                    n.name as name, n.trust_score as trust,
                    n.anomaly_score as anomaly,
                    n.is_crown_jewel as crown_jewel,
                    n.is_entry_point as entry_point,
                    n.blast_radius as blast_radius
            """).data()

            edges = s.run("""
                MATCH (a)-[r]->(b) RETURN
                    elementId(r) as id, elementId(a) as source, elementId(b) as target,
                    type(r) as type,
                    r.anomaly_score as anomaly,
                    r.is_revoked as revoked,
                    r.is_gated as gated
            """).data()

        return {
            "nodes": [{"data": {**n, "id": str(n["id"])}} for n in nodes],
            "edges": [{"data": {**e, "id": str(e["id"]),
                                "source": str(e["source"]),
                                "target": str(e["target"])}} for e in edges]
        }
    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e)}

@app.get("/api/risk")
def get_risk():
    if not scorer:
        return {"riskiest_edges": [], "attack_paths": [], "error": "Scorer not initialized"}
    
    try:
        edges = scorer.get_riskiest_edges()
        paths = scorer.get_attack_paths()
        return {
            "riskiest_edges": [vars(e) for e in edges],
            "attack_paths": [vars(p) for p in paths]
        }
    except Exception as e:
        return {"riskiest_edges": [], "attack_paths": [], "error": str(e)}

@app.post("/api/simulate")
async def run_simulation():
    """Run one full attack episode and stream results via WebSocket."""
    if red_agent is None or blue_agent is None:
        return {"status": "error", "message": "Agents not loaded. Run: python create_dummy_checkpoints.py"}
    asyncio.create_task(_run_episode())
    return {"status": "simulation started"}

@app.post("/api/seed")
def reseed():
    if not driver:
        return {"status": "error", "message": "Neo4j not connected"}
    
    try:
        from backend.graph_seeder import GraphSeeder
        GraphSeeder().seed()
        return {"status": "graph reseeded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _run_episode():
    """Run red vs blue, push each step to connected WebSocket clients."""
    from backend.env import TrishulEnv
    
    env = TrishulEnv(agent_type="red")
    obs, _ = env.reset()
    done = False
    step = 0

    await _broadcast({"type": "simulation_start",
                      "entry": env.nodes[env.red_position]['name']})

    while not done and step < 50:  # Max 50 steps
        red_action, _ = red_agent.predict(obs, deterministic=False)
        obs, reward, done, _, info = env.step(int(red_action))

        # Blue agent responds
        blue_obs = obs
        blue_action, _ = blue_agent.predict(blue_obs, deterministic=False)
        _, b_reward, _, _, b_info = env.step(int(blue_action))

        step_data = {
            "type": "step",
            "step": step,
            "red_position": env.nodes.get(env.red_position, {}).get('name', ''),
            "red_action": info.get("result", ""),
            "blue_action": b_info.get("result", ""),
            "reward": float(reward),
            "attack_path": [env.nodes.get(n, {}).get('name', '') for n in env.attack_path],
            "compromised_nodes": [nid for nid, n in env.nodes.items() if n['is_compromised']],
            "revoked_edges": [eid for eid, e in env.edges.items() if e['is_revoked']]
        }

        await _broadcast(step_data)
        await asyncio.sleep(0.5)
        step += 1

    result = "crown_jewel_reached" if info.get("result") == "crown_jewel_reached" else "blocked"
    await _broadcast({"type": "simulation_end", "result": result,
                      "path": [env.nodes.get(n, {}).get('name', '') for n in env.attack_path]})

async def _broadcast(message: dict):
    dead = []
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except:
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)