"""Environment for training the acceleration behavior of vehicles in a ring."""

from flow.envs.ring.accel import AccelEnv
from flow.envs.base import Env

import numpy as np

class HighwayRampsZOVEnv(AccelEnv):

    def __init__(self, env_params, sim_params, network, simulator='traci'):
        super().__init__(env_params, sim_params, network, simulator)
        self.previous_lane = {}
        self.detected_vehichles = []
        self.detected_special_lane_vehichles = []

    def additional_command(self):
        """See parent class.

        Define which vehicles are observed for visualization purposes, and
        update the sorting of vehicles using the self.sorted_ids variable.
        """
        # if len(self.k.vehicle.get_controlled_ids()) > 0:
        #     for veh_id in self.k.vehicle.get_controlled_ids():
        #         veh_tpe = self.k.vehicle.get_type[veh_id]
                
        #         if (veh_tpe == "special_cav"):
        #             veh_acc = self.k.vehicle.get_acc_controller(veh_id)
        #             edg = self.k.vehicle.get_edge[veh_id]
        #             edg_tpe = self.k.network.get_edge_type(edg)
        #             if edg_tpe == "highway":
        #                 index = self.k.vehicle.get_lane[veh_id]
        #                 acc_params = self.k.network.network.net_params.additional_params["highway_zero_car_following"][str(index)]
        #                 veh_acc.T = acc_params["T"]
        #                 veh_acc.v0 = acc_params["v0"]
        #             else: 
        #                 acc_params = self.k.network.network.net_params.additional_params["ramps_zero_car_following"]
        #                 veh_acc.T = acc_params["T"]
        #                 veh_acc.v0 = acc_params["v0"]

        lane_change_counter = 0
        num_zov = 0
        num_new_detected = 0
        num_special = 0
        for veh_id in self.k.vehicle.get_ids():
            if veh_id in self.previous_lane.keys() and self.previous_lane[veh_id] != self.k.vehicle.get_lane(veh_id):
                lane_change_counter += 1
            
            #################################################### comment it for hov case and mixed case
            # car following change related to zov lanes 
            if self.k.vehicle.get_type(veh_id) == "special_cav" and self.k.network.network.zero_lanes == 1:
                if self.k.vehicle.get_lane(veh_id) != 3:
                    # change to cav params
                    self.k.vehicle.set_accel(veh_id, 2)
                    self.k.vehicle.set_decel(veh_id, 3.5)
                    self.k.vehicle.set_leaderDecel(veh_id, 3.5)
                    self.k.vehicle.set_tau(veh_id, 1.5)
                    self.k.vehicle.set_sigma(veh_id, 0.1)
                    # self.k.vehicle.set_min_gap(veh_id, 0)
                    self.k.vehicle.set_max_speed(veh_id, 31)
                    # ### test
                    # self.k.vehicle.set_accel(veh_id, 2)
                    # self.k.vehicle.set_decel(veh_id, 3.5)
                    # self.k.vehicle.set_tau(veh_id, 2)
                    # self.k.vehicle.set_sigma(veh_id, 0.5)
                    # self.k.vehicle.set_min_gap(veh_id, 1.5)
                    # self.k.vehicle.set_max_speed(veh_id, 31)
                elif self.k.vehicle.get_lane(veh_id) == 3:
                    # change to cav_zero params
                    self.k.vehicle.set_accel(veh_id, 7.6)
                    self.k.vehicle.set_decel(veh_id, 8)
                    self.k.vehicle.set_leaderDecel(veh_id, 8)
                    self.k.vehicle.set_sigma(veh_id, 0.1)
                    self.k.vehicle.set_tau(veh_id, 1)
                    # self.k.vehicle.set_min_gap(veh_id, 1)
                    self.k.vehicle.set_max_speed(veh_id, 40)
                # #### test
                #     self.k.vehicle.set_accel(veh_id, 2)
                #     self.k.vehicle.set_decel(veh_id, 3.5)
                #     self.k.vehicle.set_tau(veh_id, 2)
                #     self.k.vehicle.set_sigma(veh_id, 0.5)
                #     #self.k.vehicle.set_min_gap(veh_id, 1.5)
                #     self.k.vehicle.set_max_speed(veh_id, 31)    
                else: 
                    pass
                
            #########################################

            if self.k.vehicle.get_type(veh_id) == "special_cav":
                if self.k.vehicle.get_lane(veh_id) == 0:
                    self.k.vehicle.set_accel(veh_id, 2)
                    self.k.vehicle.set_decel(veh_id, 3.5)
                    self.k.vehicle.set_leaderDecel(veh_id, 3.5)
                    self.k.vehicle.set_tau(veh_id, 1.5)
                    self.k.vehicle.set_sigma(veh_id, 0.1)
                    # self.k.vehicle.set_min_gap(veh_id, 0)
                    self.k.vehicle.set_max_speed(veh_id, 31)
            #########################################

            if self.k.vehicle.get_edge(veh_id)[:7] == "highway" and self.k.vehicle.get_lane(veh_id) == 3:
                num_zov += 1

            if self.k.vehicle.get_edge(veh_id) == "highway_3" and self.k.vehicle.get_position(veh_id) > 100:
                if veh_id not in self.detected_vehichles:
                    num_new_detected += 1
                    self.detected_vehichles.append(veh_id)
                    if self.k.vehicle.get_lane(veh_id) == 3:
                        num_special += 1
                        self.detected_special_lane_vehichles.append(veh_id)
            
            self.previous_lane[veh_id] = self.k.vehicle.get_lane(veh_id)


        self.k.vehicle.for_crystal["num_lane_change"] += lane_change_counter
        self.k.vehicle.for_crystal["num_zov_on_zov_lane"] = num_zov
        self.k.vehicle.for_crystal["special_lane_throughput"] = len(self.detected_special_lane_vehichles)
        self.k.vehicle.for_crystal["throughput"] = len(self.detected_vehichles)
        # print("--------------------------")
        # print("step: %d" % self.step_counter)
        # print("new lane changes: %d" %lane_change_counter)
        # print("num of vehicles on zov lane : %d" % num_zov)
        # print("newly detected vehicles: %d" %num_new_detected)
        # print("total detected: %d" %len(self.detected_vehichles))

    
    def reset(self):
        self.previous_lane = {}
        self.detected_vehichles = []
        self.detected_special_lane_vehichles = []
        return super().reset()

    def step(self, rl_actions):
        """Advance the environment by one step.

        Assigns actions to autonomous and human-driven agents (i.e. vehicles,
        traffic lights, etc...). Actions that are not assigned are left to the
        control of the simulator. The actions are then used to advance the
        simulator by the number of time steps requested per environment step.

        Results from the simulations are processed through various classes,
        such as the Vehicle and TrafficLight kernels, to produce standardized
        methods for identifying specific network state features. Finally,
        results from the simulator are used to generate appropriate
        observations.

        Parameters
        ----------
        rl_actions : array_like
            an list of actions provided by the rl algorithm

        Returns
        -------
        observation : array_like
            agent's observation of the current environment
        reward : float
            amount of reward associated with the previous state/action pair
        done : bool
            indicates whether the episode has ended
        info : dict
            contains other diagnostic information from the previous action
        """
        for _ in range(self.env_params.sims_per_step):
            self.time_counter += 1
            self.step_counter += 1

            # perform acceleration actions for controlled human-driven vehicles
            if len(self.k.vehicle.get_controlled_ids()) > 0:
                accel = []
                for veh_id in self.k.vehicle.get_controlled_ids():
                    action = self.k.vehicle.get_acc_controller(
                        veh_id).get_action(self)
                    accel.append(action)
                self.k.vehicle.apply_acceleration(
                    self.k.vehicle.get_controlled_ids(), accel)

            # perform lane change actions for controlled human-driven vehicles
            if len(self.k.vehicle.get_controlled_lc_ids()) > 0:
                direction = []
                for veh_id in self.k.vehicle.get_controlled_lc_ids():
                    target_lane = self.k.vehicle.get_lane_changing_controller(
                        veh_id).get_action(self)
                    direction.append(target_lane)
                self.k.vehicle.apply_lane_change(
                    self.k.vehicle.get_controlled_lc_ids(),
                    direction=direction)

            # perform (optionally) routing actions for all vehicles in the
            # network, including RL and SUMO-controlled vehicles
            routing_ids = []
            routing_actions = []
            for veh_id in self.k.vehicle.get_ids():
                if self.k.vehicle.get_routing_controller(veh_id) \
                        is not None:
                    routing_ids.append(veh_id)
                    route_contr = self.k.vehicle.get_routing_controller(
                        veh_id)
                    routing_actions.append(route_contr.choose_route(self))

            self.k.vehicle.choose_routes(routing_ids, routing_actions)

            self.apply_rl_actions(rl_actions)

            self.additional_command()

            # advance the simulation in the simulator by one step
            self.k.simulation.simulation_step()

            # store new observations in the vehicles and traffic lights class
            self.k.update(reset=False)

            # update the colors of vehicles
            if self.sim_params.render:
                self.k.vehicle.update_vehicle_colors()

            # crash encodes whether the simulator experienced a collision
            # crash = self.k.simulation.check_collision()
            crash = False
            
            # stop collecting new simulation steps if there is a collision
            if crash:
                break

            # render a frame
            self.render()

        states = self.get_state()

        # collect information of the state of the network based on the
        # environment class used
        self.state = np.asarray(states).T

        # collect observation new state associated with action
        next_observation = np.copy(states)

        # test if the environment should terminate due to a collision or the
        # time horizon being met
        done = (self.time_counter >= self.env_params.sims_per_step *
                (self.env_params.warmup_steps + self.env_params.horizon)
                or crash)

        # compute the info for each agent
        infos = {}

        # compute the reward
        if self.env_params.clip_actions:
            rl_clipped = self.clip_actions(rl_actions)
            reward = self.compute_reward(rl_clipped, fail=crash)
        else:
            reward = self.compute_reward(rl_actions, fail=crash)

        return next_observation, reward, done, infos