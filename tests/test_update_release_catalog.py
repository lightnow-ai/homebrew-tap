import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "update-release-catalog.py"
SPEC = importlib.util.spec_from_file_location("release_catalog", SCRIPT)
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class ReleaseCatalogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "Formula").mkdir()
        self.write_formula("lightnow-cli", "1.3.1")
        self.write_formula("lightnow-proxy", "1.4.2")
        self.write_catalog("1.3.1", "1.4.2")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_formula(self, package: str, version: str) -> None:
        normalized = package.replace("-", "_")
        (self.root / "Formula" / f"{package}.rb").write_text(
            f'class Formula\n  url "https://example.test/{normalized}-{version}.tar.gz"\nend\n'
        )

    def write_catalog(self, cli: str, proxy: str) -> None:
        (self.root / "releases.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generated_at": "2026-07-17T00:00:00Z",
                    "packages": {
                        "lightnow-cli": {"version": cli},
                        "lightnow-proxy": {"version": proxy},
                    },
                }
            )
        )

    def test_check_accepts_matching_catalog(self) -> None:
        catalog.check_catalog(self.root)

    def test_update_requires_verified_formula_and_is_idempotent(self) -> None:
        self.write_formula("lightnow-proxy", "1.4.3")
        self.assertTrue(catalog.update_catalog(self.root, "lightnow-proxy", "1.4.3"))
        self.assertFalse(catalog.update_catalog(self.root, "lightnow-proxy", "1.4.3"))
        self.assertEqual(
            json.loads((self.root / "releases.json").read_text())["packages"][
                "lightnow-proxy"
            ]["version"],
            "1.4.3",
        )

    def test_update_refuses_downgrade(self) -> None:
        self.write_formula("lightnow-proxy", "1.4.1")
        with self.assertRaisesRegex(ValueError, "downgrade"):
            catalog.update_catalog(self.root, "lightnow-proxy", "1.4.1")

    def test_update_refuses_unverified_version(self) -> None:
        with self.assertRaisesRegex(ValueError, "verified formula"):
            catalog.update_catalog(self.root, "lightnow-proxy", "1.4.3")


if __name__ == "__main__":
    unittest.main()
