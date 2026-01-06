# tests/test_env_contract.py

from logexp.app.config import OPTIONAL_ENV_VARS, REQUIRED_ENV_VARS


def test_required_env_vars_are_documented_and_unique() -> None:
    """
    Ensure the set of required env vars is explicit, non-empty, and unique.
    """
    assert isinstance(REQUIRED_ENV_VARS, dict)
    assert REQUIRED_ENV_VARS, "REQUIRED_ENV_VARS must not be empty"

    keys = list(REQUIRED_ENV_VARS.keys())
    assert len(keys) == len(set(keys)), "Duplicate keys in REQUIRED_ENV_VARS"


def test_optional_env_vars_are_documented_and_unique() -> None:
    """
    Ensure the set of optional env vars is explicit and unique.
    """
    assert isinstance(OPTIONAL_ENV_VARS, dict)

    keys = list(OPTIONAL_ENV_VARS.keys())
    assert len(keys) == len(set(keys)), "Duplicate keys in OPTIONAL_ENV_VARS"


def test_no_required_env_shadowed_by_optional() -> None:
    """
    A variable must not be declared both required and optional.
    """
    required_keys = set(REQUIRED_ENV_VARS.keys())
    optional_keys = set(OPTIONAL_ENV_VARS.keys())

    overlap = required_keys & optional_keys
    assert not overlap, f"Env vars present in both required and optional: {overlap}"
