### MDP Value Iteration and Policy Iteration

import numpy as np
import gym
import time
from lake_envs import *

np.set_printoptions(precision=3)

"""
For policy_evaluation, policy_improvement, policy_iteration and value_iteration,
the parameters P, nS, nA, gamma are defined as follows:

    P: nested dictionary
        From gym.core.Environment
        For each pair of states in [1, nS] and actions in [1, nA], P[state][action] is a
        tuple of the form (probability, nextstate, reward, terminal) where
            - probability: float
                the probability of transitioning from "state" to "nextstate" with "action"
            - nextstate: int
                denotes the state we transition to (in range [0, nS - 1])
            - reward: int
                either 0 or 1, the reward for transitioning from "state" to
                "nextstate" with "action"
            - terminal: bool
              True when "nextstate" is a terminal state (hole or goal), False otherwise
    nS: int
        number of states in the environment
    nA: int
        number of actions in the environment
    gamma: float
        Discount factor. Number in range [0, 1)
"""


def p_to_tensor(P, nS, nA):

    # Construct P as tensor so it's easier to work with:
    P_tensor = np.zeros((nS,nA,4), dtype=float)
    for s in range(nS):
        for a in range(nA):
            P_tensor[s][a] = np.array(P[s][a][0][0:4])

    prob    = P_tensor[:,:,0]                       # Tensor: shape (nS, nA)
    s_next  = np.array(P_tensor[:,:,1]).astype(int) # Tensor: shape (nS, nA)
    r       = P_tensor[:,:,2]                       # Tensor: shape (nS, nA)

    return prob, s_next, r



def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-3):
    """Evaluate the value function from a given policy.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    policy: np.array[nS]
        The policy to evaluate. Maps states to actions.
    tol: float
        Terminate policy evaluation when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns
    -------
    value_function: np.ndarray[nS]
        The value function of the given policy, where value_function[s] is
        the value of state s
    """

    value_function = np.zeros(nS)
    ############################
    # YOUR IMPLEMENTATION HERE #


    # Vectorize so it's easier to work with
    (prob, s_next, r) = p_to_tensor(P, nS, nA) # Tensors: shape (nS, nA)

    V = value_function          # Vector: shape (nS,)
    V_new = V.copy()            # Vector: shape (nS,)

    # Given pi(a), create indices which produce
    # column vectors of shape (nS ,) from the matrices above
    take_indices = nA*np.arange(nS) + policy
    prob_pi     = np.take(prob, take_indices)
    s_next_pi   = np.take(s_next, take_indices)
    r_pi        = np.take(r, take_indices)

    while True:
        V_new = prob_pi * (r_pi + gamma * V[s_next_pi])
        if np.linalg.norm(V - V_new, ord=np.inf) < tol:
            break
        V = V_new.copy()
    
    value_function = V_new


    ############################
    return value_function


def policy_improvement(P, nS, nA, value_from_policy, policy, gamma=0.9):
    """Given the value function from policy improve the policy.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    value_from_policy: np.ndarray
        The value calculated from the policy
    policy: np.array
        The previous policy.

    Returns
    -------
    new_policy: np.ndarray[nS]
        An array of integers. Each integer is the optimal action to take
        in that state according to the environment dynamics and the
        given value function.
    """

    new_policy = np.zeros(nS, dtype='int')

    ############################
    # YOUR IMPLEMENTATION HERE #


    def randargmax(x, **kw):
        """argmax with random tiebreaking"""
        return np.argmax(np.random.random(x.shape) * (x==x.max()), **kw)

    # Vectorize so it's easier to work with
    (prob, s_next, r) = p_to_tensor(P, nS, nA) # Tensors: shape (nS, nA)

    V_pi = prob * (r + gamma * value_from_policy[s_next])
    new_policy = np.argmax(V_pi, axis=1) # Deterministic tiebreaking; lower s wins. 
    # new_policy = randargmax(V_pi, axis=1) # Random tiebreaking
    print(new_policy)


    ############################
    return new_policy


