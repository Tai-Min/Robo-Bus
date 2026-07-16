"""
Provides implementation of WriterReceiverSync class, a synchronization object that notifies
managed device about it's current role and delivery status.
"""
import asyncio
import logging
from typing import Self


logger = logging.getLogger(__name__)


class WriterReceiverSync():
    """
    Sync object that notifies managed object about it's current role.
    """

    def __init__(self, name: str, is_writer: bool):
        """
        Constructor.

        @param name: Name for logging.
        @param is_writer: Whether this object is a writer at the beginning.
        @param delivery_timeout: Timeout for waiting for delivery confirmation.
        """
        logger.debug("%s: Init, is_writer: %s", name, is_writer)
        self._name = name
        self._writer_role_timeout = 0
        self._delivery_confirmed_flag = asyncio.Event()
        self._is_writer_flag = asyncio.Event()
        self._friend: Self = None
        if is_writer:
            self._is_writer_flag.set()
        self._payload = b""

    def set_friend(self, friend: Self):
        """
        Set friend that this object will notify about received data and will mark as a writer.
        """
        self._friend = friend


    def set_writer_role_timeout(self, timeout: float):
        """
        Set timeout value for writer role await.

        @param timeout: Timeout to set.
        """
        self._writer_role_timeout = timeout


    async def wait_for_delivery(self):
        """
        Await untill some other object confirms that
        the payload was delivered to this object or timeout occurs.
        """
        try:
            await asyncio.wait_for(self._delivery_confirmed_flag.wait(), timeout=self._writer_role_timeout)
        except asyncio.TimeoutError:
            pass


    def is_delivered(self) -> bool:
        """
        Whether other object confirmed that the payload was delivered.
        """
        return self._delivery_confirmed_flag.is_set()


    def notify_friend_delivered(self, payload: bytes):
        """
        Notify friend that the payload was delivered.

        @param payload: Delivered payload.
        """
        if self._friend:
            # pylint: disable=protected-access
            self._friend._notify_delivered(payload)
        else:
            pass


    def _notify_delivered(self, payload: bytes):
        """
        Called by other object to notify this object that the payload was delivered.

        @param payload: Delivered payload.
        """
        logger.debug("%s: Friend has received the payload", self._name)
        self._delivery_confirmed_flag.set()
        self._payload = payload


    def get_last_payload(self) -> bytes:
        """
        Get last delivered payload.

        @return Last delivered payload.
        """
        return self._payload


    async def wait_for_writer_role(self):
        """
        Await until other object marks this object as a writer.
        """
        try:
            await asyncio.wait_for(self._is_writer_flag.wait(), timeout=self._writer_role_timeout)
        except asyncio.TimeoutError:
            pass


    def _mark_writer(self):
        """
        Called by other object to mark this object as a writer.
        """
        logger.debug("%s: Marked as a writer", self._name)
        self._is_writer_flag.set()


    def pass_writer_role_to_friend(self):
        """
        Mark friend as a writer.
        """
        self._is_writer_flag.clear()
        self._delivery_confirmed_flag.clear() # Non writer doesn't expect delivery confirmation

        if not self._friend:
            logger.warning("%s: No friend to mark as a writer", self._name)
            return

        # pylint: disable=protected-access
        self._friend._mark_writer()
