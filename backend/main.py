from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from neo4j import GraphDatabase
from dotenv import load_dotenv
import asyncio, json, os, csv, io
from datetime import datetime

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
    
    # Initialize database
    try:
        from backend.database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database init warning: {e}")
    
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
    from backend.database import save_simulation
    import time
    
    start_time = time.time()
    env = TrishulEnv(agent_type="red")
    obs, _ = env.reset()
    done = False
    step = 0
    
    entry_name = env.nodes[env.red_position]['name']
    target_reached = None

    await _broadcast({"type": "simulation_start",
                      "entry": entry_name})

    while not done and step < 100:  # Increased for complex paths
        red_action, _ = red_agent.predict(obs, deterministic=False)
        obs, reward, done, _, info = env.step(int(red_action))

        # Blue agent responds
        blue_obs = obs
        blue_action, _ = blue_agent.predict(blue_obs, deterministic=False)
        _, b_reward, _, _, b_info = env.step(int(blue_action))

        # Get current node info
        current_node = env.nodes.get(env.red_position, {})
        node_name = current_node.get('name', 'Unknown')
        node_type = current_node.get('label', 'Unknown')
        is_crown = current_node.get('is_crown_jewel', False)
        
        # Format red action
        red_result = info.get("result", "")
        red_action_text = ""
        if "moved" in red_result:
            red_action_text = f"🔴 Moved to {node_name} ({node_type})"
        elif "blocked" in red_result:
            red_action_text = f"🚫 Blocked by {red_result.replace('blocked_', '')}"
        elif "persisted" in red_result:
            red_action_text = f"🔴 Established persistence at {node_name}"
        elif "exfil" in red_result:
            red_action_text = f"🔴 Attempted data exfiltration from {node_name}"
        elif "crown_jewel_reached" in red_result:
            red_action_text = f"🎯 BREACHED CROWN JEWEL: {node_name}!"
        else:
            red_action_text = f"🔴 {red_result}"
        
        # Format blue action
        blue_result = b_info.get("result", "")
        blue_action_text = ""
        if "blocked_hot_path" in blue_result:
            blue_action_text = f"🔵 Revoked critical edge on attack path"
        elif "false_revoke" in blue_result:
            blue_action_text = f"🔵 Revoked edge (not on attack path)"
        elif "mfa_added" in blue_result:
            blue_action_text = f"🔵 Added MFA protection"
        elif "noop" in blue_result:
            blue_action_text = f"🔵 Monitoring..."
        else:
            blue_action_text = f"🔵 {blue_result}"

        step_data = {
            "type": "step",
            "step": step,
            "red_position": node_name,
            "red_action": red_action_text,
            "blue_action": blue_action_text,
            "reward": float(reward),
            "is_crown_jewel": is_crown,
            "attack_path": [env.nodes.get(n, {}).get('name', '') for n in env.attack_path],
            "compromised_nodes": [nid for nid, n in env.nodes.items() if n['is_compromised']],
            "revoked_edges": [eid for eid, e in env.edges.items() if e['is_revoked']]
        }

        await _broadcast(step_data)
        await asyncio.sleep(0.5)  # Slower for better visualization
        step += 1
        
        # Check if crown jewel reached
        if env.nodes.get(env.red_position, {}).get('is_crown_jewel'):
            target_reached = env.nodes[env.red_position]['name']
            break

    result = "crown_jewel_reached" if info.get("result") == "crown_jewel_reached" else "blocked"
    duration = time.time() - start_time
    attack_path = [env.nodes.get(n, {}).get('name', '') for n in env.attack_path]
    
    # Save to database
    try:
        save_simulation(result, step, entry_name, target_reached, attack_path, duration)
    except Exception as e:
        print(f"Failed to save simulation: {e}")
    
    await _broadcast({"type": "simulation_end", "result": result,
                      "path": attack_path, "steps": step, "duration": round(duration, 2)})

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


@app.get("/api/dashboard")
def get_dashboard():
    """Get dashboard statistics"""
    try:
        from backend.database import get_dashboard_stats
        stats = get_dashboard_stats()
        
        # Add current graph stats
        if driver:
            with driver.session() as s:
                node_count = s.run("MATCH (n) RETURN count(n) as count").single()["count"]
                edge_count = s.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                entry_count = s.run("MATCH (n) WHERE n.is_entry_point = true RETURN count(n) as count").single()["count"]
                crown_count = s.run("MATCH (n) WHERE n.is_crown_jewel = true RETURN count(n) as count").single()["count"]
                
                stats["current_graph"] = {
                    "nodes": node_count,
                    "edges": edge_count,
                    "entry_points": entry_count,
                    "crown_jewels": crown_count
                }
        
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/history")
def get_history(limit: int = 50):
    """Get simulation history"""
    try:
        from backend.database import get_simulation_history
        return {"history": get_simulation_history(limit)}
    except Exception as e:
        return {"error": str(e), "history": []}

