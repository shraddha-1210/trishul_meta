from neo4j import GraphDatabase
from dotenv import load_dotenv
import os, random

load_dotenv()

VENDORS = [
    # Tier 1 - Critical Infrastructure (High Trust)
    ("SecureVault APIs", 88, False),
    ("DevOps Partners", 81, False),
    ("CloudBridge Co", 67, False),
    ("SecureLink APIs", 73, False),
    ("BuildMaster Tools", 58, False),
    ("DevStream Partners", 69, False),
    ("ApiGate Systems", 76, False),
    ("CloudOps Solutions", 62, False),
    ("SecureFlow APIs", 79, False),
    ("TechGuard Systems", 84, False),
    
    # Tier 2 - Medium Trust Vendors
    ("DataBridge Inc", 72, False),
    ("LogicNest Co", 65, False),
    ("NexaBuild Tools", 71, False),
    ("CodeStream Inc", 55, False),
    ("DataPipe Systems", 48, False),
    ("FlowSync Ltd", 51, False),
    ("CloudMesh Solutions", 59, False),
    ("ApiFlow Systems", 64, False),
    ("DataSync Corp", 57, False),
    ("BuildFlow Inc", 63, False),
    
    # Tier 3 - Entry Points (Low Trust - Attack Vectors)
    ("AuthFlow Systems", 38, True),
    ("PipelineForge", 29, True),
    ("CloudSync Ltd", 45, True),
    ("TechFlow Solutions", 42, True),
    ("DataFlow Inc", 44, True),
    ("QuickBuild Systems", 35, True),
    ("FastDeploy Co", 31, True),
    ("RapidSync Ltd", 39, True),
    ("InstaBuild Tools", 33, True),
    ("SpeedFlow Systems", 37, True),
    ("AgileOps Inc", 41, True),
    ("DevFast Solutions", 36, True),
    ("QuickPipe Co", 34, True),
    ("RushDeploy Ltd", 32, True),
    ("SwiftBuild Systems", 40, True),
    
    # Tier 4 - Specialized Services
    ("MonitorFlow Systems", 68, False),
    ("LogStream Inc", 61, False),
    ("MetricsHub Co", 66, False),
    ("AlertFlow Systems", 70, False),
    ("TraceOps Ltd", 60, False)
]

SERVICES = [
    # Critical Crown Jewels
    ("Salesforce CRM", "critical", 847),
    ("Production Database", "critical", 1200),
    ("Payment Gateway", "critical", 430),
    ("AWS Infrastructure", "critical", 980),
    ("Customer Data Lake", "critical", 1500),
    ("Authentication Service", "critical", 2100),
    
    # High Value Targets
    ("GitHub Main Repo", "high", 200),
    ("Email Service", "high", 650),
    ("Backup Systems", "high", 890),
    ("API Gateway", "high", 750),
    ("Load Balancer", "high", 820),
    ("CDN Service", "high", 940),
    
    # Medium Value Targets
    ("Analytics Platform", "medium", 320),
    ("Logging Service", "medium", 280),
    ("Monitoring Dashboard", "medium", 310),
    ("Notification Service", "medium", 290),
    ("Search Engine", "medium", 340),
    ("Cache Layer", "medium", 260)
]

PIPELINES = [
    ("CI Deploy Pipeline", True),
    ("Build Automation", True),
    ("Test Runner", False),
    ("Staging Pipeline", True),
    ("Production Deploy", True),
    ("Docker Registry", True),
    ("Artifact Storage", False),
    ("QA Pipeline", False),
    ("Integration Pipeline", True),
    ("Release Pipeline", True),
    ("Hotfix Pipeline", True),
    ("Rollback Pipeline", False)
]

