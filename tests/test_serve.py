import importlib.util
from pathlib import Path
from unittest.mock import Mock

import joblib
import pytest
from fastapi.testclient import TestClient
from google.cloud import storage


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ARTIFACT_BUCKET", "test-bucket")
    model_path = tmp_path / "models" / "model.joblib"
    monkeypatch.setattr("os.path.expanduser", lambda path: str(model_path))
    model = Mock()
    cloud = Mock()
    cloud.bucket.return_value.blob.return_value.download_to_filename.side_effect = (
        lambda path: Path(path).write_bytes(b"test model")
    )
    monkeypatch.setattr(storage, "Client", lambda: cloud)
    monkeypatch.setattr(joblib, "load", lambda path: model)

    source = Path(__file__).resolve().parents[1] / "src" / "serve.py"
    spec = importlib.util.spec_from_file_location("serve_under_test", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    cloud.bucket.assert_called_once_with("test-bucket")
    cloud.bucket.return_value.blob.assert_called_once_with(
        "artifacts/current/model.joblib"
    )
    assert model_path.exists()
    with TestClient(module.app) as client:
        yield client, model


def test_health_and_predictions(api):
    client, model = api
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    features = [28, 2, 14, 2, 11, 0, 1, 0, 0, 45]
    for prediction, label in [(0, "thu_nhap_thap"), (1, "thu_nhap_cao")]:
        model.predict.return_value = [prediction]
        response = client.post("/score", json={"features": features})
        assert response.status_code == 200
        assert response.json() == {"prediction": prediction, "label": label}
        model.predict.assert_called_with([features])


@pytest.mark.parametrize("count", [0, 9, 11])
def test_wrong_feature_count(api, count):
    client, model = api
    response = client.post("/score", json={"features": [0] * count})
    assert response.status_code == 400
    model.predict.assert_not_called()


@pytest.mark.parametrize("value", ["invalid", "NaN", "Infinity"])
def test_invalid_feature_value(api, value):
    client, model = api
    response = client.post("/score", json={"features": [value] + [0] * 9})
    assert response.status_code == 422
    model.predict.assert_not_called()
