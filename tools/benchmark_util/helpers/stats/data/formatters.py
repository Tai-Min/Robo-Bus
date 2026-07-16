"""
Provides implementation of string formatters for different unit types.
"""

class UnitTypes():
    """
    Contains unit types as strings.
    """
    BYTES_UNIT = "bytes"
    MICROAMPS_UNIT = "microamps"

def pretty_format_bytes(size: int) -> str:
    """
    Format bytes size to string with post fixes like 2KB, 10.2MB etc.

    @param size: Size in bytes.
    @return Pretty formatted size.
    """
    size = float(size)
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size >= power:
        size /= power
        n += 1

    if n > 4:
        raise ValueError(
            f"Size is too big to format: {size}B. I have no idea how you managed to get here.")

    return str(round(size, 2)) + power_labels[n]+"B"


def pretty_format_microamps(size: int) -> str:
    """
    Format microamps size to string with post fixes like 2mA, 10.2uA etc.

    @param size: Size in microamps.
    @return Pretty formatted size.
    """
    size = float(size)
    power = 1000
    n = 0
    power_labels = {0 : 'u', 1: 'm', 2: ''}
    while size >= power:
        size /= power
        n += 1

    if n > 4:
        raise ValueError(
            f"Size is too big to format: {size}uA. I have no idea how you managed to get here.")

    return str(round(size, 2)) + power_labels[n]+"A"
