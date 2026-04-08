"""
SQLite database for storing simulation history and metrics
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import os

DB_PATH = "trishul_history.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Simulations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            result TEXT,
            steps INTEGER,
            entry_point TEXT,
            target_reached TEXT,
            attack_path TEXT,
            duration_seconds REAL
        )
    ''')
    
    # Metrics table
    c.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_nodes INTEGER,
            total_edges INTEGER,
            entry_points INTEGER,
            crown_jewels INTEGER,
            avg_risk_score REAL,
            high_risk_paths INTEGER
        )
    ''')
    
    # Node history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS node_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            node_name TEXT,
            node_type TEXT,
            trust_score REAL,
            anomaly_score REAL,
            times_compromised INTEGER DEFAULT 0,
            last_compromised DATETIME,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_simulation(result: str, steps: int, entry_point: str, 
                   target_reached: str, attack_path: List[str], 
                   duration: float):
    """Save simulation results"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO simulations 
        (result, steps, entry_point, target_reached, attack_path, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (result, steps, entry_point, target_reached, 
          json.dumps(attack_path), duration))
    
    conn.commit()
    conn.close()

def save_metrics(total_nodes: int, total_edges: int, entry_points: int,
                crown_jewels: int, avg_risk: float, high_risk_paths: int):
    """Save current graph metrics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO metrics 
        (total_nodes, total_edges, entry_points, crown_jewels, 
         avg_risk_score, high_risk_paths)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (total_nodes, total_edges, entry_points, crown_jewels,
          avg_risk, high_risk_paths))
    
    conn.commit()
    conn.close()

def get_simulation_history(limit: int = 50) -> List[Dict]:
    """Get recent simulation history"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM simulations 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_metrics_history(limit: int = 30) -> List[Dict]:
    """Get metrics history"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM metrics 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_dashboard_stats() -> Dict:
    """Get dashboard statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Total simulations
    c.execute('SELECT COUNT(*) FROM simulations')
    total_sims = c.fetchone()[0]
    
    # Success rate
    c.execute('''
        SELECT 
            COUNT(CASE WHEN result = 'crown_jewel_reached' THEN 1 END) as breaches,
            COUNT(CASE WHEN result = 'blocked' THEN 1 END) as blocked
        FROM simulations
    ''')
    breaches, blocked = c.fetchone()
    
    # Average steps
    c.execute('SELECT AVG(steps) FROM simulations')
    avg_steps = c.fetchone()[0] or 0
    
    # Most targeted services
    c.execute('''
        SELECT target_reached, COUNT(*) as count 
        FROM simulations 
        WHERE target_reached IS NOT NULL
        GROUP BY target_reached 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_targets = [{"name": row[0], "count": row[1]} for row in c.fetchall()]
    
    conn.close()
    
    return {
        "total_simulations": total_sims,
        "breaches": breaches,
        "blocked": blocked,
        "success_rate": (breaches / total_sims * 100) if total_sims > 0 else 0,
        "avg_steps": round(avg_steps, 1),
        "top_targets": top_targets
    }

# Initialize database on import
if not os.path.exists(DB_PATH):
    init_db()
