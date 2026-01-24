# filename: tests/fixtures/poller_factory.py

"""
Fixtures for constructing Poller instances in a deterministic, test-safe way.
"""

from typing import Any, Iterable, Optional

import pytest

import beamfoundry.poller as poller_module
from beamfoundry.poller import Poller
from beamfoundry.poller_config import PollerConfig

from .poller.fake_ingestion import FakeIngestion
from .poller.fake_serial import FakeSerial


@pytest.fixture
def make_poller(monkeypatch):
    """
    Factory fixture for creating Poller instances with controlled config
    and deterministic ingestion behavior.
    """

    def _make(
        config: Optional[PollerConfig] = None,
        fake_serial_items: Optional[Iterable[Any]] = None,
        ingestion: Optional[Any] = None,
        fail_ingestion: bool = False,
    ) -> Poller:
        if config is None:
            config = PollerConfig(mode="fake")

        if fake_serial_items is not None:

            def _fake_serial(*args: Any, **kwargs: Any) -> FakeSerial:
                return FakeSerial(fake_serial_items, *args, **kwargs)

            monkeypatch.setattr(poller_module.serial, "Serial", _fake_serial)

            if config.mode == "serial" and not config.serial_port:
                config.serial_port = "/dev/ttyFAKE"

        ingestion_impl = ingestion or FakeIngestion(should_fail=fail_ingestion)
        return Poller(config, ingestion_impl)

    return _make
