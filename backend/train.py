from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from backend.env import TrishulEnv
import os

CHECKPOINT_DIR = "checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

CURRICULUM = [
    {"timesteps": 10_000, "label": "stage1_warmup"},
    {"timesteps": 30_000, "label": "stage2_medium"},
    {"timesteps": 60_000, "label": "stage3_full"},
    {"timesteps": 50_000, "label": "stage4_advanced"}
]

def make_red_env():
    return DummyVecEnv([lambda: TrishulEnv(agent_type="red")])

def make_blue_env():
    return DummyVecEnv([lambda: TrishulEnv(agent_type="blue")])

def train():
    print("Training Red Agent...")
    red_env = make_red_env()
    red_agent = PPO(
        "MlpPolicy", red_env, learning_rate=3e-4,
        n_steps=512, batch_size=64, n_epochs=10,
        gamma=0.99, gae_lambda=0.95, clip_range=0.2, verbose=1
    )

    print("Training Blue Agent...")
    blue_env = make_blue_env()
    blue_agent = PPO(
        "MlpPolicy", blue_env, learning_rate=3e-4,
        n_steps=512, batch_size=64, n_epochs=10, gamma =0.99,
        gae_lambda=0.95, clip_range=0.2, verbose=1
    )

    for stage in CURRICULUM:
        print(f"\n {stage['label']} - {stage['timesteps']} timesteps each")

        red_agent.learn(
            total_timesteps = stage['timesteps'],
            callback = CheckpointCallback(
                save_freq=1000, save_path=CHECKPOINT_DIR,
                name_prefix = f"red_{stage['label']}"
            ) 
        )

        blue_agent.learn(
            total_timesteps = stage['timesteps'],
            callback = CheckpointCallback(
                save_freq=1000, save_path=CHECKPOINT_DIR,
                name_prefix = f"blue_{stage['label']}"
            ) 
        )

        _evaluate(red_agent, blue_agent)

    red_agent.save(f"{CHECKPOINT_DIR}/red_final")
    blue_agent.save(f"{CHECKPOINT_DIR}/blue_final")
    print("Training complete. Models saved")


def _evaluate(red, blue, episodes=20):
    """Quick eval: what % of red attacks does blue catch?"""
    red_wins =0
    blue_wins=0
    for _ in range(episodes):
        env = TrishulEnv(agent_type="red")
        obs, _ = env.reset()
        done = False
        red_won = False

        while not done:
            red_action, _ = red.predict(obs, deterministic=False)
            obs, reward, done, _, info = env.step(int(red_action))
            if info.get("result") == "crown_jewel_reached":
                red_won = True

        
        if red_won:
            red_wins+=1
        else:
            blue_wins+=1
    catch_rate = blue_wins/episodes *100
    print(f"   Defender catch rate: {catch_rate:.0f}% ({blue_wins}/{episodes} episodes)")

if __name__ == "__main__":
    train()


