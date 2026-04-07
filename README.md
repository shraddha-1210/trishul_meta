# TRISHUL (Threat Response Intelligence System for Hostile Unknown Laterals)

🔱 An AI-powered security system that uses reinforcement learning to find weaknesses in your supply chain before real hackers do.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Neo4j](https://img.shields.io/badge/neo4j-5.x-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Neo4j Database

### Installation (5 minutes)

1. **Start Neo4j** (choose one):
   - Neo4j Desktop: Download from https://neo4j.com/download/, create DB with password `trishul123`
   - Docker: `docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest`

2. **Setup and Seed** (one command):
   ```bash
   # Windows:
   setup_and_seed.bat
   
   # Mac/Linux:
   chmod +x setup_and_seed.sh
   ./setup_and_seed.sh
   ```

3. **Verify Setup** (optional but recommended):
   ```bash
   # Activate venv first
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   
   # Run test
   python test_connection.py
   ```

4. **Start Application** (two terminals):
   ```bash
   # Terminal 1 - Backend:
   start_backend.bat  # or ./start_backend.sh
   
   # Terminal 2 - Frontend:
   start_frontend.bat  # or ./start_frontend.sh
   ```

5. **Open Browser**: http://localhost:3000

## 🎯 Features

- 🕸️ **Interactive Graph Visualization** - See your supply chain as a live network
- 🤖 **AI Attack Simulation** - Watch red team (attacker) vs blue team (defender) battle in real-time
- 📊 **Risk Analysis** - Identify the riskiest paths and edges with CVSS-style scoring
- 🎯 **Attack Path Detection** - Find all possible routes from entry points to crown jewels
- 📄 **PDF Reports** - Generate security reports with actionable recommendations
- ⚡ **Real-time Updates** - WebSocket streaming of simulation events

## 🏗️ Architecture

```
Frontend (React + Cytoscape.js)
    ↓ REST API + WebSocket
Backend (FastAPI + RL Agents)
    ↓ Cypher Queries
Neo4j Graph Database
```

- **Backend**: FastAPI + Neo4j + Stable-Baselines3 (PPO algorithm)
- **Frontend**: React + Vite + Cytoscape.js for graph visualization
- **Database**: Neo4j 5.x with supply chain graph model
- **AI**: Reinforcement learning agents (red team attacker, blue team defender)

## 📚 Documentation

- **[INSTALL.md](docs/INSTALL.md)** - Detailed installation guide
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference
- **[COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)** - Comprehensive usage guide
- **[API_DOCS.md](docs/API_DOCS.md)** - API documentation
- **[FEATURES.md](docs/FEATURES.md)** - Feature list
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Code structure

## 🎮 Usage

1. **View Graph**: Interactive supply chain visualization with color-coded risk levels
2. **Analyze Risk**: Check top attack paths and riskiest edges in the right panel
3. **Run Simulation**: Click "▶️ Start Attack" to watch AI agents battle
4. **Generate Report**: Run `python -m backend.report_generator` for PDF

## 🔧 Training Custom Agents

The setup script creates dummy (untrained) agents for quick testing.

To train real agents (~10 minutes):
```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Train agents
python -m backend.train
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Neo4j - Graph database
- Stable-Baselines3 - RL library (PPO algorithm)
- Gymnasium - RL environment interface
- ReportLab - PDF generation

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Cytoscape.js - Graph visualization
- WebSocket - Real-time updates

## 📊 Graph Model

**Nodes:**
- 🏢 Vendors (entry points for attacks)
- 🎯 Services (crown jewels - critical systems)
- ⚙️ CI/CD Pipelines
- 📦 Dependencies (supply chain attack vectors)

**Edges:**
- HAS_TOKEN - API access relationships
- USES_DEPENDENCY - Package dependencies
- CAN_EXECUTE_IN - Execution permissions
- DEPLOYS_TO - Deployment relationships

## 🔐 Security Scenarios

TRISHUL simulates real-world attack patterns:
- **Token Compromise**: Vendor API token breach (Drift-style attack)
- **Supply Chain Attack**: Malicious dependency injection (axios example)
- **CI/CD Compromise**: Pipeline access to production
- **Lateral Movement**: Multi-hop attacks through trust relationships

## 🐛 Troubleshooting

**"Connection refused" to Neo4j:**
- Ensure Neo4j is running: Check http://localhost:7474
- Verify credentials in `.env` file

**"Module not found" errors:**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

**Frontend won't connect:**
- Check backend is running on port 8000
- Try http://127.0.0.1:3000 instead

See [COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md) for detailed troubleshooting.

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

Built with ❤️ for supply chain security

