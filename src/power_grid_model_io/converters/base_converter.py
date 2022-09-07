# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod
from typing import Generic, Optional, Tuple, TypeVar

import structlog
from power_grid_model.data_types import Dataset, SingleDataset

from power_grid_model_io.data_stores.base_data_store import BaseDataStore
from power_grid_model_io.data_types import ExtraInfoLookup

DataType = TypeVar("DataType")


class BaseConverter(Generic[DataType], ABC):
    def __init__(self):
        self._log = structlog.get_logger(type(self).__name__)

    def load_input_data(self, store: BaseDataStore[DataType]) -> Tuple[SingleDataset, ExtraInfoLookup]:
        extra_info: ExtraInfoLookup = {}
        data = self._parse_data(data=store.load(), data_type="input", extra_info=extra_info)
        if isinstance(data, list):
            raise TypeError("Input data can not be batch data")
        return data, extra_info

    def load_update_data(self, store: BaseDataStore[DataType]) -> Dataset:
        return self._parse_data(data=store.load(), data_type="update")

    def load_sym_output_data(self, store: BaseDataStore[DataType]) -> Dataset:
        return self._parse_data(data=store.load(), data_type="sym_output")

    def load_asym_output_data(self, store: BaseDataStore[DataType]) -> Dataset:
        return self._parse_data(data=store.load(), data_type="asym_output")

    def save_data(self, store: BaseDataStore[DataType], data: Dataset, extra_info: Optional[ExtraInfoLookup] = None):
        store.save(data=self._serialize_data(data=data, extra_info=extra_info))

    @abstractmethod  # pragma: nocover
    def _parse_data(self, data: DataType, data_type: str, extra_info: Optional[ExtraInfoLookup] = None) -> Dataset:
        pass

    @abstractmethod  # pragma: nocover
    def _serialize_data(self, data: Dataset, extra_info: Optional[ExtraInfoLookup] = None) -> DataType:
        pass
