from neo4j import GraphDatabase
from dotenv import load_dotenv
import os, random

load_dotenv()

VENDORS = [
    # name, trust_score, is_entry_point (low trust = attacker starts here)
    ("AuthFlow Systems", 38, True), # Drift-style: has token to Salesforce 
    ("PipelineForge", 29, True), # has CI access to prod 
    ("CloudSync Ltd", 45, True), # has payment gateway token 
    ("DataBridge Inc", 72, False), #uses axios(Axios vec attack)
    ("DevOps Partners", 81, False),
    ("SecureVault APIs", 88, False),
    ("LogicNest Co", 65, False),
    ("NexaBuild Tools", 71, False)
]

SERVICES = [
    #name, sensitivity, blast_radius (how many customers affected)
    ("Salesforce CRM", "critical", 847),
    ("Production Database", "critical", 1200),
    ("Payment Gateway", "critical", 430),
    ("GitHub Main Repo", "high", 200)
] 

PIPELINES = [
    ("CI Deploy Pipelines", True), #has_secrets=True
    ("Build Automation", True),
    ("Test Runner", False)
]

DEPENDENCIES = [
    #name, version, anomaly_score(0-1), weekly_downloads
    ("axios", "1.41.1", 0.95, 100_000_000), #attack
    ("plain-crypto-js", "4.2.1", 0.98, 0), #pre-staged malware
    ("lodash", "4.17.21", 0.10, 40_000_000),
    ("requests", "2.31.0", 0.08, 50_000_000)
]

class GraphSeeder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth = (os.getenv("NEO4J_USER"),os.getenv("NEO4J_PASS")),
        )

    def seed(self):
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")
            self._create_vendors(s)
            self._create_services(s)
            self._create_pipelines(s)
            self._create_dependencies(s)
            self._create_edges(s)
            print("✅ Graph seeded")

    def _create_vendors(self, s):
        for name, trust, entry in VENDORS:
            s.run(""" CREATE (
            :Vendor { 
            id: $id, 
            name: $name, 
            trust_score: $trust, 
            anomaly_score: $anomaly, 
            is_entry_point: $entry, 
            is_compromised: false, 
            mfa_enabled: $mfa }) """, 
            id=name.lower().replace(" ","_"), 
            name=name, 
            trust=trust, anomaly=round(1-(trust/100), 2), 
            entry=entry, mfa=(trust > 70))

        
    def _create_services(self, s):
        for name, sensitivity, radius in SERVICES:
            s.run(""" CREATE (:Service { id: $id, name: $name, sensitivity: $s, blast_radius: $r, is_crown_jewel: true }) """, id=name.lower().replace(" ","_"), name=name, s=sensitivity, r=radius)

    def _create_pipelines(self,s):     
        for name, secrets in PIPELINES: 
            s.run(""" CREATE (:Pipeline { id: $id, name: $name, has_secrets_access: $secrets }) """, id=name.lower().replace(" ","_"), name=name, secrets=secrets)


    def _create_dependencies(self, s):
        for name, ver, anomaly, downloads in DEPENDENCIES: 
            s.run(""" CREATE (:Dependency { id: $id, name: $name, version: $ver, anomaly_score: $anomaly, weekly_downloads: $dl, flagged: $flagged }) """, id=f"{name}_{ver}", name=name, ver=ver, anomaly=anomaly, dl=downloads, flagged=(anomaly > 0.8))

    def _create_edges(self, s):
        #AuthFlow -> Salesforce(Drift attack path)
        s.run(""" MATCH (v:Vendor {name:'AuthFlow Systems'}), (svc:Service {name:'Salesforce CRM'}) CREATE (v)-[:HAS_TOKEN { scope:'read:write:admin', anomaly_score:0.87, is_revoked:false, is_gated:false, token_id:'tok_auth_sf_001' }]->(svc) """) 
        # PipelineForge → Production DB 
        s.run(""" MATCH (v:Vendor {name:'PipelineForge'}), (svc:Service {name:'Production Database'}) CREATE (v)-[:HAS_TOKEN { scope:'read:write', anomaly_score:0.79, is_revoked:false, is_gated:false, token_id:'tok_pipe_db_001' }]->(svc) """) 
        # DataBridge uses axios (supply chain path) 
        s.run(""" MATCH (v:Vendor {name:'DataBridge Inc'}), (d:Dependency {name:'axios'}) CREATE (v)-[:USES_DEPENDENCY { auto_update:true, anomaly_score:0.92 }]->(d) """) 
        # axios → CI pipeline (postinstall hook) 
        s.run(""" MATCH (d:Dependency {name:'axios'}), (p:Pipeline {name:'CI Deploy Pipeline'}) CREATE (d)-[:CAN_EXECUTE_IN { via:'postinstall_hook', anomaly_score:0.95 }]->(p) """) 
        # CI pipeline → GitHub (deploys to) 
        s.run(""" MATCH (p:Pipeline {name:'CI Deploy Pipeline'}), (svc:Service {name:'GitHub Main Repo'}) CREATE (p)-[:DEPLOYS_TO { anomaly_score:0.40, is_gated:true }]->(svc) """) 
        # CloudSync → Payment Gateway 
        s.run(""" MATCH (v:Vendor {name:'CloudSync Ltd'}), (svc:Service {name:'Payment Gateway'}) CREATE (v)-[:HAS_TOKEN { scope:'read:write', anomaly_score:0.71, is_revoked:false, is_gated:false, token_id:'tok_cloud_pay_001' }]->(svc) """) 
        
        

if __name__ == "__main__": 
    GraphSeeder().seed()