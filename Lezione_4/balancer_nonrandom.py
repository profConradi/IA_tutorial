import argparse

import gym

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Run an environment')
    parser.add_argument('--input-env', dest='input_env', required=True,
            choices=['cartpole', 'mountaincar', 'pendulum'], 
            help='Specify the name of the environment')
    return parser

if __name__=='__main__':
    args = build_arg_parser().parse_args()
    input_env = args.input_env

    name_map = {'cartpole': 'CartPole-v0', 
                'mountaincar': 'MountainCar-v0',
                'pendulum': 'Pendulum-v0'}

    # Create the environment 
    env = gym.make(name_map[input_env])
    highscore = 0
    # Start iterating 
    for _ in range(20):
        # Reset the environment
        observation = env.reset()
        points = 0 # keep track of the reward each episode
        # Iterate 100 times
        for i in range(100):
            # Render the environment
            env.render()

            # if angle if positive, move right. if angle is negative, move left
            if observation[2] > 0:
                action = 1 
            else:
                action = 0 

            # Print the current observation
            print(observation)

            # Extract the observation, reward, status and 
            # other info based on the action taken
            observation, reward, done, info = env.step(action)
            points += reward

            # Check if it's done
            if done:
                print('Episode finished after {} timesteps'.format(i+1))
                if points > highscore: # record high score
                    highscore = points
                break

    print('Highscore: {}'.format(highscore))