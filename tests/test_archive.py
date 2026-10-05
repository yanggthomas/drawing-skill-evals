import tempfile
import unittest
from pathlib import Path

from drawing_eval.io import load_manifest, png_dimensions, repository_root, sha256
from drawing_eval.validate import validate_repository


class ArchiveHelpersTest(unittest.TestCase):
    def test_json_compatible_yaml_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.yaml"
            path.write_text('{"schema_version": 1, "id": "run"}')
            self.assertEqual(load_manifest(path)["id"], "run")

    def test_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "value"
            path.write_bytes(b"abc")
            self.assertEqual(sha256(path), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_png_dimensions_rejects_non_png(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(ValueError):
                png_dimensions(path)

    def test_repository_archive_is_valid(self):
        self.assertEqual(validate_repository(repository_root()), [])

    def test_manifests_inventory_all_54_final_images(self):
        root = repository_root()
        image_count = 0
        for manifest_path in (root / "runs").glob("*/run.yaml"):
            run = load_manifest(manifest_path)
            for case in run["cases"]:
                for artifacts in case["arms"].values():
                    image_count += sum(item["path"].endswith(".png") for item in artifacts)
        self.assertEqual(image_count, 54)


if __name__ == "__main__":
    unittest.main()
