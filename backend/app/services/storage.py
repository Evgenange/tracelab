import hashlib
import uuid
from pathlib import Path


class LocalStorageService:
    def __init__(self, root_path: str) -> None:
        self.root_path = Path(root_path)

    def save_dataset_version(
        self,
        *,
        dataset_id: uuid.UUID,
        version_id: uuid.UUID,
        filename: str,
        content: bytes,
    ) -> tuple[str, str]:
        checksum = hashlib.sha256(content).hexdigest()

        extension = Path(filename).suffix.lower()

        directory = self.root_path / "datasets" / str(dataset_id) / str(version_id)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = f"source{extension}"

        file_path = directory / stored_filename

        file_path.write_bytes(content)

        return str(file_path), checksum
