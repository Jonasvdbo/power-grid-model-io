# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Unit mapping helper class
"""

from typing import Dict, Optional, Set, Tuple

import structlog

#            si-unit   unit factor
Units = Dict[str, Optional[Dict[str, float]]]


class UnitMapping:
    """
    Unit mapping helper class.
    The input data is expected to be of the form:
    {
        "A" : None,
        "W": {
            "kW": 1000.0,
            "MW": 1000000.0
        }
     }
    """

    def __init__(self, mapping: Optional[Units] = None):
        self._log = structlog.get_logger(type(self).__name__)
        self._si_units: Set[str] = set()
        self._mapping: Dict[str, Tuple[float, str]] = {}
        self.set_mapping(mapping=mapping if mapping is not None else {})

    def set_mapping(self, mapping: Units):
        """
        Creates an internal mapping lookup table based on input data of the form:
        mapping = {
            "A" : None,
            "W": {
                "kW": 1000.0,
                "MW": 1000000.0
            }
         }
        """
        self._si_units = set(mapping.keys())
        self._mapping = {}
        for si_unit, multipliers in mapping.items():
            if not multipliers:
                continue
            for unit, multiplier in multipliers.items():
                if unit in self._mapping:
                    multiplier_, si_unit_ = self._mapping[unit]
                    raise ValueError(
                        f"Multiple unit definitions for '{unit}': "
                        f"1{unit} = {multiplier_}{si_unit_} = {multiplier}{si_unit}"
                    )
                self._mapping[unit] = (multiplier, si_unit)
                if unit == si_unit:
                    if multiplier != 1.0:
                        raise ValueError(
                            f"Invalid unit definition for '{unit}': 1{unit} cannot be {multiplier}{si_unit}"
                        )
                    continue
                self._mapping[unit] = (multiplier, si_unit)
        self._log.debug(
            "Set unit definitions", n_units=len(self._si_units | self._mapping.keys()), n_si_units=len(self._si_units)
        )

    def get_unit_multiplier(self, unit: str) -> Tuple[float, str]:
        """
        Find the correct unit multiplier and the corresponding SI unit
        """
        return (1.0, unit) if unit in self._si_units else self._mapping[unit]
