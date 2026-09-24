#!/usr/bin/env python3
"""PreToolUse hook utility: blocks destructive shell commands."""

import json
import sys

DENYLIST = (
    "rm -rf /",
    "rm -rf ~",
    "mkfs",
    "dd if=",
    ":(){",
    "chmod -R 777 /",
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    command = ""
    try:
        command = payload["toolCall"]["args"]["CommandLine"]
    except Exception:
        return

    if not isinstance(command, str):
        return

    normalized = " ".join(command.split())

    for pattern in DENYLIST:
        if pattern in normalized:
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": (
                            f"このコマンドは全社エージェント開発規約により禁止されています: {pattern}\n"
                            "破壊的な操作は実行できません。"
                            "目的を達成する別の手段を検討してください。"
                        ),
                    },
                    ensure_ascii=False,
                )
            )
            return


if __name__ == "__main__":
    main()
