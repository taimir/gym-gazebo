#!/usr/bin/env python
import gym
import gym_gazebo
import click
import numpy as np
import ipc

WINDOW_LENGTH = 10
WINDOW_SHIFT = 1

if __name__ == '__main__':
    env = gym.make('GazeboMazeTurtlebotLidar-v0')
    outdir = '/tmp/gazebo_gym_experiments'
    env.monitor.start(outdir, force=True, seed=None)

    observation = env.reset()

    client = ipc.SLAMClient()

    us = []
    xs = []
    while True:
        try:
            key = click.getchar()
            if key == 'a':
                action = 1
                u = np.array([0.0, 1.0], dtype="float32")
            elif key == 'd':
                action = 2
                u = np.array([1.0, 1.0], dtype="float32")
            elif key == 'w':
                action = 0
                u = np.array([-1.0, 0.0], dtype="float32")
            elif key == 's':
                action = 3
                u = np.array([0.0, -1.0], dtype="float32")
            else:
                u = np.array([0.0, 0.0], dtype="float32")
                action = None

            # Execute the action and get feedback
            observation, reward, done, info = env.step(action)
            x = np.array(observation, dtype="float32")

            us.append(u)
            xs.append(x)

            if len(us) == len(xs) == WINDOW_LENGTH:
                U = np.stack(us)[np.newaxis]
                print(U.shape)
                X = np.stack(xs)[np.newaxis]
                print(X.shape)

                client.send_data([X, U])

                # pop the first elements (effectively sliding the window)
                us = us[WINDOW_SHIFT:]
                xs = xs[WINDOW_SHIFT:]

            env.monitor.flush(force=True)

            if done:
                env.reset()
        except KeyboardInterrupt:
            break

    env.monitor.close()
    env.close()
