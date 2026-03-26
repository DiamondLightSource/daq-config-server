import xmltodict
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.xpdf_parameters import (
    TemperatureControllerParams,
    TemperatureControllersConfig,
)


def test_xml_can_be_read():
    with open(TestDataPaths.TEST_I15_1_XPDF_LOCAL_PARAMETERS) as f:
        contents = f.read()
    result = xmltodict.parse(contents)
    expected = {
        "configuration": {
            "detectors": {
                "pe1": {
                    "stopBetweenPoints": "true",
                    "calibrationFilePath": "/dls/i15-1/data/2022/cm31137-2/processed/"
                    + "cal/cal_i15-1-52506_pe1AD.nxs",
                },
                "pe2": {
                    "stopBetweenPoints": "true",
                    "calibrationFilePath": "/dls/i15-1/data/2026/cm44163-1/processed/"
                    + "cal/cal_i15-1-94989_pe2AD.nxs",
                },
                "arc": {
                    "calibrationFilePath": "/dls_sw/i15-1/scripts/notebooks/"
                    + "arc_cal_2024-10-16_12-58-17_z_out_out_out_out_out.json",
                    "flat": ["arc_fake_flat_1s.nxs", "/entry/flat/flat"],
                    "mask": ["arc_basic_mask.nxs", "/entry/mask/mask"],
                },
            },
            "i0": {"normalise_to": "1.0"},
            "devices": {
                "cobra": {
                    "settle_time": "600",
                    "tolerance": "5.0",
                    "units": "K",
                    "ramp_units": "/h",
                    "move_in_position": "0.",
                    "move_out_position": "-100.",
                    "safe_position": "2.0",
                    "beam_position": "461.5",
                    "calibration_file": "cobra_calibration_2025-09-11.txt",
                    "use_calibration": "true",
                    "use_fast_cool": "true",
                },
                "blower": {
                    "settle_time": "0",
                    "tolerance": "5.0",
                    "units": "C",
                    "ramp_units": "/min",
                    "move_in_position": "30.",
                    "move_out_position": "0.1",
                    "beam_position": "44.7",
                    "safe_position": "2.0",
                    "use_calibration": "true",
                    "calibration_file": "blower_cal_10_03_2026.txt",
                },
                "cryostream": {
                    "beam_position": "469.9",
                    "safe_position": "0",
                    "ramp_units": "/h",
                    "units": "K",
                    "tolerance": "0.5",
                    "settle_time": "600",
                    "calibration_file": "cryostream_cal_2025-01-23.txt",
                    "use_calibration": "true",
                },
                "linkam": {
                    "tolerance": "1.0",
                    "units": "C",
                    "settle_time": "180",
                    "ramp_units": "/min",
                },
                "helix": {
                    "dean": "34",
                    "ramp_units": "/h",
                    "units": "K",
                    "settle_time": "120",
                    "use_fast_cool": "false",
                    "tolerance": "0.1",
                },
            },
            "positions": {
                "envX": {"out_test": "0"},
                "blowerY": {"out_test": "10"},
                "H": {"in_test": {"hx": "0", "hz": "0"}},
            },
        }
    }
    assert result == expected


def test_robot_load_devices_config_model():
    with open(TestDataPaths.TEST_I15_1_XPDF_LOCAL_PARAMETERS) as f:
        contents = f.read()
    result = TemperatureControllersConfig.from_xpdf_parameters(contents)
    assert result == TemperatureControllersConfig(
        cobra=TemperatureControllerParams(
            beam_position=461.5,
            safe_position=2.0,
            settle_time=600,
            tolerance=5.0,
            units="K",
            ramp_units="/h",
            use_calibration=True,
            use_fast_cool=True,
            calibration_file="cobra_calibration_2025-09-11.txt",
        ),
        blower=TemperatureControllerParams(
            beam_position=44.7,
            safe_position=2.0,
            settle_time=0,
            tolerance=5.0,
            units="C",
            ramp_units="/min",
            use_calibration=True,
            use_fast_cool=None,
            calibration_file="blower_cal_10_03_2026.txt",
        ),
    )