def policy_iteration(P, nS, nA, gamma=0.9, tol=10e-3):
    """Runs policy iteration.

    You should call the policy_evaluation() and policy_improvement() methods to
    implement this method.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    tol: float
        tol parameter used in policy_evaluation()
    Returns:
    ----------
    value_function: np.ndarray[nS]
    policy: np.ndarray[nS]
    """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)
    ############################
    # YOUR IMPLEMENTATION HERE #


    V = value_function # Set alias
    V = policy_evaluation(P, nS, nA, policy, gamma)

    while True:
        policy_new = policy_improvement(P, nS, nA, V, policy, gamma)
        V_new = policy_evaluation(P, nS, nA, policy_new, gamma)
        if np.array_equal(policy, policy_new): # policy stable
            break
        # print(policy_new)
        V = V_new.copy()
        policy = policy_new.copy()


    ############################
    return value_function, policy

def value_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """
    Learn value function and policy by using value iteration method for a given
    gamma and environment.

    Parameters:
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    tol: float
        Terminate value iteration when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns:
    ----------
    value_function: np.ndarray[nS]
    policy: np.ndarray[nS]
    """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)
    ############################
    # YOUR IMPLEMENTATION HERE #


    # Vectorize so it's easier to work with
    (prob, s_next, r) = p_to_tensor(P, nS, nA) # Tensors: shape (nS, nA)

    V = value_function
    while True:
        V_new = np.zeros(nS, dtype=float)
        Q = prob * (r + gamma * V[s_next]) #/ prob_total[:, np.newaxis]
        np.maximum(V_new, np.max(Q, axis=1), out=V_new) # Best V(s) is just best Q(s,a) among the actions available in each s
        if np.linalg.norm(V - V_new, ord=np.inf) < tol:
            break
        V = V_new.copy()
    policy = policy_improvement(P, nS, nA, V_new, policy, gamma)


    ############################
    return value_function, policy

def render_single(env, policy, max_steps=100):
  """
    This function does not need to be modified
    Renders policy once on environment. Watch your agent play!

    Parameters
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as
      attributes.
    Policy: np.array of shape [env.nS]
      The action to take at a given state
  """

  episode_reward = 0
  ob = env.reset()
  for t in range(max_steps):
    env.render()
    time.sleep(0.25)
    a = policy[ob]
    ob, rew, done, _ = env.step(a)
    episode_reward += rew
    if done:
      break
  env.render();
  if not done:
    print("The agent didn't reach a terminal state in {} steps.".format(max_steps))
  else:
      print("Episode reward: %f" % episode_reward)



# Edit below to run policy and value iteration on different environments and
# visualize the resulting policies in action!
# You may change the parameters in the functions below
if __name__ == "__main__":


    def run_n(env, policy, max_steps=100, iters=100):
        total_reward = 0
        for i in range(iters):
            episode_reward = 0
            ob = env.reset()
            for t in range(max_steps):
                a = policy[ob]
                ob, reward, done, _ = env.step(a)
                episode_reward += reward
                if done:
                    break
            total_reward += episode_reward
        print("iterations completed: " + str(iters))
        print(total_reward / iters)


    # comment/uncomment these lines to switch between deterministic/stochastic environments
    # env = gym.make("Deterministic-8x8-FrozenLake-v0")
    env = gym.make("Stochastic-4x4-FrozenLake-v0")

    print("\n" + "-"*25 + "\nBeginning Policy Iteration\n" + "-"*25)

    V_pi, p_pi = policy_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    # render_single(env, p_pi, 100)
    run_n(env, p_pi, 100, 100)

    print("\n" + "-"*25 + "\nBeginning Value Iteration\n" + "-"*25)

    V_vi, p_vi = value_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    # render_single(env, p_vi, 100)
    run_n(env, p_pi, 100, 100)