@app.get("/api/node/{node_id}")
def get_node_details(node_id: str):
    """Get detailed information about a specific node"""
    if not driver:
        return {"error": "Neo4j not connected"}
    
    try:
        with driver.session() as s:
            # Get node details
            node_result = s.run("""
                MATCH (n)
                WHERE elementId(n) = $node_id
                RETURN n, labels(n) as labels, elementId(n) as id
            """, node_id=node_id).single()
            
            if not node_result:
                return {"error": "Node not found"}
            
            node = node_result["n"]
            node_data = dict(node)
            node_data["id"] = node_result["id"]
            node_data["type"] = node_result["labels"][0] if node_result["labels"] else "Unknown"
            
            # Get incoming connections
            incoming = s.run("""
                MATCH (source)-[r]->(target)
                WHERE elementId(target) = $node_id
                RETURN source.name as source_name, type(r) as rel_type, 
                       r.anomaly_score as anomaly, elementId(source) as source_id
                LIMIT 20
            """, node_id=node_id).data()
            
            # Get outgoing connections
            outgoing = s.run("""
                MATCH (source)-[r]->(target)
                WHERE elementId(source) = $node_id
                RETURN target.name as target_name, type(r) as rel_type,
                       r.anomaly_score as anomaly, elementId(target) as target_id
                LIMIT 20
            """, node_id=node_id).data()
            
            return {
                "node": node_data,
                "incoming": incoming,
                "outgoing": outgoing
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/export/csv")
def export_csv():
    """Export risk data to CSV"""
    if not scorer:
        return {"error": "Scorer not initialized"}
    
    try:
        edges = scorer.get_riskiest_edges()
        paths = scorer.get_attack_paths()
        
        # Create CSV in memory
        output = io.StringIO()
        
        # Write edges
        writer = csv.writer(output)
        writer.writerow(["Type", "Source", "Target", "Risk Score", "Anomaly", "Blast Radius", "Recommendation"])
        
        for edge in edges:
            writer.writerow([
                "Edge",
                edge.src_name,
                edge.dst_name,
                edge.combined_risk,
                edge.anomaly_score,
                edge.blast_radius,
                edge.recommendation
            ])
        
        writer.writerow([])  # Empty row
        writer.writerow(["Type", "Path", "Total Risk", "Probability", "Target"])
        
        for path in paths:
            writer.writerow([
                "Path",
                " → ".join(path.path),
                path.total_risk,
                f"{path.reach_probability * 100:.0f}%",
                path.crown_jewel
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=trishul_risk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/search")
def search_nodes(query: str):
    """Search for nodes by name"""
    if not driver:
        return {"results": []}
    
    try:
        with driver.session() as s:
            results = s.run("""
                MATCH (n)
                WHERE toLower(n.name) CONTAINS toLower($query)
                RETURN elementId(n) as id, n.name as name, 
                       labels(n)[0] as type, n.trust_score as trust,
                       n.anomaly_score as anomaly
                LIMIT 20
            """, query=query).data()
            
            return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

@app.post("/api/whatif/remove-vendor")
def whatif_remove_vendor(vendor_name: str):
    """Simulate removing a vendor from the supply chain"""
    if not driver or not scorer:
        return {"error": "System not ready"}
    
    try:
        with driver.session() as s:
            # Get current risk
            current_edges = scorer.get_riskiest_edges(top_n=5)
            current_paths = scorer.get_attack_paths()
            
            # Simulate removal by checking paths that would be affected
            affected_paths = [p for p in current_paths if vendor_name in p.path]
            remaining_paths = [p for p in current_paths if vendor_name not in p.path]
            
            return {
                "vendor": vendor_name,
                "current_risk_paths": len(current_paths),
                "affected_paths": len(affected_paths),
                "remaining_paths": len(remaining_paths),
                "risk_reduction": f"{(len(affected_paths) / len(current_paths) * 100):.1f}%" if current_paths else "0%",
                "affected_path_details": [
                    {
                        "path": p.path,
                        "risk": p.total_risk,
                        "target": p.crown_jewel
                    } for p in affected_paths[:5]
                ]
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/whatif/add-mfa")
def whatif_add_mfa(node_name: str):
    """Simulate adding MFA to a node"""
    if not driver:
        return {"error": "Neo4j not connected"}
    
    try:
        with driver.session() as s:
            # Find edges connected to this node
            edges = s.run("""
                MATCH (n)-[r]->(target)
                WHERE n.name = $node_name
                RETURN count(r) as outgoing_count
            """, node_name=node_name).single()
            
            incoming = s.run("""
                MATCH (source)-[r]->(n)
                WHERE n.name = $node_name
                RETURN count(r) as incoming_count
            """, node_name=node_name).single()
            
            return {
                "node": node_name,
                "impact": "Adding MFA would protect all incoming connections",
                "incoming_connections": incoming["incoming_count"] if incoming else 0,
                "outgoing_connections": edges["outgoing_count"] if edges else 0,
                "estimated_risk_reduction": "30-50%",
                "recommendation": "High priority if this node has high anomaly score"
            }
    except Exception as e:
        return {"error": str(e)}
