# Doodle-Jump-Project
Doodle Jump is a popular infinite platform game which consists on reaching the highest
score without falling. In this repository, a copy of this famous game has been created
using PyGame for then, adapting the game to Gymnasium's API environment to work with 
Stable Baseline 3, a module in charge of introducing popular Reinforcement Learning algorithms
to train an agent that can get the best score possible in this game.

## Technologies used
-Python
-Pygame
-Tensorboard
-Stable Baseline 3(SB3)
-Gymnasium

## Files
*Doodle.py* contains the classes and the core of the game.
*RLMain.py* creates the gymnasium environment using the existing game
*SB3_Training.py* here is where SB3 and the algorithms are tuned for then start the training process

*Logs* contains the trained algorithm logs, ready to be visualized in tensorboard
*models* stores the different trained models, specifying the number of steps and algorithm