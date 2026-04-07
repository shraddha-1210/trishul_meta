#!/bin/bash

echo "========================================"
echo "TRISHUL Setup and Seed Script"
echo "========================================"
echo ""

echo "Step 1: Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

echo "Step 2: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 3: Seeding Neo4j database..."
python -m backend.graph_seeder
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to seed database"
    echo "Make sure Neo4j is running on bolt://localhost:7687"
    exit 1
fi

echo ""
echo "Step 4: Creating dummy checkpoints..."
python create_dummy_checkpoints.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create checkpoints"
    exit 1
fi

echo ""
echo "========================================"
echo "SUCCESS! Setup complete."
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Open a new terminal and run: ./start_backend.sh"
echo "2. Open another terminal and run: ./start_frontend.sh"
echo "3. Open browser to http://localhost:3000"
echo ""
