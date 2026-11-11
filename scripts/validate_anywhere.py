#!/usr/bin/env python3
"""Validate generated Anywhere routing rule sets."""

from __future__ import annotations

import argparse
import ipaddress
from pathlib import Path

MAX_RULES = 100_000
ACTION_PRIORITY = ("REJECT", "PROXY", "DIRECT")
ROUTING_BY_ACTION = {"DIRECT": 1, "REJECT": 2, "PROXY": 0}

# Single-label suffixes match a whole TLD. Only these reserved or
# brand TLDs are expected from the sources; anything else is treated
# as a broken upstream list rather than shipped.
ALLOWED_SINGLE_LABEL_SUFFIXES = frozenset(
    {
        "example",
        "internal",
        "invalid",
        "lan",
        "local",
        "localdomain",
        "localhost",
        "psk",
        "test",
        "xbox",
        "yandex",
        "youtube",
    }
)
MIN_PREFIX_LENGTH = {4: 8, 6: 16}
# Broader networks are accepted only inside multicast and reserved space.
ALLOWED_BROAD_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in ("224.0.0.0/3", "fc00::/7", "fe80::/10", "ff00::/8")
)


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
    routing: int | None = None

    for number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(("#", "//")):
            continue

        if "=" in line:
            key, value = (part.strip() for part in line.split("=", 1))
            if key.lower() == "name":
                has_name = bool(value)
                continue
            if key.lower() == "routing":
                if value not in {"0", "1", "2"}:
                    raise ValueError(f"invalid routing at {path}:{number}: {value}")
                routing = int(value)
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
            if network.prefixlen < MIN_PREFIX_LENGTH[network.version] and not any(
                network.version == allowed.version and network.subnet_of(allowed)
                for allowed in ALLOWED_BROAD_NETWORKS
            ):
                raise ValueError(f"CIDR is too broad at {path}:{number}: {line}")
        elif rule_type == 2:
            if "." not in value and value.lower() not in ALLOWED_SINGLE_LABEL_SUFFIXES:
                raise ValueError(
                    f"unexpected top-level suffix at {path}:{number}: {line}"
                )

        rules.append((rule_type, value.lower()))

    if not has_name:
        raise ValueError(f"missing name header: {path}")
    if not 0 < len(rules) <= MAX_RULES:
        raise ValueError(f"invalid rule count in {path}: {len(rules)}")
    if len(rules) != len(set(rules)):
        raise ValueError(f"duplicate rules in {path}")
    action = path.stem.split("_", 1)[0]
    if routing != ROUTING_BY_ACTION.get(action):
        raise ValueError(f"invalid routing assignment in {path}: {routing}")
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


def default_tier_overrides(
    groups: dict[str, list[tuple[int, str]]],
) -> list[tuple[tuple[int, str], tuple[int, str]]]:
    """PROXY rules that a DIRECT rule wins while PROXY stays on Default.

    PROXY is seeded with routing = 0, which Anywhere loads into the Neutral
    tier, below the User tier holding DIRECT. A broader DIRECT rule then
    beats the more specific PROXY rule until PROXY gets an explicit action.
    """
    return [
        (proxy_rule, direct_rule)
        for proxy_rule in groups.get("PROXY", [])
        for direct_rule in groups.get("DIRECT", [])
        if rule_is_covered(proxy_rule, direct_rule)
    ]


def validate(directory: Path, quiet: bool = False) -> None:
    paths = sorted(directory.rglob("*.arrs"))
    if not paths:
        raise ValueError(f"no .arrs files found under {directory}")

    for profile in sorted(path for path in directory.iterdir() if path.is_dir()):
        groups: dict[str, list[tuple[int, str]]] = {}
        for path in sorted(profile.glob("*.arrs")):
            action = path.stem.split("_", 1)[0]
            rules = parse_rule_set(path)
            groups.setdefault(action, []).extend(rules)
            if not quiet:
                print(f"{path}: {len(rules)} rules")
        validate_priority(profile, groups)
        if not quiet:
            for proxy_rule, direct_rule in default_tier_overrides(groups):
                print(
                    f"warning: {profile.name}: PROXY rule {proxy_rule} needs an "
                    f"explicit action, DIRECT rule {direct_rule} wins on Default"
                )


if __name__ == "__main__":
    validate(parse_args().directory)
