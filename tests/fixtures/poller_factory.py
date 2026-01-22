# filename: tests/fixtures/poller_factory.py

"""
Fixtures for constructing Poller instances in a deterministic, test-safe way.
"""

from typing import Any, Iterable, Optional

import pytest

import logexp.poller as poller_module
from logexp.poller import Poller
from logexp.poller_config import PollerConfig
from tests.fixtures.poller.fake_ingestion import FakeIngestion
from tests.fixtures.poller.fake_serial import FakeSerial


@pytest.fixture
def make_poller(monkeypatch):
    """
    Factory fixture for creating Poller instances with controlled config
    and deterministic ingestion behavior.

    Supports:
      - config: PollerConfig (preferred, required going forward)
      - fake_serial_items: iterable of bytes or items for FakeSerial
      - ingestion: custom ingestion object (overrides FakeIngestion)
      - fail_ingestion: bool to force ingestion failures via FakeIngestion
    """

    def _make(
        config: Optional[PollerConfig] = None,
        fake_serial_items: Optional[Iterable[Any]] = None,
        ingestion: Optional[Any] = None,
        fail_ingestion: bool = False,
    ) -> Poller:
        # Default config: fake mode with default frame value
        if config is None:
            config = PollerConfig(mode="fake")

        # If tests provide fake_serial_items, patch serial.Serial and ensure
        # a non-empty serial_port so Poller enters "serial" mode.
        if fake_serial_items is not None:

            def _fake_serial(*args: Any, **kwargs: Any) -> FakeSerial:
                return FakeSerial(fake_serial_items, *args, **kwargs)

            monkeypatch.setattr(poller_module.serial, "Serial", _fake_serial)

            if config.mode == "serial" and not config.serial_port:
                config.serial_port = "/dev/ttyFAKE"

        # Ingestion: either a custom ingestion or our FakeIngestion
        if ingestion is not None:
            ingestion_impl = ingestion
        else:
            ingestion_impl = FakeIngestion(should_fail=fail_ingestion)

        return Poller(config, ingestion_impl)

    return _make
