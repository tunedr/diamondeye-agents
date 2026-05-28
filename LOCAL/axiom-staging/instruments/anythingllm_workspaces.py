#!/usr/bin/env python3
"""
Ensure the five required AnythingLLM workspaces exist.

Uses the developer API exposed by AnythingLLM. The script checks each
workspace slug and creates it with the documented workspace name when missing.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import json
from dataclasses import dataclass
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Workspace:
    name: str

    @property
    def slug(self) -> str:
        return slugify(self.name)


WORKSPACES: List[Workspace] = [
    Workspace("DiamondEye-Research"),
    Workspace("Infrastructure"),
    Workspace("MediaMind"),
    Workspace("Publishing"),
    Workspace("Inspections"),
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def build_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def workspace_exists(base_url: str, token: str, slug: str) -> bool:
    request = Request(
        f"{base_url.rstrip('/')}/api/v1/workspace/{slug}",
        headers=build_headers(token),
        method="GET",
    )
    try:
        with urlopen(request, timeout=20) as response:
            return response.status == 200
    except HTTPError as exc:
        if exc.code == 404:
            return False
        raise RuntimeError(f"workspace check for {slug} failed: HTTP {exc.code} {exc.read().decode('utf-8', 'ignore')}") from exc
    except URLError as exc:
        raise RuntimeError(f"workspace check for {slug} failed: {exc}") from exc


def create_workspace(base_url: str, token: str, workspace: Workspace) -> None:
    payload = json.dumps({"name": workspace.name}).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}/api/v1/workspace/new",
        data=payload,
        headers=build_headers(token),
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            if response.status not in (200, 201):
                raise RuntimeError(
                    f"workspace create for {workspace.name} failed: HTTP {response.status}"
                )
    except HTTPError as exc:
        if exc.code not in (200, 201):
            raise RuntimeError(
                f"workspace create for {workspace.name} failed: HTTP {exc.code} {exc.read().decode('utf-8', 'ignore')}"
            ) from exc
    except URLError as exc:
        raise RuntimeError(f"workspace create for {workspace.name} failed: {exc}") from exc


def ensure_workspaces(base_url: str, token: str, workspaces: Iterable[Workspace]) -> None:
    for workspace in workspaces:
        if workspace_exists(base_url, token, workspace.slug):
            print(f"ok: {workspace.name}")
            continue
        create_workspace(base_url, token, workspace)
        print(f"created: {workspace.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ANYTHINGLLM_URL", "http://anythingllm:3001"),
        help="AnythingLLM base URL.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("ANYTHINGLLM_AUTH_TOKEN", "") or os.environ.get("AUTH_TOKEN", ""),
        help="AnythingLLM developer API bearer token.",
    )
    args = parser.parse_args()

    if not args.token:
        print("missing AnythingLLM token", file=sys.stderr)
        return 1

    ensure_workspaces(args.base_url, args.token, WORKSPACES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
