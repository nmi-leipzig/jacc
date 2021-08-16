
def frequency_to_period_ns_precision(frequency_in_mhz: float) -> float:
    return (1 / frequency_in_mhz) * 1000


def period_to_frequency_mhz_precision(period_in_ns: float) -> float:
    return (1 / period_in_ns) * 1000


def relative_error(target_value, actual_value):
    return abs(target_value - actual_value) / target_value