DEPENDENCIES = [
    # Critical Supply Chain Risks (High Anomaly)
    ("axios", "1.41.1", 0.95, 100_000_000),
    ("plain-crypto-js", "4.2.1", 0.98, 0),
    ("jwt-decode", "3.1.2", 0.91, 8_500_000),
    ("stripe", "5.5.0", 0.87, 5_000_000),
    ("twilio", "8.5.0", 0.82, 4_000_000),
    ("sendgrid", "6.10.0", 0.79, 3_500_000),
    ("malicious-package", "1.0.0", 0.99, 100),
    ("crypto-miner", "2.1.0", 0.97, 500),
    ("backdoor-lib", "1.5.0", 0.96, 200),
    
    # Popular but Risky
    ("lodash", "4.17.21", 0.10, 40_000_000),
    ("requests", "2.31.0", 0.08, 50_000_000),
    ("express", "4.18.2", 0.12, 30_000_000),
    ("redis-py", "4.5.0", 0.15, 7_000_000),
    ("celery", "5.3.0", 0.14, 6_000_000),
    ("pandas", "2.0.0", 0.11, 18_000_000),
    
    # Safe Dependencies
    ("react", "18.2.0", 0.05, 25_000_000),
    ("django", "4.2.0", 0.07, 15_000_000),
    ("flask", "2.3.0", 0.09, 12_000_000),
    ("fastapi", "0.104.0", 0.06, 8_000_000),
    ("numpy", "1.24.0", 0.04, 20_000_000),
    ("tensorflow", "2.13.0", 0.13, 10_000_000),
    ("pytorch", "2.0.0", 0.08, 9_000_000),
    ("boto3", "1.28.0", 0.10, 22_000_000),
    
    # Additional Dependencies
    ("webpack", "5.88.0", 0.16, 12_000_000),
    ("babel", "7.22.0", 0.09, 15_000_000),
    ("typescript", "5.1.0", 0.06, 18_000_000),
    ("eslint", "8.44.0", 0.07, 14_000_000),
    ("jest", "29.5.0", 0.08, 11_000_000),
    ("mocha", "10.2.0", 0.10, 8_000_000),
    ("chai", "4.3.0", 0.09, 7_000_000),
    ("sinon", "15.2.0", 0.11, 6_000_000),
    ("puppeteer", "20.7.0", 0.17, 5_000_000),
    ("selenium", "4.10.0", 0.14, 9_000_000),
    ("cypress", "12.17.0", 0.12, 7_500_000),
    ("playwright", "1.35.0", 0.13, 6_500_000),
    ("graphql", "16.6.0", 0.10, 10_000_000),
    ("apollo", "3.7.0", 0.11, 8_000_000),
    ("prisma", "4.16.0", 0.15, 7_000_000),
    ("sequelize", "6.32.0", 0.12, 9_000_000),
    ("mongoose", "7.3.0", 0.13, 11_000_000),
    ("typeorm", "0.3.17", 0.14, 6_000_000),
    ("knex", "2.4.0", 0.11, 5_000_000),
    ("socket.io", "4.6.0", 0.18, 8_500_000)
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
        # Create dense, realistic attack graph with multiple paths
        import random
        
        # === ATTACK VECTOR 1: Direct Vendor → Service (Token Compromise) ===
        vendor_service_connections = [
            # Critical paths (high anomaly)
            ("AuthFlow Systems", "Salesforce CRM", 0.87),
            ("PipelineForge", "Production Database", 0.79),
            ("CloudSync Ltd", "Payment Gateway", 0.71),
            ("TechFlow Solutions", "AWS Infrastructure", 0.84),
            ("DataFlow Inc", "Customer Data Lake", 0.88),
            ("QuickBuild Systems", "Authentication Service", 0.92),
            ("FastDeploy Co", "GitHub Main Repo", 0.81),
            ("RapidSync Ltd", "Email Service", 0.75),
            ("InstaBuild Tools", "API Gateway", 0.83),
            ("SpeedFlow Systems", "Load Balancer", 0.78),
            
            # Medium risk paths
            ("AgileOps Inc", "CDN Service", 0.68),
            ("DevFast Solutions", "Analytics Platform", 0.65),
            ("QuickPipe Co", "Logging Service", 0.62),
            ("RushDeploy Ltd", "Monitoring Dashboard", 0.69),
            ("SwiftBuild Systems", "Notification Service", 0.64),
            
            # Trusted vendors (lower anomaly)
            ("SecureVault APIs", "Backup Systems", 0.45),
            ("DevOps Partners", "Search Engine", 0.42),
            ("CloudBridge Co", "Cache Layer", 0.38),
            ("SecureLink APIs", "Production Database", 0.52),
            ("BuildMaster Tools", "GitHub Main Repo", 0.48)
        ]
        
        for vendor, service, anomaly in vendor_service_connections:
            s.run(f"""
                MATCH (v:Vendor {{name:'{vendor}'}}), (svc:Service {{name:'{service}'}})
                CREATE (v)-[:HAS_TOKEN {{
                    scope:'read:write:admin',
                    anomaly_score:{anomaly},
                    is_revoked:false,
                    is_gated:{str(anomaly < 0.5).lower()},
                    token_id:'tok_{vendor.lower().replace(" ", "_")}_{service.lower().replace(" ", "_")}'
                }}]->(svc)
            """)
        
        # === ATTACK VECTOR 2: Vendor → Dependency (Supply Chain) ===
        vendor_dependency_connections = [
            # High-risk dependencies
            ("DataBridge Inc", "axios", 0.92),
            ("QuickBuild Systems", "plain-crypto-js", 0.95),
            ("FastDeploy Co", "malicious-package", 0.98),
            ("InstaBuild Tools", "crypto-miner", 0.94),
            ("SpeedFlow Systems", "backdoor-lib", 0.93),
            ("AgileOps Inc", "jwt-decode", 0.89),
            ("DevFast Solutions", "stripe", 0.86),
            ("QuickPipe Co", "twilio", 0.81),
            ("RushDeploy Ltd", "sendgrid", 0.78),
            
            # Medium-risk dependencies
            ("CodeStream Inc", "express", 0.15),
            ("CloudBridge Co", "react", 0.08),
            ("BuildMaster Tools", "django", 0.12),
            ("DevStream Partners", "fastapi", 0.09),
            ("ApiGate Systems", "flask", 0.11),
            ("CloudOps Solutions", "boto3", 0.14),
            ("DataPipe Systems", "redis-py", 0.16),
            ("FlowSync Ltd", "celery", 0.17),
            ("LogicNest Co", "pandas", 0.13),
            ("NexaBuild Tools", "webpack", 0.18),
            
            # Additional connections for density
            ("TechFlow Solutions", "typescript", 0.10),
            ("DataFlow Inc", "graphql", 0.12),
            ("CloudSync Ltd", "socket.io", 0.19),
            ("AuthFlow Systems", "puppeteer", 0.16),
            ("PipelineForge", "selenium", 0.15),
            ("RapidSync Ltd", "cypress", 0.14),
            ("SwiftBuild Systems", "playwright", 0.13),
            ("MonitorFlow Systems", "apollo", 0.11),
            ("LogStream Inc", "prisma", 0.16),
            ("MetricsHub Co", "sequelize", 0.14)
        ]
        
        for vendor, dep, anomaly in vendor_dependency_connections:
            s.run(f"""
                MATCH (v:Vendor {{name:'{vendor}'}}), (d:Dependency {{name:'{dep}'}})
                CREATE (v)-[:USES_DEPENDENCY {{
                    auto_update:true,
                    anomaly_score:{anomaly}
                }}]->(d)
            """)
        
        # === ATTACK VECTOR 3: Dependency → Pipeline (Code Execution) ===
        dependency_pipeline_connections = [
            # Critical execution paths
            ("axios", "CI Deploy Pipeline", 0.95),
            ("plain-crypto-js", "Build Automation", 0.97),
            ("malicious-package", "Production Deploy", 0.99),
            ("crypto-miner", "Staging Pipeline", 0.96),
            ("backdoor-lib", "Integration Pipeline", 0.94),
            ("jwt-decode", "Release Pipeline", 0.91),
            ("stripe", "Hotfix Pipeline", 0.88),
            
            # Medium-risk execution
            ("express", "Test Runner", 0.18),
            ("webpack", "Build Automation", 0.20),
            ("typescript", "CI Deploy Pipeline", 0.12),
            ("babel", "Build Automation", 0.14),
            ("jest", "Test Runner", 0.10),
            ("mocha", "QA Pipeline", 0.11),
            ("puppeteer", "Integration Pipeline", 0.19),
            ("selenium", "QA Pipeline", 0.17),
            ("cypress", "Test Runner", 0.15),
            ("socket.io", "Production Deploy", 0.21),
            
            # Additional paths
            ("graphql", "Staging Pipeline", 0.13),
            ("apollo", "Integration Pipeline", 0.14),
            ("prisma", "CI Deploy Pipeline", 0.16),
            ("sequelize", "Build Automation", 0.15),
            ("mongoose", "Production Deploy", 0.17),
            ("typeorm", "Staging Pipeline", 0.16)
        ]
        
        for dep, pipeline, anomaly in dependency_pipeline_connections:
            s.run(f"""
                MATCH (d:Dependency {{name:'{dep}'}}), (p:Pipeline {{name:'{pipeline}'}})
                CREATE (d)-[:CAN_EXECUTE_IN {{
                    via:'postinstall_hook',
                    anomaly_score:{anomaly}
                }}]->(p)
            """)
        
        # === ATTACK VECTOR 4: Pipeline → Service (Deployment Access) ===
        pipeline_service_connections = [
            # Critical deployment paths
            ("CI Deploy Pipeline", "GitHub Main Repo", 0.40, True),
            ("Production Deploy", "Production Database", 0.72, True),
            ("Production Deploy", "AWS Infrastructure", 0.68, True),
            ("Staging Pipeline", "Customer Data Lake", 0.55, False),
            ("Integration Pipeline", "API Gateway", 0.62, False),
            ("Release Pipeline", "Load Balancer", 0.58, True),
            ("Hotfix Pipeline", "Production Database", 0.75, True),
            
            # Build and test access
            ("Build Automation", "GitHub Main Repo", 0.35, True),
            ("Build Automation", "Docker Registry", 0.42, False),
            ("Docker Registry", "AWS Infrastructure", 0.48, False),
            ("QA Pipeline", "Staging Pipeline", 0.30, False),
            ("Test Runner", "Analytics Platform", 0.25, False),
            
            # Additional deployment paths
            ("CI Deploy Pipeline", "CDN Service", 0.45, True),
            ("Production Deploy", "Payment Gateway", 0.78, True),
            ("Staging Pipeline", "Email Service", 0.52, False),
            ("Integration Pipeline", "Notification Service", 0.48, False),
            ("Release Pipeline", "Backup Systems", 0.55, True),
            ("Hotfix Pipeline", "Authentication Service", 0.82, True)
        ]
        
        for pipeline, service, anomaly, gated in pipeline_service_connections:
            s.run(f"""
                MATCH (p:Pipeline {{name:'{pipeline}'}}), (svc:Service {{name:'{service}'}})
                CREATE (p)-[:DEPLOYS_TO {{
                    anomaly_score:{anomaly},
                    is_gated:{str(gated).lower()}
                }}]->(svc)
            """)
        
        # === ATTACK VECTOR 5: Service → Service (Lateral Movement) ===
        service_service_connections = [
            ("API Gateway", "Production Database", 0.65),
            ("Load Balancer", "API Gateway", 0.58),
            ("CDN Service", "Load Balancer", 0.52),
            ("Authentication Service", "Customer Data Lake", 0.70),
            ("Email Service", "Notification Service", 0.45),
            ("Logging Service", "Monitoring Dashboard", 0.38),
            ("Analytics Platform", "Customer Data Lake", 0.62),
            ("Cache Layer", "Production Database", 0.55),
            ("Search Engine", "Analytics Platform", 0.48)
        ]
        
        for src_svc, dst_svc, anomaly in service_service_connections:
            s.run(f"""
                MATCH (src:Service {{name:'{src_svc}'}}), (dst:Service {{name:'{dst_svc}'}})
                CREATE (src)-[:CONNECTS_TO {{
                    anomaly_score:{anomaly},
                    is_revoked:false
                }}]->(dst)
            """)
        
        # === ATTACK VECTOR 6: Vendor → Pipeline (Direct CI Access) ===
        vendor_pipeline_connections = [
            ("PipelineForge", "CI Deploy Pipeline", 0.85),
            ("FastDeploy Co", "Production Deploy", 0.88),
            ("QuickBuild Systems", "Build Automation", 0.82),
            ("DevOps Partners", "Release Pipeline", 0.55),
            ("BuildMaster Tools", "Integration Pipeline", 0.60),
            ("AgileOps Inc", "Hotfix Pipeline", 0.78)
        ]
        
        for vendor, pipeline, anomaly in vendor_pipeline_connections:
            s.run(f"""
                MATCH (v:Vendor {{name:'{vendor}'}}), (p:Pipeline {{name:'{pipeline}'}})
                CREATE (v)-[:HAS_CI_ACCESS {{
                    anomaly_score:{anomaly},
                    is_revoked:false
                }}]->(p)
            """) 
        
        

if __name__ == "__main__": 
    GraphSeeder().seed()