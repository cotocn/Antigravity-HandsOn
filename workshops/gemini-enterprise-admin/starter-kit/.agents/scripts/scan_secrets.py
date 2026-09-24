#!/usr/bin/env python3
"""Stop hook utility: checks whether secret literals are hardcoded in app/."""

import json
import pathlib
import re
import sys
import tempfile

SECRET_PATTERN = re.compile(
    r"""(\w*(?:KEY|TOKEN|SECRET|PASSWORD))\s*=\s*["']([^"']{16,})["']""",
    re.IGNORECASE,
)

MAX_BLOCKS_PER_CONVERSATION = 3

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN_TARGET = PROJECT_ROOT / "app"


def find_secrets() -> tuple[list[str], str]:
    """Scan app/ for hardcoded secret literals and return findings and first variable name."""
    findings = []
    first_var = "API_KEY"
    if not SCAN_TARGET.is_dir():
        return findings, first_var

    for path in sorted(SCAN_TARGET.rglob("*.py")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for lineno, line in enumerate(lines, start=1):
            match = SECRET_PATTERN.search(line)
            if match:
                rel = path.relative_to(PROJECT_ROOT)
                var_name = match.group(1)
                if not findings:
                    first_var = var_name
                findings.append(f"  - {rel}:{lineno}  変数 {var_name}")
    return findings, first_var


def block_count(conversation_id: str) -> int:
    if not conversation_id:
        return 0
    marker = pathlib.Path(tempfile.gettempdir()) / f"scan_secrets_{conversation_id}.count"
    try:
        count = int(marker.read_text()) if marker.exists() else 0
        marker.write_text(str(count + 1))
        return count
    except Exception:
        return 0


def main() -> None:
    conversation_id = ""
    try:
        payload = json.load(sys.stdin)
        conversation_id = str(payload.get("conversationId", ""))
    except Exception:
        pass

    try:
        findings, first_var = find_secrets()
    except Exception:
        return

    if not findings:
        return

    if block_count(conversation_id) >= MAX_BLOCKS_PER_CONVERSATION:
        return

    reason = (
        "【ガードレールによる差し戻し】\n"
        "シークレットがソースコードに直書きされています。\n\n"
        + "\n".join(findings)
        + "\n\n"
        "全社エージェント開発規約に従い、環境変数から読み込むよう修正してください。\n"
        "例:\n"
        f'    {first_var} = os.environ.get("{first_var}", "")\n\n'
        "修正したうえで、再度作業を完了してください。"
    )

    print(json.dumps({"decision": "continue", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    main()
