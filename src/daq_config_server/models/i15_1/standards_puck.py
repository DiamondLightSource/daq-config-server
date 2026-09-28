from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

STANDARD_SAMPLE = Literal[
    "Silicon", "Tungsten/Boron mix", "Si/Al2O3", "Pb", "LaB6 660b", "Ga/In"
]

ALLOWED_USER_CAPILLARIES = Literal[
    "bs1.0",
    "bs1.5",
    "bs2.0",
    "fq1.0",
    "fq1.5",
    "fq2.0",
]

STANDARD_CAPILLARY = ALLOWED_USER_CAPILLARIES | Literal["metal"]


class StandardsPin(BaseModel):
    capillary: STANDARD_CAPILLARY
    contents: STANDARD_SAMPLE | None  # None for empty capillary


class StandardsPuck(BaseModel):
    model_config = ConfigDict(validate_default=True)

    pins: dict[int, StandardsPin | None]

    def get_pin_number(self, pin: StandardsPin):
        for pin_number, loaded_pin in self.pins.items():
            if pin == loaded_pin:
                return pin_number
        raise ValueError(f"No pin on the standards puck matching {pin}")

    @field_validator("pins")
    @classmethod
    def pins_must_be_1_to_22(cls, pins: dict[int, StandardsPin | None]):
        assert sorted(pins.keys()) == list(range(1, 23)), (
            f"Pins must be 1-22, with no gaps. Current pins: {list(pins.keys())}"
        )
        return pins
