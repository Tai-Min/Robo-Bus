"""
Contains multiple wait_for_dut_x used to wait 
for the DUT to reach a valid state during PPK2 setup.
"""
import logging
import asyncio
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


logger = logging.getLogger(__name__)


class FileHandler(FileSystemEventHandler):
    """
    Used with Observer to watch for file to appear in the filesystem.
    """
    def __init__(self, file: str, evt: asyncio.Event):
        """
        Constructor.

        @param file: File to watch for.
        @param evt: Event flag to set when file is created.
        """

        if file is None or file == "":
            e = "Valid filename must be provided"
            logger.error(e)
            raise ValueError(e)
        
        if evt is None:
            e = "Event must be provided"

        super().__init__()
        logger.debug("Init")
        self._file = file
        self._evt = evt


    def on_created(self, _):
        """
        Set event flag when desired file is created.

        @param _: Not used.
        """
        # Better than checking src_path
        # when looking for symlink serial ports
        if os.path.exists(self._file):
            self._evt.set()


async def wait_for_dut_serial(kwargs: dict) -> bool:
    """
    Wait for serial port to appear or timeout.

    @param kwargs: Shall contain DUT port and a timeout.
    @return True if serial port appeared, false otherwise.
    """
    if "port" not in kwargs or "timeout" not in kwargs:
        logger.error("%s: Requires port (str) and wait timeout (float) as parameters", 
                     wait_for_dut_serial.__name__)
        return False

    serial = kwargs["port"]
    timeout = kwargs["timeout"]

    evt = asyncio.Event()
    handler = FileHandler(serial, evt)
    observer = Observer()
    observer.schedule(handler, path="/dev")
    observer.start()

    try:
        await asyncio.wait_for(evt.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass

    observer.stop()

    return evt.is_set()


# pylint: disable=unused-argument
async def wait_for_dut_none(kwargs: dict) -> bool:
    """
    Noop.

    @param: kwargs: Not used.
    @return Always true.
    """
    return True
