# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
These functions can be used in the mapping files to apply functions to vision data
"""

import math
import re
from typing import Tuple

from power_grid_model import WindingType

CONNECTION_PATTERN = re.compile(r"(Y|YN|D|Z|ZN)(y|yn|d|z|zn)(\d|1[0-2])")

"""
TODO: Implement Z winding
"""
WINDING_TYPES = {
    "Y": WindingType.wye,
    "YN": WindingType.wye_n,
    "D": WindingType.delta,
    "Z": WindingType.wye,
    "ZN": WindingType.wye_n,
}


def relative_no_load_current(i: float, p: float, s_nom: float, u_nom: float) -> float:
    """
    TODO: description
    """
    return i / (s_nom / u_nom / math.sqrt(3)) if i > p / s_nom else p / s_nom


def reactive_power_calculation(pref: float, cosphi: float, scale: float) -> float:
    """
    Calculate the reactive power, based on Pref, cosine Phy and a scaling factor.
    """
    return scale * pref * math.sqrt((1 - math.pow(cosphi, 2) / cosphi))


def power_wind_speed(  # pylint: disable=too-many-arguments
    p_nom: float,
    wind_speed_m_s: float,
    cut_in_wind_speed_m_s: float = 3.0,
    nominal_wind_speed_m_s: float = 14.0,
    cutting_out_wind_speed_m_s: float = 25.0,
    cut_out_wind_speed_m_s: float = 30.0,
) -> float:
    """
    Estimate p_ref based on p_nom and wind_speed.

    See section "Wind turbine" in https://phasetophase.nl/pdf/VisionEN.pdf
    """

    # At a wind speed below cut-in, the power is zero.
    if wind_speed_m_s < cut_in_wind_speed_m_s:
        return 0.0

    # At a wind speed between cut-in and nominal, the power is a third power function of the wind speed.
    if wind_speed_m_s < nominal_wind_speed_m_s:
        factor = wind_speed_m_s - cut_in_wind_speed_m_s
        max_factor = nominal_wind_speed_m_s - cut_in_wind_speed_m_s
        return ((factor / max_factor) ** 3) * p_nom

    # At a wind speed between nominal and cutting-out, the power is the nominal power.
    if wind_speed_m_s < cutting_out_wind_speed_m_s:
        return p_nom

    # At a wind speed between cutting-out and cut-out, the power decreases from nominal to zero.
    if wind_speed_m_s < cut_out_wind_speed_m_s:
        factor = wind_speed_m_s - cutting_out_wind_speed_m_s
        max_factor = cut_out_wind_speed_m_s - cutting_out_wind_speed_m_s
        return (1.0 - factor / max_factor) * p_nom

    # Above cut-out speed, the power is zero.
    return 0.0


def get_winding_from(conn_str: str, neutral_grounding: bool = True) -> WindingType:
    """
    Get the winding type, based on a textual encoding of the conn_str
    TODO: use z winding when zigzag is implemented
    """
    wfr, wto, clock = _split_connection_string(conn_str)
    winding = WINDING_TYPES[wfr]
    if winding == WindingType.wye_n and not neutral_grounding:
        winding = WindingType.wye
    if wfr[0] == "Z" and wto != "d" and clock % 2:
        winding = WindingType.delta
    return winding


def get_winding_to(conn_str: str, neutral_grounding: bool = True) -> WindingType:
    """
    Get the winding type, based on a textual encoding of the conn_str
    TODO: use z winding when zigzag is implemented
    """
    wfr, wto, clock = _split_connection_string(conn_str)
    winding = WINDING_TYPES[wto.upper()]
    if winding == WindingType.wye_n and not neutral_grounding:
        winding = WindingType.wye
    if wfr != "D" and wto[0] == "z" and clock % 2:
        winding = WindingType.delta
    return winding


def get_clock(conn_str: str) -> int:
    """
    Extract the clock part of the conn_str
    """
    _, _, clock = _split_connection_string(conn_str)
    return clock


def _split_connection_string(conn_str: str) -> Tuple[str, str, int]:
    """
    Helper function to split the conn_str into three parts:
     * winding_from
     * winding_to
     * clock
    """
    match = CONNECTION_PATTERN.fullmatch(conn_str)
    if not match:
        raise ValueError(f"Invalid transformer connection string: '{conn_str}'")
    return match.group(1), match.group(2), int(match.group(3))
