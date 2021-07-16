"""Used as an example of ring experiment.

This example consists of 22 IDM cars on a ring creating shockwaves.
"""

from flow.envs.ring.wave_attenuation import WaveAttenuationEnv, WaveAttenuationPOEnv
from flow.controllers import IDMController, ContinuousRouter, TrainedSingleRingController, TrainedRingAttackerController
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, SumoCarFollowingParams
from flow.envs.ring.accel import AccelEnv, ADDITIONAL_ENV_PARAMS
from flow.networks.ring import RingNetwork, ADDITIONAL_NET_PARAMS


vehicles = VehicleParams()
vehicles.add(
    veh_id="idm",
    acceleration_controller=(IDMController, {
        "noise": 0.08
    }),
    car_following_params=SumoCarFollowingParams(
        min_gap=0
    ),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=21)
# vehicles.add(
#     veh_id="good",
#     acceleration_controller=(TrainedSingleRingController, {}),
#     car_following_params=SumoCarFollowingParams(
#         min_gap=0,
#         speed_mode="all_checks"
#     ),
#     routing_controller=(ContinuousRouter, {}),
#     num_vehicles=1,
#     color="green")
vehicles.add(
    veh_id="attacker",
    acceleration_controller=(TrainedRingAttackerController, {}),
    car_following_params=SumoCarFollowingParams(
        min_gap=0,
        speed_mode="all_checks"
    ),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=1,
    color="red")


flow_params = dict(
    # name of the experiment
    exp_tag='ring',

    # name of the flow environment the experiment is running on
    env_name=WaveAttenuationEnv,

    # name of the network class the experiment is running on
    network=RingNetwork,

    # simulator that is used by the experiment
    simulator='traci',

    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(
        render=True,
        sim_step=0.1,
        emission_path="/home/cwang717/git/flow/output/scenario_2"
    ),

    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        horizon=10000,
        warmup_steps=0,
        #additional_params=ADDITIONAL_ENV_PARAMS,
        additional_params={
            "max_accel": 1,
            "max_decel": 1,
            "ring_length": [220, 220],
        },
    ),

    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    # net=NetParams(
    #     additional_params=ADDITIONAL_NET_PARAMS.copy(),
    # ),
    net=NetParams(
        additional_params={
            "length": 520,
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
        # bunching=20,
    ),
)
