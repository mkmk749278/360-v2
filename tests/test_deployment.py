"""Tests for deployment configuration and pre-flight checks."""

import os


from src.historical_data import HistoricalDataStore


class TestEnvExample:
    def test_env_example_exists(self):
        path = os.path.join(
            os.path.dirname(__file__), os.pardir, ".env.example"
        )
        assert os.path.isfile(path)



class TestDeployScript:
    def test_deploy_script_exists(self):
        path = os.path.join(
            os.path.dirname(__file__), os.pardir, "deploy.sh"
        )
        assert os.path.isfile(path)

    def test_deploy_script_is_executable(self):
        path = os.path.join(
            os.path.dirname(__file__), os.pardir, "deploy.sh"
        )
        assert os.access(path, os.X_OK)

    def test_deploy_script_has_shebang(self):
        path = os.path.join(
            os.path.dirname(__file__), os.pardir, "deploy.sh"
        )
        with open(path) as f:
            first_line = f.readline()
        assert first_line.startswith("#!/")


class TestHistoricalDataStoreHasData:
    def test_has_data_empty(self):
        store = HistoricalDataStore()
        assert store.has_data() is False

    def test_has_data_with_candles(self):
        import numpy as np

        store = HistoricalDataStore()
        store.candles["BTCUSDT"] = {
            "1m": {
                "open": np.array([1.0]),
                "high": np.array([2.0]),
                "low": np.array([0.5]),
                "close": np.array([1.5]),
                "volume": np.array([100.0]),
            }
        }
        assert store.has_data() is True
