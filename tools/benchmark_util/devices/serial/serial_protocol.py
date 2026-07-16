"""
Provides implementation of Protocol class for HalfDuplexSerial.
"""
import logging
import asyncio
import timeit
from collections.abc import Callable
from collections import deque


logger = logging.getLogger(__name__)


class Protocol(asyncio.Protocol):
    """
    Serial port protocol implementation.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._name = ""

        self._new_data_flag = asyncio.Event()
        self._read_len = 0
        self._read_buf = deque()
        self._silence_time = 0
        self._expected_payload_size = 0

        self._transport: asyncio.Transport = None
        self._data_callback: Callable[[bytes], None] = None
        self._last_read_time = 0
        self._reader_stopped_flag = asyncio.Event()
        self._reader_stopped_flag.set()
        self._exit_flag = asyncio.Event()


    def _make_payload(self) -> bytes:
        """
        Combine all available transfers into one bytes object. Clears stored transfers.

        @return Complete data transfer.
        """
        res = b"".join(self._read_buf)
        self._read_buf.clear()
        self._read_len = 0
        return res


    def _forward_payload(self, payload: bytes):
        """
        Forward payload to the callback.

        @param payload: Payload to forward.
        """
        if self._data_callback:
            logger.debug("%s: Forwarding data: %s", self._name, payload)
            self._data_callback(payload)
        else:
            logger.warning("%s: No callback to forward payload", self._name)


    def set_name(self, name: str):
        """
        Set name for the protocol. Used in logging.

        @param name: Name to set.
        """
        self._name = name


    def set_silence_time(self, silence_time: float):
        """
        Set time at which the protocol will detect silence on the receiver.

        @param silence_time: Time to set.
        """
        self._silence_time = silence_time


    def set_expected_payload_size(self, size: int):
        """
        Set the expected size of the payload to receive.

        @param size: Expected payload size in bytes.
        """
        self._expected_payload_size = size


    def set_data_callback(self, callback: Callable[[bytes], None]):
        """
        Set callback that will be called after a complete data transfer is received.

        @param callback: Callback to be called on finished datatransfer.
        Parameter contains complete payload.
        """
        self._data_callback = callback


    def connection_made(self, transport: asyncio.BaseTransport):
        """
        DO NOT CALL MANUALLY.
        Called by asyncio when connection is made after open.

        @param transport: Asyncio transport object.
        """
        logger.info("%s: Connection made", self._name)
        self._transport = transport


    def connection_lost(self, _):
        """
        DO NOT CALL MANUALLY.
        Called by asyncio when connection is lost.

        @param _: Unused.
        """
        logger.info("%s: Connection lost", self._name)
        loop = asyncio.get_running_loop()
        loop.create_task(self.stop())


    def data_received(self, data: bytes):
        """
        DO NOT CALL MANUALLY.
        Called by asyncio when received chunk of data from the serial.

        @param data: Received data.
        """
        logger.debug("%s: Received payload: %s", self._name, data)
        self._read_len += len(data)
        self._read_buf.append(data)
        self._last_read_time = timeit.default_timer()
        self._new_data_flag.set()


    def data_write(self, payload: bytes):
        """
        Write some payload to the serial

        @param payload: Payload to write.
        """
        logger.debug("%s: Writing payload: %s", self._name, payload)

        if not self._transport:
            logger.warning("%s: No transport to write payload", self._name)
            return

        self._transport.write(payload)


    async def loop_reader(self):
        """
        Check buffer for incoming data constantly,
        forward this data when silence on serial is detected.
        """
        self._reader_stopped_flag.clear()
        logger.info("%s: Starting reader loop", self._name)

        while not self._exit_flag.is_set():
            await self._new_data_flag.wait()
            self._new_data_flag.clear()

            if (self._read_len < self._expected_payload_size) and \
               (timeit.default_timer() - self._last_read_time < self._silence_time):
                continue

            logger.debug("%s: Finished reading serial, forwarding payload", self._name)
            self._forward_payload(self._make_payload())

        logger.info("%s: Stopping reader loop", self._name)
        self._reader_stopped_flag.set()


    async def stop(self):
        """
        Stop the protocol.
        """
        logger.info("%s: Stopping protocol", self._name)
        self._exit_flag.set()
        self._new_data_flag.set()

        if not self._reader_stopped_flag.is_set():
            logger.debug("%s: Waiting for reader loop to stop...", self._name)
            await self._reader_stopped_flag.wait()

        if self._transport:
            logger.debug("%s: Stopping transport", self._name)
            self._transport.close()
