"""Example of a highway section network with on/off ramps."""

from flow.envs.highway_ramps_env import HighwayRampsEnv
from flow.envs.multiagent import highway
from flow.controllers import car_following_models
from flow.controllers.car_following_models import IDMController, LACController
from flow.core.params import SumoParams, EnvParams, NetParams, InitialConfig
from flow.core.params import SumoCarFollowingParams, SumoLaneChangeParams
from flow.core.params import InFlows, VehicleParams, TrafficLightParams
from flow.networks.highway_ramps_crystal import ADDITIONAL_NET_PARAMS
from flow.envs.ring.accel import AccelEnv, ADDITIONAL_ENV_PARAMS
from flow.networks import HighwayRampsNetwork_Crystal

# inflow rates in vehs/hour
HIGHWAY_INFLOW_RATE = 3000
ON_RAMPS_INFLOW_RATE = 1000
CAV_RATE = 0.5
ZERO_RATE = 0.5

vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    # acceleration_controller=(IDMController, {"T":1, "v0":25}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="no_collide",  # for safer behavior at the merges
        tau=1.5  # larger distance between cars
    ),
    lane_change_params=SumoLaneChangeParams(lane_change_mode=1621),
    color = "white"
)

vehicles.add(
    veh_id="cav_zero",
    # acceleration_controller=(LACController, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="obey_safe_speed",  # for safer behavior at the merges
        tau=1.5  # larger distance between cars
    ),
    lane_change_params=SumoLaneChangeParams(lane_change_mode=1621),
    vClass="hov",
    color = "red"
)

vehicles.add(
    veh_id="cav",
    # acceleration_controller=(LACController, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="no_collide",  # for safer behavior at the merges
        tau=1.5  # larger distance between cars
    ),
    lane_change_params=SumoLaneChangeParams(lane_change_mode=1621),
    # vClass="hov",
    color = "yellow"
)


additional_net_params = ADDITIONAL_NET_PARAMS.copy()

# lengths
additional_net_params["highway_length"] = 8000
additional_net_params["on_ramps_length"] = 300
additional_net_params["off_ramps_length"] = 300

# number of lanes
additional_net_params["highway_lanes"] = 4
additional_net_params["on_ramps_lanes"] = 1
additional_net_params["off_ramps_lanes"] = 1

# speed limits
additional_net_params["highway_speed"] = 30
additional_net_params["on_ramps_speed"] = 20
additional_net_params["off_ramps_speed"] = 20

# ramps
additional_net_params["on_ramps_pos"] = [500, 3000, 5500]
additional_net_params["off_ramps_pos"] = [2500, 5000, 7500]

# probability of exiting at the next off-ramp
additional_net_params["next_off_ramp_proba"] = 0.25

# zero-occupancy lane
additional_net_params["zero_lanes"] = 1
assert additional_net_params["zero_lanes"]<additional_net_params["highway_lanes"]
additional_net_params["highway_zero_car_following"] = dict()
for i in range(additional_net_params["highway_lanes"]):
    if i < additional_net_params["highway_lanes"] - additional_net_params["zero_lanes"]:
        additional_net_params["highway_zero_car_following"][str(i)] = {"T": 1, "v0": 20}
    else:
        additional_net_params["highway_zero_car_following"][str(i)] = {"T": 0.5, "v0": 40}
additional_net_params["ramps_zero_car_following"] = {"T": 1, "v0": 20}
# additional_net_params["allow"] = dict()
# for i in range(additional_net_params["highway_lanes"]):
#     if i < additional_net_params["zero_occupancy_lanes"]:
#         additional_net_params["allow"][str(i)] = "cav_zero"
#     else:
#         additional_net_params["allow"][str(i)] = "all"

inflows = InFlows()
inflows.add(
    veh_type="human",
    edge="highway_0",
    vehs_per_hour=(1-CAV_RATE)*HIGHWAY_INFLOW_RATE,
    depart_lane="allowed",
    depart_speed="max",
    name="highway_human")
inflows.add(
    veh_type="cav",
    edge="highway_0",
    vehs_per_hour=CAV_RATE*(1-ZERO_RATE)*HIGHWAY_INFLOW_RATE,
    depart_lane="allowed",
    depart_speed="max",
    name="highway_cav")
inflows.add(
    veh_type="cav_zero",
    edge="highway_0",
    vehs_per_hour=CAV_RATE*ZERO_RATE*HIGHWAY_INFLOW_RATE,
    depart_lane="allowed",
    depart_speed="max",
    name="highway_zero")
for i in range(len(additional_net_params["on_ramps_pos"])):
    inflows.add(
        veh_type="human",
        edge="on_ramp_{}".format(i),
        vehs_per_hour=(1-CAV_RATE)*ON_RAMPS_INFLOW_RATE,
        depart_lane="first",
        depart_speed="max",
        name="on_ramp_human")
    inflows.add(
        veh_type="cav",
        edge="on_ramp_{}".format(i),
        vehs_per_hour=CAV_RATE*(1-ZERO_RATE)*ON_RAMPS_INFLOW_RATE,
        depart_lane="first",
        depart_speed="max",
        name="on_ramp_cav")
    inflows.add(
        veh_type="cav_zero",
        edge="on_ramp_{}".format(i),
        vehs_per_hour=CAV_RATE*ZERO_RATE*ON_RAMPS_INFLOW_RATE,
        depart_lane="first",
        depart_speed="max",
        name="on_ramp_zero")


flow_params = dict(
    # name of the experiment
    exp_tag='highway-ramp',

    # name of the flow environment the experiment is running on
    env_name=HighwayRampsEnv,

    # name of the network class the experiment is running on
    network=HighwayRampsNetwork_Crystal,

    # simulator that is used by the experiment
    simulator='traci',

    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(
        render=True,
        emission_path="./data/",
        sim_step=0.1,
        restart_instance=True,
        minigap_factor = 0

    ),

    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        additional_params=ADDITIONAL_ENV_PARAMS,
        horizon=36000,
        sims_per_step=1,
        warmup_steps=0
    ),

    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    net=NetParams(
        inflows=inflows,
        additional_params=additional_net_params
    ),

    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.params.VehicleParams)
    veh=vehicles,

    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(),

    # traffic lights to be introduced to specific nodes (see
    # flow.core.params.TrafficLightParams)
    tls=TrafficLightParams(),
)
