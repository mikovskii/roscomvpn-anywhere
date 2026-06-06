#!/usr/bin/env python3
"""Validate generated Anywhere routing rule sets."""

from __future__ import annotations

import argparse
import ipaddress
from pathlib import Path

MAX_RULES = 10_000
ACTION_PRIORITY = ("REJECT", "PROXY", "DIRECT")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "ANYWHERE",
    )
    return parser.parse_args()


def parse_rule_set(path: Path) -> list[tuple[int, str]]:
    rules: list[tuple[int, str]] = []
    has_name = False

    for number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(("#", "//")):
            continue

        if "=" in line and line.split("=", 1)[0].strip().lower() == "name":
            has_name = bool(line.split("=", 1)[1].strip())
            continue

        try:
            raw_type, value = (part.strip() for part in line.split(",", 1))
            rule_type = int(raw_type)
        except (ValueError, TypeError) as error:
            raise ValueError(f"invalid rule at {path}:{number}: {line}") from error

        if rule_type not in range(4) or not value:
            raise ValueError(f"invalid rule at {path}:{number}: {line}")

        if rule_type in (0, 1):
            try:
                network = ipaddress.ip_network(value, strict=False)
            except ValueError as error:
                raise ValueError(
                    f"invalid CIDR at {path}:{number}: {value}"
                ) from error
            expected_version = 4 if rule_type == 0 else 6
            if network.version != expected_version:
                raise ValueError(f"CIDR type mismatch at {path}:{number}: {line}")

        rules.append((rule_type, value.lower()))

    if not has_name:
        raise ValueError(f"missing name header: {path}")
    if not 0 < len(rules) <= MAX_RULES:
        raise ValueError(f"invalid rule count in {path}: {len(rules)}")
    if len(rules) != len(set(rules)):
        raise ValueError(f"duplicate rules in {path}")
    return rules


def rule_is_covered(
    rule: tuple[int, str],
    higher_priority_rule: tuple[int, str],
) -> bool:
    rule_type, value = rule
    higher_type, higher_value = higher_priority_rule

    if rule == higher_priority_rule:
        return True
    if higher_type == 2 and rule_type == 2:
        return value.endswith("." + higher_value)
    if higher_type == 3 and rule_type in (2, 3):
        return higher_value in value
    if higher_type in (0, 1) and rule_type == higher_type:
        network = ipaddress.ip_network(value, strict=False)
        higher_network = ipaddress.ip_network(higher_value, strict=False)
        return network.subnet_of(higher_network)
    return False


def validate_priority(profile: Path, groups: dict[str, list[tuple[int, str]]]) -> None:
    for index, higher_action in enumerate(ACTION_PRIORITY):
        for lower_action in ACTION_PRIORITY[index + 1 :]:
            for lower_rule in groups.get(lower_action, []):
                for higher_rule in groups.get(higher_action, []):
                    if rule_is_covered(lower_rule, higher_rule):
                        raise ValueError(
                            f"{profile.name}: {lower_action} rule {lower_rule} "
                            f"is covered by {higher_action} rule {higher_rule}"
                        )


def validate(directory: Path) -> None:
    paths = sorted(directory.rglob("*.arrs"))
    if not paths:
        raise ValueError(f"no .arrs files found under {directory}")

    for profile in sorted(path for path in directory.iterdir() if path.is_dir()):
        groups: dict[str, list[tuple[int, str]]] = {}
        for path in sorted(profile.glob("*.arrs")):
            action = path.stem.split("_", 1)[0]
            rules = parse_rule_set(path)
            groups.setdefault(action, []).extend(rules)
            print(f"{path}: {len(rules)} rules")
        validate_priority(profile, groups)


if __name__ == "__main__":
    validate(parse_args().directory)
