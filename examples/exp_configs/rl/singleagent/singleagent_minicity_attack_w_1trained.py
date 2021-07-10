"""Ring road example.

Trains a single autonomous vehicle to stabilize the flow of 21 human-driven
vehicles in a variable length ring road.
"""
from flow.networks.minicity import MiniCityNetwork
from flow.controllers.routing_controllers import MinicityRouter
from flow.core.params import SumoLaneChangeParams, SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, SumoCarFollowingParams
from flow.controllers import RLController, IDMController, ContinuousRouter, TrainedMinicityController
from flow.envs import MinicityAttackPOEnv_three
from flow.networks import RingNetwork

# time horizon of a single rollout
HORIZON = 3000
# number of rollouts per training iteration
N_ROLLOUTS = 20
# number of parallel workers
N_CPUS = 2

# We place one autonomous vehicle and 99 human-driven vehicles in the network
vehicles = VehicleParams()
vehicles.add(
    veh_id="idm",
    acceleration_controller=(IDMController, {}),
    routing_controller=(MinicityRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode=1,
        tau=1.5  # larger distance between cars
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode="no_lc_safe",
    ),
    initial_speed=0,
    num_vehicles=98)
vehicles.add(
    veh_id="trained",
    acceleration_controller=(TrainedMinicityController, {}),
    car_following_params=SumoCarFollowingParams(
        min_gap=0,
        speed_mode="all_checks"
    ),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=1)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    routing_controller=(MinicityRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="obey_safe_speed",
    ),
    initial_speed=0,
    num_vehicles=1)

flow_params = dict(
    # name of the experiment
    exp_tag="singleagent_minicity_attack_w_1trained",

    # name of the flow environment the experiment is running on
    env_name=MinicityAttackPOEnv_three,

    # name of the network class the experiment is running on
    network=MiniCityNetwork,

    # simulator that is used by the experiment
    simulator='traci',

    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(
        sim_step=0.1,
        render=False,
        restart_instance=True
    ),

    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        horizon=HORIZON,
        warmup_steps=750,
        clip_actions=False,
        additional_params={
            "max_accel": 1,
            "max_decel": 1
        },
    ),

    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    net=NetParams(
        additional_params={
            "length": 260,
            "lanes": 1,
            "speed_limit": 30,
            "resolution": 40,
        }, ),

    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.params.VehicleParams)
    veh=vehicles,

    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(
        shuffle=True,
        spacing="random",
        min_gap=5,
    ),
)
