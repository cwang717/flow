"""Environment for training the acceleration behavior of vehicles in a ring."""

from flow.core import rewards
from flow.envs.base import Env

from gym.spaces.box import Box

import numpy as np

ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration for autonomous vehicles, in m/s^2
    'max_accel': 1,
    # maximum deceleration for autonomous vehicles, in m/s^2
    'max_decel': 1
}


class MinicityAttackPOEnv(Env):
    """Partial observed acceleration environment.
    """

    def __init__(self, env_params, sim_params, network, simulator='traci'):
        from flow.controllers.car_following_models import IDMController
        from flow.core.params import SumoCarFollowingParams
        for p in ADDITIONAL_ENV_PARAMS.keys():
            if p not in env_params.additional_params:
                raise KeyError(
                    'Environment parameter \'{}\' not supplied'.format(p))

        super().__init__(env_params, sim_params, network, simulator)
        self.idm = IDMController("idm_ref", car_following_params=SumoCarFollowingParams())

    @property
    def action_space(self):
        """See class definition."""
        return Box(
            low=-np.abs(self.env_params.additional_params['max_decel']),
            high=self.env_params.additional_params['max_accel'],
            shape=(self.initial_vehicles.num_rl_vehicles, ),
            dtype=np.float32)

    @property
    def observation_space(self):
        """See class definition."""
        return Box(low=-float('inf'), high=float('inf'),
                   shape=(4, ), dtype=np.float32)

    def _apply_rl_actions(self, rl_actions):
        """See class definition."""
        self.k.vehicle.apply_acceleration(
            self.k.vehicle.get_rl_ids(), rl_actions)

    def get_state(self):
        """See class definition."""
        rl_id = self.k.vehicle.get_rl_ids()[0]
        lead_id = self.k.vehicle.get_leader(rl_id) or rl_id

        # normalizers
        max_speed = 15.
        max_headway = 1e3

        observation = np.array([
            self.k.vehicle.get_speed(rl_id) / max_speed,
            (self.k.vehicle.get_speed(lead_id) -
             self.k.vehicle.get_speed(rl_id)) / max_speed,
            self.k.vehicle.get_headway(rl_id) / max_headway,
            self.k.vehicle.get_follower_headway(rl_id) / max_headway
        ])

        return observation

    def compute_reward(self, rl_actions, **kwargs):
        """See class definition."""
        # in the warmup steps
        if rl_actions is None:
            return 0
        vel = np.array([
            self.k.vehicle.get_speed(veh_id)
            for veh_id in self.k.vehicle.get_ids()
        ])

        if any(vel < -100) or kwargs['fail']:
            return -10000

        # panalize average velocity
        eta_2 = 4.
        reward = -eta_2 * np.mean(vel) / 20

        # reward similar acceleration with IDM model

        eta = 1
        difference_threshold = 0.2
        
        idm_actions = []
        for veh_id in self.k.vehicle.get_rl_ids():
            self.idm.veh_id = veh_id
            idm_actions.append(self.idm.get_accel(self))
        mean_difference = np.mean(np.abs(np.array(idm_actions)-np.array(rl_actions)))
        reward -= eta * mean_difference

        return float(reward)

    def additional_command(self):
        """Define which vehicles are observed for visualization purposes."""
        # specify observed vehicles
        rl_id = self.k.vehicle.get_rl_ids()[0]
        lead_id = self.k.vehicle.get_leader(rl_id) or rl_id
        self.k.vehicle.set_observed(lead_id)

    def reset(self):
        """See parent class.
        """
        print('\n-----------------------')
        print('resetting')
        print('-----------------------')

        return super().reset()