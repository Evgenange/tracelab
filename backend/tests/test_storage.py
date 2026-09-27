import hashlib
import uuid

from app.services.storage import LocalStorageService


def test_storage_saves_file_with_expected_checksum(tmp_path) -> None:
    service = LocalStorageService(str(tmp_path))

    content = b"country,year\nNetherlands,2024\n"
    dataset_id = uuid.uuid4()
    version_id = uuid.uuid4()

    storage_path, checksum = service.save_dataset_version(
        dataset_id=dataset_id,
        version_id=version_id,
        filename="data.csv",
        content=content,
    )

    expected_checksum = hashlib.sha256(content).hexdigest()

    assert checksum == expected_checksum

    with open(storage_path, "rb") as stored_file:
        assert stored_file.read() == content
