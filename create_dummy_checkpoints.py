"""
Creates dummy checkpoint files for testing without training.
Only use this for quick testing - train real agents for actual use.
"""
import os
from stable_baselines3 import PPO
from backend.env import TrishulEnv

CHECKPOINT_DIR = "checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("Creating dummy checkpoints for testing...")

# Create minimal red agent
red_env = TrishulEnv(agent_type="red")
red_agent = PPO("MlpPolicy", red_env, verbose=0)
red_agent.save(f"{CHECKPOINT_DIR}/red_final")
print("✅ Created red_final checkpoint")

# Create minimal blue agent
blue_env = TrishulEnv(agent_type="blue")
blue_agent = PPO("MlpPolicy", blue_env, verbose=0)
blue_agent.save(f"{CHECKPOINT_DIR}/blue_final")
print("✅ Created blue_final checkpoint")

print("\n⚠️  These are untrained agents - they will perform randomly!")
print("For real use, run: python -m backend.train")
