# TRISHUL - Supply Chain Security System

AI-powered supply chain attack simulation using reinforcement learning.

---

## ⚡ SUPER QUICK START

**First time:**
```bash
INSTALL_AND_RUN.bat
```

**Every time after:**
```bash
START.bat                    # Terminal 1
start_frontend.bat           # Terminal 2 (NEW terminal)
# Open: http://localhost:3003
```

---

## 🚀 Quick Start (Recommended)

**FIRST TIME - Run this ONE command:**

```bash
INSTALL_AND_RUN.bat
```

**EVERY TIME AFTER:**

```bash
# Terminal 1:
START.bat

# Terminal 2 (open NEW terminal):
start_frontend.bat

# Browser:
http://localhost:3003
```

That's it! 🎉

## 🔧 If You Get Errors

### Error: "No module named 'neo4j'"
**Solution:** Run with venv Python
```bash
INSTALL_AND_RUN.bat
```

### Error: "Virtual environment not found"
**Solution:** Install first
```bash
INSTALL_AND_RUN.bat
```

### Error: "Neo4j connection failed"
**Solution:** Start Neo4j
```bash
docker start trishul-neo4j
```
Or create new:
```bash
docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest
```

### Error: "vite not found"
**Solution:** Install frontend dependencies
```bash
cd frontend
npm install
```

## 📋 System Check

Run diagnostics to see what's wrong:
```bash
diagnose.bat
```

## 🎯 Manual Start (After Setup)

**Terminal 1 - Backend:**
```bash
start_backend.bat
```

**Terminal 2 - Frontend:**
```bash
start_frontend.bat
```

## 🏗️ Project Structure

```
trishul_meta/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── env.py           # RL environment
│   ├── graph_seeder.py  # Database seeding
│   ├── database.py      # History tracking
│   ├── risk_scorer.py   # Risk analysis
│   └── train.py         # Agent training
├── frontend/            # React frontend
│   └── src/
│       ├── App.jsx
│       └── components/
├── checkpoints/         # AI agents (generated)
├── INSTALL_AND_RUN.bat  # 🔥 First time setup
├── START.bat            # Quick start
├── start_frontend.bat   # Frontend launcher
└── README.md            # You are here
```

See `FILE_STRUCTURE.txt` for complete details.

## 🎮 Features

- 🤖 **AI vs AI**: Red team (attacker) vs Blue team (defender)
- 📊 **Real-time Visualization**: See attacks unfold step-by-step
- 🎯 **113 Nodes**: Dense supply chain with 40 vendors, 18 services, 12 pipelines
- 📈 **Risk Scoring**: ML-powered vulnerability analysis
- 📝 **Detailed Logs**: Step-by-step attack progression
- 💾 **History Tracking**: All simulations saved to database

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Backend won't start | Run `FIX_ALL.bat` |
| Frontend shows errors | Run `cd frontend && npm install` |
| No graph data | Run `python backend\graph_seeder.py` |
| Button disabled | Check debug panel (top-right), ensure backend is connected |

## 📦 Requirements

- Python 3.8+
- Node.js 16+
- Docker (for Neo4j)
- 4GB RAM minimum

## 🔑 Default Credentials

- **Neo4j**: neo4j / trishul123
- **Backend**: http://localhost:8001
- **Frontend**: http://localhost:3003

## 📚 API Documentation

Once backend is running: http://localhost:8001/docs

## 🎯 How to Use

1. Run `FIX_ALL.bat` (first time only)
2. Start backend: `start_backend.bat`
3. Start frontend: `start_frontend.bat` (new terminal)
4. Open http://localhost:3003
5. Click "▶️ Start Attack" button
6. Watch the AI battle unfold!

## 🆘 Still Having Issues?

Run the diagnostic tool:
```bash
diagnose.bat
```

This will show you exactly what's wrong and how to fix it.

---

**Made with ❤️ using FastAPI, React, Neo4j, and Stable-Baselines3**
