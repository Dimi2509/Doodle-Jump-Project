from stable_baselines3 import PPO
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env # Used to create parallel environments
from RLMain import DoodleEnv
import time
import datetime
import os
from stable_baselines3.common.callbacks import CheckpointCallback

models_dir = f"models/PPO_{datetime.datetime.now().strftime('%d_%m_%y')}/"
logdir = f"logs/PPO_{datetime.datetime.now().strftime('%d_%m_%y')}/"
#models_dir = f"models/PPO_{int(time.time())}/"
#logdir = f"logs/PPO_{int(time.time())}/"

if not os.path.exists(models_dir):
	os.makedirs(models_dir)

if not os.path.exists(logdir):
	os.makedirs(logdir)

env = DoodleEnv()
env.reset()

LEARNING_RATE = 0.0001 # Default is 0.0003 MAYBE INTRODUCE VARYING LEARNING RATE TO SEE HOW IT WORKS
EXPLORATION_FINAL_EPS = 0.1 # Default is 0.05
# model = DQN(
#   'MultiInputPolicy', 
#   env, 
#   verbose=1, 
#   tensorboard_log=logdir, 
#   learning_rate=LEARNING_RATE, 
#   exploration_fraction=0.12,
#   batch_size=64,
#   target_update_interval=1000,
#   learning_starts=1000,
#   buffer_size=100000,
#   exploration_final_eps=EXPLORATION_FINAL_EPS
# ) # Initially "MlpPolicy", but now with dict we need "MultiInputPolicy"

model = PPO(
  'MultiInputPolicy', 
  env, 
  verbose=1, 
  tensorboard_log=logdir, 
  learning_rate=LEARNING_RATE
)

TIMESTEPS = 1_000_000
iters = 0

checkpoint_callback = CheckpointCallback(
  save_freq=100_000,
  save_path=f"{models_dir}/",
  name_prefix="PPO_model",
  #save_replay_buffer=True,
)

model.learn(total_timesteps=TIMESTEPS, tb_log_name=f"PPO", callback=checkpoint_callback)
model.save(f"{models_dir}/final_model_{LEARNING_RATE}LR")