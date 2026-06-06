from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_anywhere as generator
import validate_anywhere as validator


class GeoSiteParsingTests(unittest.TestCase):
    def parse(self, name: str, contents: str) -> list[tuple[int, str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / name
            path.write_text(contents)
            return generator.parse_geosite_file(path)

    def test_supported_geosite_syntax(self) -> None:
        rules = self.parse(
            "service",
            """
            # comment
            domain:example.com
            keyword:example-
            full:api.example.net
            plain.example.org
            domain:example.com
            """,
        )
        self.assertEqual(
            rules,
            [
                (2, "example.com"),
                (3, "example-"),
                (2, "api.example.net"),
                (2, "plain.example.org"),
            ],
        )

    def test_github_regexp_is_approximated(self) -> None:
        rules = self.parse("github", r"regexp:^github-production-release-asset-.+$")
        self.assertEqual(rules, [(3, "github-production-release-asset-")])

    def test_private_regexp_is_omitted(self) -> None:
        rules = self.parse("private", r"regexp:^[a-z]+$")
        self.assertEqual(rules, [])

    def test_unknown_regexp_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported regexp"):
            self.parse("service", r"regexp:^example$")


class RuleSemanticsTests(unittest.TestCase):
    def test_suffix_keyword_and_cidr_coverage(self) -> None:
        self.assertTrue(
            generator.rule_is_covered((2, "api.example.com"), (2, "example.com"))
        )
        self.assertTrue(
            generator.rule_is_covered((2, "cdn-example.net"), (3, "example"))
        )
        self.assertTrue(
            generator.rule_is_covered((0, "10.1.0.0/16"), (0, "10.0.0.0/8"))
        )
        self.assertFalse(
            generator.rule_is_covered((2, "notexample.com"), (2, "example.com"))
        )

    def test_split_never_exceeds_anywhere_limit(self) -> None:
        rules = [(2, f"{index}.example") for index in range(20_001)]
        chunks = generator.split_rules(rules)
        self.assertEqual([len(chunk) for chunk in chunks], [10_000, 10_000, 1])


class ValidationTests(unittest.TestCase):
    def test_validator_rejects_duplicate_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "DEFAULT"
            profile.mkdir()
            (profile / "DIRECT.arrs").write_text(
                "name = Duplicate\n2, example.com\n2, example.com\n"
            )
            with self.assertRaisesRegex(ValueError, "duplicate"):
                validator.validate(Path(directory), quiet=True)

    def test_validator_rejects_priority_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "DEFAULT"
            profile.mkdir()
            (profile / "REJECT.arrs").write_text(
                "name = Reject\n2, example.com\n"
            )
            (profile / "DIRECT.arrs").write_text(
                "name = Direct\n2, api.example.com\n"
            )
            with self.assertRaisesRegex(ValueError, "is covered"):
                validator.validate(Path(directory), quiet=True)


class AtomicGenerationTests(unittest.TestCase):
    def test_failed_build_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "ANYWHERE"
            output.mkdir()
            marker = output / "existing.arrs"
            marker.write_text("original")
            sources = root / "sources.json"
            sources.write_text(json.dumps({"geoip": {}, "geosite": {}}))

            with mock.patch.object(
                generator, "build_rule_sets", side_effect=ValueError("broken")
            ):
                with self.assertRaisesRegex(ValueError, "broken"):
                    generator.generate(
                        root / "geosite",
                        root / "geoip",
                        output,
                        sources,
                        root / "stats.json",
                    )

            self.assertEqual(marker.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
