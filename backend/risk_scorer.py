from neo4j import GraphDatabase
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import os

load_dotenv()

@dataclass
class RiskyEdge:
    edge_id: str
    src_name: str
    dst_name: str
    edge_type: str
    anomaly_score: float
    blast_radius: int
    combined_risk: float
    recommendation: str

@dataclass
class AttackPath:
    path: List[str]
    total_risk: float
    reach_probability: float
    crown_jewel: str

class RiskScorer:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
        )

    def get_riskiest_edges(self, top_n=10) -> List[RiskyEdge]:
        """
        Finds edges with highest combined risk score
        combined_risk = anomaly_score * (1/trust_score) * log(blast_radius+1)
        this mirrors CVSS style scoring
        """
        with self.driver.session() as s:
            results = s.run("""
                MATCH (src)-[r]->(dst)
                WHERE r.is_revoked = false
                OPTIONAL MATCH (dst:Service)
                RETURN 
                    elementId(r) as rid,
                    src.name as src_name,
                    dst.name as dst_name,
                    type(r) as edge_type,
                    coalesce(r.anomaly_score, 0.1) as anomaly,
                    coalesce(src.trust_score, 50) as trust,
                    coalesce(dst.blast_radius, 0) as blast_radius,
                    coalesce(r.is_gated, false) as is_gated
                ORDER BY anomaly DESC
                LIMIT 50
            """).data()

        edges = []
        for row in results:
            import math
            trust_factor = 1 - (row['trust'] / 100.0)
            blast_factor = math.log(row['blast_radius'] + 1) / 10.0
            combined = row['anomaly'] * (0.4 + trust_factor * 0.4 + blast_factor * 0.2)

            rec = self._generate_recommendation(row)
            edges.append(RiskyEdge(
                edge_id=str(row['rid']),
                src_name=row['src_name'],
                dst_name=row['dst_name'],
                edge_type=row['edge_type'],
                anomaly_score=row['anomaly'],
                blast_radius=row['blast_radius'],
                combined_risk=round(combined, 3),
                recommendation=rec
            ))
        edges.sort(key=lambda e: e.combined_risk, reverse=True)
        return edges[:top_n]

    def get_attack_paths(self) -> List[AttackPath]:
        """Find all paths from entry vendors to crown jewels."""
        with self.driver.session() as s:
            results = s.run("""
                MATCH path = (v:Vendor)-[*1..4]->(svc:Service)
                WHERE v.is_entry_point = true
                  AND svc.is_crown_jewel = true
                  AND ALL(r IN relationships(path) WHERE r.is_revoked = false)
                RETURN 
                    [n IN nodes(path) | n.name] as node_names,
                    svc.name as crown_jewel,
                    svc.blast_radius as radius,
                    reduce(s=0.0, r IN relationships(path) | s + coalesce(r.anomaly_score,0)) as total_risk
                ORDER BY total_risk DESC
                LIMIT 10
            """).data()

        paths = []
        for row in results:
            reach_prob = min(0.99, row['total_risk'] / (len(row['node_names']) * 1.5))
            paths.append(AttackPath(
                path=row['node_names'],
                total_risk=round(row['total_risk'], 2),
                reach_probability=round(reach_prob, 2),
                crown_jewel=row['crown_jewel']
            ))
        return paths

    def _generate_recommendation(self, edge_row) -> str:
        recs = []
        if edge_row['anomaly'] > 0.8:
            recs.append(f"URGENT: Rotate token for {edge_row['src_name']} → {edge_row['dst_name']}")
        if not edge_row['is_gated']:
            recs.append(f"Add MFA gate on {edge_row['edge_type']} edge")
        if edge_row['trust'] < 50:
            recs.append(f"Vendor {edge_row['src_name']} below trust threshold — audit immediately")
        if edge_row['blast_radius'] > 500:
            recs.append(f"Segment {edge_row['dst_name']} — blast radius {edge_row['blast_radius']} customers")
        return "; ".join(recs) if recs else "Monitor closely"
