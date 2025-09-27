import config.config as config_mod
import importlib


def test_config_module_import():
    # Should import without error
    importlib.reload(config_mod)
    assert hasattr(config_mod, "__file__") or hasattr(config_mod, "__doc__")


def test_config_file_exists():
    assert hasattr(config_mod, "__file__")
