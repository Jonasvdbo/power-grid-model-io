# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from power_grid_model.enum import WindingType
from pytest import mark

from power_grid_model_io.filters.phase_to_phase import get_clock, get_winding_from, get_winding_to, power_wind_speed


@mark.parametrize(
    "wind_speed,expected",
    [
        (0.0, 0.0),
        (1.5, 0.0),
        (3.0, 0.0),  # cut-in
        (8.5, 125000.0),
        (14.0, 1000000.0),  # nominal
        (19.5, 1000000.0),
        (25.0, 1000000.0),  # cutting-out
        (27.5, 500000.0),
        (30.0, 0.0),  # cut-out
        (100.0, 0.0),
    ],
)
def test_power_wind_speed(wind_speed, expected):
    assert power_wind_speed(p_nom=1e6, wind_speed_m_s=wind_speed) == expected


def test_get_winding_from():
    assert get_winding_from("Yy1") == WindingType.wye
    assert get_winding_from("Yyn2") == WindingType.wye
    assert get_winding_from("Yd3") == WindingType.wye
    assert get_winding_from("YNy4") == WindingType.wye_n
    assert get_winding_from("YNyn5") == WindingType.wye_n
    assert get_winding_from("YNd6") == WindingType.wye_n
    assert get_winding_from("Dy7") == WindingType.delta
    assert get_winding_from("Dyn8") == WindingType.delta
    assert get_winding_from("Dd9") == WindingType.delta
    with pytest.raises(ValueError):
        get_winding_from("XNd11")


def test_get_winding_to():
    assert get_winding_to("Yy1") == WindingType.wye
    assert get_winding_to("Yyn2") == WindingType.wye_n
    assert get_winding_to("Yd3") == WindingType.delta
    assert get_winding_to("YNy4") == WindingType.wye
    assert get_winding_to("YNyn5") == WindingType.wye_n
    assert get_winding_to("YNd6") == WindingType.delta
    assert get_winding_to("Dy7") == WindingType.wye
    assert get_winding_to("Dyn8") == WindingType.wye_n
    assert get_winding_to("Dd9") == WindingType.delta
    with pytest.raises(ValueError):
        get_winding_to("XNd11")


def test_get_clock():
    assert get_clock("YNd0") == 0
    assert get_clock("YNyn5") == 5
    assert get_clock("YNd12") == 12
    with pytest.raises(ValueError):
        get_clock("YNd-1")
    with pytest.raises(ValueError):
        get_clock("YNd13")
