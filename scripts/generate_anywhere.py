#!/usr/bin/env python3
"""Generate Anywhere .arrs rule sets from RoscomVPN source lists."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import shutil
import tempfile
from pathlib import Path

from validate_anywhere import rule_is_covered, validate

MAX_RULES = 100_000
# A set may drift by this much between builds before the update is held
# for review; both limits must be exceeded to fail.
MAX_CHANGE_RATIO = 0.15
MAX_CHANGE_RULES = 50
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DIRECT_DOMAINS = (
    "private",
    "category-ru",
    "whitelist",
    "microsoft",
    "apple",
    "epicgames",
    "riot",
    "escapefromtarkov",
    "steam",
    "twitch",
    "pinterest",
    "faceit",
)
DEFAULT_PROXY_DOMAINS = (
    "google-play",
    "github",
    "twitch-ads",
    "youtube",
    "telegram",
)
REJECT_DOMAINS = ("win-spy", "torrent", "category-ads")
WHITELIST_DIRECT_DOMAINS = ("private", "whitelist")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geosite", required=True, type=Path)
    parser.add_argument("--geoip", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "ANYWHERE")
    parser.add_argument("--sources", type=Path, default=PROJECT_ROOT / "sources.json")
    parser.add_argument("--stats", type=Path, default=PROJECT_ROOT / "stats.json")
    parser.add_argument(
        "--allow-large-change",
        action="store_true",
        help="accept rule counts that moved past the drift limits",
    )
    return parser.parse_args()


def unique(rules: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return list(dict.fromkeys(rules))


def parse_geosite_file(path: Path) -> list[tuple[int, str]]:
    rules: list[tuple[int, str]] = []
    for number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("domain:"):
            rules.append((2, line.removeprefix("domain:").strip()))
        elif line.startswith("keyword:"):
            rules.append((3, line.removeprefix("keyword:").strip()))
        elif line.startswith("full:"):
            # Anywhere has no exact-domain type. Suffix is the closest
            # supported representation and may also match subdomains.
            rules.append((2, line.removeprefix("full:").strip()))
        elif line.startswith("regexp:"):
            if path.name == "github":
                # Approximation of the GitHub release asset hostname regexp.
                rules.append((3, "github-production-release-asset-"))
            elif path.name == "private":
                # The source regexp matches every single-label host. Anywhere
                # cannot express that without matching unrelated domains.
                continue
            else:
                raise ValueError(f"unsupported regexp at {path}:{number}: {line}")
        elif ":" not in line:
            rules.append((2, line))
        else:
            raise ValueError(f"unsupported rule at {path}:{number}: {line}")

    return unique(rules)


def load_domains(data_dir: Path, names: tuple[str, ...]) -> list[tuple[int, str]]:
    rules: list[tuple[int, str]] = []
    for name in names:
        path = data_dir / name
        if not path.is_file():
            raise FileNotFoundError(path)
        rules.extend(parse_geosite_file(path))
    return unique(rules)


def load_cidrs(path: Path) -> list[tuple[int, str]]:
    rules: list[tuple[int, str]] = []
    for number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            network = ipaddress.ip_network(line, strict=False)
        except ValueError as error:
            raise ValueError(f"invalid CIDR at {path}:{number}: {line}") from error
        rules.append((0 if network.version == 4 else 1, str(network)))
    return unique(rules)


def remove_shadowed(
    rules: list[tuple[int, str]],
    higher_priority_rules: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    return [
        rule
        for rule in rules
        if not any(
            rule_is_covered(rule, higher_priority_rule)
            for higher_priority_rule in higher_priority_rules
        )
    ]


def split_rules(
    rules: list[tuple[int, str]], chunk_size: int = MAX_RULES
) -> list[list[tuple[int, str]]]:
    return [
        rules[index : index + chunk_size]
        for index in range(0, len(rules), chunk_size)
    ]


def write_rule_set(
    path: Path,
    name: str,
    rules: list[tuple[int, str]],
    routing: int,
) -> None:
    if not rules or len(rules) > MAX_RULES:
        raise ValueError(f"{path} has invalid rule count: {len(rules)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"name = {name}",
        f"routing = {routing}",
        "",
        "# Generated from hydraponique/roscomvpn-geosite and roscomvpn-geoip.",
        "# Assign this set to the action stated in the file name.",
        "",
    ]
    lines.extend(f"{rule_type}, {value}" for rule_type, value in rules)
    path.write_text("\n".join(lines) + "\n")


def write_chunks(
    directory: Path,
    file_prefix: str,
    display_name: str,
    rules: list[tuple[int, str]],
    routing: int,
    chunk_size: int = MAX_RULES,
) -> None:
    chunks = split_rules(rules, chunk_size)
    for index, chunk in enumerate(chunks, start=1):
        suffix = f"_{index}" if len(chunks) > 1 else ""
        part = f" {index}/{len(chunks)}" if len(chunks) > 1 else ""
        write_rule_set(
            directory / f"{file_prefix}{suffix}.arrs",
            f"{display_name}{part}",
            chunk,
            routing,
        )


def build_rule_sets(geosite: Path, geoip: Path, output: Path) -> None:
    geosite_data = geosite / "data"
    if not geosite_data.is_dir():
        raise FileNotFoundError(f"GeoSite data directory not found under {geosite}")

    geoip_text = geoip / "text"
    if not geoip_text.is_dir():
        geoip_text = geoip / "release" / "text"
    if not geoip_text.is_dir():
        raise FileNotFoundError(f"GeoIP text directory not found under {geoip}")

    reject = load_domains(geosite_data, REJECT_DOMAINS)
    proxy = remove_shadowed(
        load_domains(geosite_data, DEFAULT_PROXY_DOMAINS),
        reject,
    )
    direct_domains = remove_shadowed(
        load_domains(geosite_data, DEFAULT_DIRECT_DOMAINS),
        reject + proxy,
    )
    direct_ips = unique(
        load_cidrs(geoip_text / "private.txt")
        + load_cidrs(geoip_text / "direct.txt")
    )
    direct = unique(direct_domains + direct_ips)

    default_dir = output / "DEFAULT"
    write_chunks(
        default_dir,
        "DIRECT",
        "RoscomVPN DEFAULT - DIRECT",
        direct,
        1,
    )
    write_chunks(default_dir, "PROXY", "RoscomVPN DEFAULT - PROXY", proxy, 0)
    write_chunks(default_dir, "REJECT", "RoscomVPN DEFAULT - REJECT", reject, 2)

    whitelist_direct = remove_shadowed(
        load_domains(geosite_data, WHITELIST_DIRECT_DOMAINS)
        + load_cidrs(geoip_text / "private.txt")
        + load_cidrs(geoip_text / "whitelist.txt"),
        reject,
    )
    whitelist_dir = output / "WHITELIST"
    write_chunks(
        whitelist_dir,
        "DIRECT",
        "RoscomVPN WHITELIST - DIRECT",
        whitelist_direct,
        1,
    )
    write_chunks(
        whitelist_dir,
        "REJECT",
        "RoscomVPN WHITELIST - REJECT",
        reject,
        2,
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rule_count(path: Path) -> int:
    return sum(
        1
        for line in path.read_text().splitlines()
        if line.strip() and line.lstrip()[0].isdigit() and "," in line
    )


def build_stats(output: Path, sources_path: Path) -> dict[str, object]:
    sources = json.loads(sources_path.read_text())
    files: list[dict[str, object]] = []
    profile_totals: dict[str, int] = {}

    for path in sorted(output.rglob("*.arrs")):
        relative = path.relative_to(output).as_posix()
        profile = relative.split("/", 1)[0]
        count = rule_count(path)
        profile_totals[profile] = profile_totals.get(profile, 0) + count
        files.append(
            {
                "path": relative,
                "rules": count,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )

    return {
        "schema": 1,
        "sources": sources,
        "profiles": {
            name: {"rules": count}
            for name, count in sorted(profile_totals.items())
        },
        "files": files,
    }


def rule_counts_by_set(stats: dict[str, object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for file in stats.get("files", []):
        # DEFAULT/DIRECT_2.arrs and DEFAULT/DIRECT.arrs are the same set.
        profile, name = file["path"].split("/", 1)
        key = f"{profile}/{name.removesuffix('.arrs').split('_', 1)[0]}"
        counts[key] = counts.get(key, 0) + file["rules"]
    return counts


def check_rule_count_changes(
    previous: dict[str, object],
    current: dict[str, object],
) -> None:
    before = rule_counts_by_set(previous)
    after = rule_counts_by_set(current)
    problems = []
    for key in sorted(before.keys() | after.keys()):
        old, new = before.get(key, 0), after.get(key, 0)
        delta = abs(new - old)
        if delta > MAX_CHANGE_RULES and delta > old * MAX_CHANGE_RATIO:
            problems.append(f"{key}: {old} -> {new}")
    if problems:
        raise ValueError(
            "rule counts changed more than expected, rerun with "
            "--allow-large-change if this is intended: " + ", ".join(problems)
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    os.replace(temporary, path)


def replace_directory(staged: Path, output: Path) -> None:
    backup = output.with_name(f".{output.name}.backup")
    if backup.exists():
        shutil.rmtree(backup)

    had_output = output.exists()
    if had_output:
        os.replace(output, backup)

    try:
        os.replace(staged, output)
    except BaseException:
        if had_output and backup.exists():
            os.replace(backup, output)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup)


def generate(
    geosite: Path,
    geoip: Path,
    output: Path,
    sources_path: Path,
    stats_path: Path,
    allow_large_change: bool = False,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(
        tempfile.mkdtemp(prefix=".anywhere-build-", dir=output.parent)
    )
    staged_output = staging_root / output.name

    try:
        build_rule_sets(geosite, geoip, staged_output)
        validate(staged_output, quiet=True)
        stats = build_stats(staged_output, sources_path)
        if stats_path.is_file() and not allow_large_change:
            check_rule_count_changes(json.loads(stats_path.read_text()), stats)
        replace_directory(staged_output, output)
        write_json(stats_path, stats)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    arguments = parse_args()
    generate(
        arguments.geosite,
        arguments.geoip,
        arguments.output,
        arguments.sources,
        arguments.stats,
        arguments.allow_large_change,
    )
