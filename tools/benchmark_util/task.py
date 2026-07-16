"""
Entry point to coroutine based benchmark runner.
"""
from typing import List
import sys
import logging
import signal
import asyncio

from helpers.abc_helper import Helper
from devices.abc_device import Device


logger = logging.getLogger(__name__)


async def task(devices : List[Device], helpers: List[Helper]):
    """
    Main task that runs benchmarks.

    @param devices: List of devices to run the benchmark on.
    @param helpers: List of helpers to run the benchmark with.
    """
    async def ctrl_c_signal_handler():
        logger.info("Keyboard interrupt called")
        for helper in helpers:
            await helper.stop()
        for device in devices:
            await device.stop()

    asyncio.get_event_loop().add_signal_handler(
        signal.SIGINT, lambda: asyncio.create_task(ctrl_c_signal_handler()))

    devices.sort(key=lambda d: d.get_priority())

    logger.info("Opening devices")

    for device in devices:
        res = await device.open()
        if not res:
            logger.error("Failed to open device %s", device.get_name())
            return

    logger.info("Starting loops")
    async with asyncio.TaskGroup() as tg:
        for device in devices:
            tg.create_task(device.loop())
        for helper in helpers:
            tg.create_task(helper.loop())
