"""Environment for training the acceleration behavior of vehicles in a ring."""

from flow.envs.ring.accel import AccelEnv
from flow.envs.base import Env

import numpy as np

class HighwayRampsEnv(AccelEnv):

    def __init__(self, env_params, sim_params, network, simulator='traci'):
        super().__init__(env_params, sim_params, network, simulator)
        self.previous_lane = {}
        self.detected_vehichles = []

    def additional_command(self):
        """See parent class.

        Define which vehicles are observed for visualization purposes, and
        update the sorting of vehicles using the self.sorted_ids variable.
        """
        if len(self.k.vehicle.get_controlled_ids()) > 0:
            for veh_id in self.k.vehicle.get_controlled_ids():
                veh_tpe = self.k.vehicle.get_type[veh_id]
                
                if (veh_tpe == "cav_zero"):
                    veh_acc = self.k.vehicle.get_acc_controller(veh_id)
                    edg = self.k.vehicle.get_edge[veh_id]
                    edg_tpe = self.k.network.get_edge_type(edg)
                    if edg_tpe == "highway":
                        index = self.k.vehicle.get_lane[veh_id]
                        acc_params = self.k.network.network.net_params.additional_params["highway_zero_car_following"][str(index)]
                        veh_acc.T = acc_params["T"]
                        veh_acc.v0 = acc_params["v0"]
                    else: 
                        acc_params = self.k.network.network.net_params.additional_params["ramps_zero_car_following"]
                        veh_acc.T = acc_params["T"]
                        veh_acc.v0 = acc_params["v0"]

        lane_change_counter = 0
        num_zov = 0
        num_new_detected = 0
        for veh_id in self.k.vehicle.get_ids():
            if veh_id in self.previous_lane.keys() and self.previous_lane[veh_id] != self.k.vehicle.get_lane(veh_id):
                lane_change_counter += 1

            if self.k.vehicle.get_edge(veh_id)[:7] == "highway" and self.k.vehicle.get_lane(veh_id) == 3:
                num_zov += 1

            if self.k.vehicle.get_edge(veh_id) == "highway_3" and self.k.vehicle.get_position(veh_id) > 100:
                if veh_id not in self.detected_vehichles:
                    num_new_detected += 1
                    self.detected_vehichles.append(veh_id)
            
            self.previous_lane[veh_id] = self.k.vehicle.get_lane(veh_id)
        
        print("--------------------------")
        print("step: %d" % self.step_counter)
        print("new lane changes: %d" %lane_change_counter)
        print("num of vehicles on zov lane : %d" % num_zov)
        print("newly detected vehicles: %d" %num_new_detected)
        print("total detected: %d" %len(self.detected_vehichles))

    
    def reset(self):
        self.previous_lane = {}
        self.detected_vehichles = []
        return super().reset()