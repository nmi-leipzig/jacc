import json
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class FPGAModel:

    mmcm_f_in_min: float
    mmcm_f_in_max: float
    mmcm_f_out_min: float
    mmcm_f_out_max: float
    mmcm_f_vco_min: float
    mmcm_f_vco_max: float
    mmcm_f_pfd_min: float
    mmcm_f_pfd_max: float

    pll_f_in_min: float
    pll_f_in_max: float
    pll_f_out_min: float
    pll_f_out_max: float
    pll_f_vco_min: float
    pll_f_vco_max: float
    pll_f_pfd_min: float
    pll_f_pfd_max: float

    model_name: str
    speed_grades: list
    voltage: str = None

    @classmethod
    def from_json(cls, json_path):
        try:
            with open(json_path) as file:
                return cls(**json.load(file))
        except FileNotFoundError:
            print(f"Error while loading FPGAModel from json, \"{json_path}\" was not found", file=sys.stderr)
        except json.decoder.JSONDecodeError:
            print(f"Error while loading FPGAModel from json, \"{json_path}\" contains invalid syntax", file=sys.stderr)

    def get_identifier(self):
        if self.voltage is None:
            return [(self.model_name, speed_grade) for speed_grade in self.speed_grades]
        else:
            return [(self.model_name, speed_grade, self.voltage) for speed_grade in self.speed_grades]

    def validate_mmcm_input_frequency(self, frequency: float):
        return self.mmcm_f_in_min <= frequency <= self.mmcm_f_in_max

    def validate_mmcm_out_frequency(self, frequency: float):
        return self.mmcm_f_out_min <= frequency <= self.mmcm_f_out_max

    def validate_pll_input_frequency(self, frequency: float):
        return self.pll_f_in_min <= frequency <= self.pll_f_in_max

    def validate_pll_out_frequency(self, frequency: float):
        return self.pll_f_out_min <= frequency <= self.pll_f_out_max

    def get_pfd_max(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_pfd_max
        elif specification == "pll":
            return self.pll_f_pfd_max
        else:
            return None

    def get_pfd_min(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_pfd_min
        elif specification == "pll":
            return self.pll_f_pfd_min
        else:
            return None

    def get_vco_max(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_vco_max
        elif specification == "pll":
            return self.pll_f_vco_max
        else:
            return None

    def get_vco_min(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_vco_min
        elif specification == "pll":
            return self.pll_f_vco_min
        else:
            return None

    def get_f_out_min(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_out_min
        elif specification == "pll":
            return self.pll_f_out_min
        else:
            return None

    def get_f_out_max(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_out_max
        elif specification == "pll":
            return self.pll_f_out_max
        else:
            return None
