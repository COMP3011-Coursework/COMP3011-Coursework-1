#!/usr/bin/env python3
"""
Convert Claude Code JSONL session logs to Markdown.

Usage:
    python convert_jsonl_to_md.py [--src SRC_DIR] [--out OUT_DIR]

Defaults:
    --src  ~/.claude/projects/<this-project>/
    --out  ./  (same directory as this script)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

THIS_PROJECT_KEY = (
    "-Users-andy-Library-CloudStorage-OneDrive-UniversityofLeeds"
    "-Years-202526-2--COMP3011-Web-Services-and-Web-Data-Coursework-1-COMP3011-Coursework-1"
)
DEFAULT_SRC = Path.home() / ".claude" / "projects" / THIS_PROJECT_KEY


def clean_user_text(text: str) -> str:
    """Strip IDE context tags injected by Claude Code."""
    text = re.sub(r"<ide_opened_file>.*?</ide_opened_file>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ide_selection>.*?</ide_selection>", "", text, flags=re.DOTALL)
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL)
    return text.strip()


def extract_messages(jsonl_path: Path) -> list[dict]:
    """Return a list of {role, text, timestamp} dicts from a JSONL session file."""
    messages = []
    with open(jsonl_path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type")
            if msg_type not in ("user", "assistant"):
                continue

            message = obj.get("message", {})
            role = message.get("role", msg_type)
            timestamp = obj.get("timestamp", "")
            content = message.get("content", [])

            # content may be a plain string (rare) or a list of content blocks
            if isinstance(content, str):
                if role == "user":
                    text = clean_user_text(content)
                    if text:
                        messages.append({"role": role, "text": text, "timestamp": timestamp})
                continue

            text_parts = []
            is_tool_only = True  # True if every block is tool-related

            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")

                if btype == "text":
                    is_tool_only = False
                    text_parts.append(block.get("text", ""))
                elif btype == "thinking":
                    # Skip internal thinking blocks
                    pass
                elif btype == "tool_use":
                    # Summarise tool calls briefly
                    tool_name = block.get("name", "unknown")
                    tool_input = block.get("input", {})
                    summary = f"*[Tool call: `{tool_name}`"
                    if "command" in tool_input:
                        cmd = str(tool_input["command"])[:120]
                        summary += f" — `{cmd}`"
                    elif "file_path" in tool_input:
                        summary += f" — `{tool_input['file_path']}`"
                    elif "pattern" in tool_input:
                        summary += f" — `{tool_input['pattern']}`"
                    summary += "]*"
                    text_parts.append(summary)
                elif btype == "tool_result":
                    # Skip tool results (they're assistant feedback, not human messages)
                    pass

            # For user messages that are purely tool_result blocks, skip them
            if role == "user" and all(
                isinstance(b, dict) and b.get("type") == "tool_result"
                for b in content
                if isinstance(b, dict)
            ):
                continue

            combined = "\n\n".join(p for p in text_parts if p.strip())
            if role == "user":
                combined = clean_user_text(combined)
            if combined.strip():
                messages.append({"role": role, "text": combined, "timestamp": timestamp})

    return messages


def session_title(messages: list[dict], session_id: str) -> str:
    """Derive a short title from the first human message."""
    for m in messages:
        if m["role"] == "user":
            first_line = m["text"].splitlines()[0].strip()
            # Truncate if too long
            if len(first_line) > 80:
                first_line = first_line[:77] + "..."
            return first_line
    return session_id


def format_timestamp(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return ts


def jsonl_to_markdown(jsonl_path: Path) -> str:
    session_id = jsonl_path.stem
    messages = extract_messages(jsonl_path)
    if not messages:
        return ""

    title = session_title(messages, session_id)
    first_ts = format_timestamp(messages[0]["timestamp"]) if messages else ""
    last_ts = format_timestamp(messages[-1]["timestamp"]) if messages else ""

    lines = [
        f"# {title}",
        "",
        f"**Session ID:** `{session_id}`  ",
        f"**Started:** {first_ts}  ",
        f"**Ended:** {last_ts}  ",
        f"**Source:** Claude Code (local session log)",
        "",
        "---",
        "",
    ]

    for msg in messages:
        role_label = "**Human**" if msg["role"] == "user" else "**Assistant**"
        ts_label = f" _{format_timestamp(msg['timestamp'])}_" if msg["timestamp"] else ""
        lines.append(f"## {role_label}{ts_label}")
        lines.append("")
        lines.append(msg["text"])
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def convert_all(src_dir: Path, out_dir: Path) -> list[dict]:
    """Convert all JSONL files in src_dir. Return metadata list for README."""
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = []

    jsonl_files = sorted(src_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    print(f"Found {len(jsonl_files)} JSONL files in {src_dir}")

    for jsonl_path in jsonl_files:
        session_id = jsonl_path.stem
        md_path = out_dir / f"session-{session_id}.md"

        md_content = jsonl_to_markdown(jsonl_path)
        if not md_content:
            print(f"  Skipping {session_id} (no extractable messages)")
            continue

        md_path.write_text(md_content, encoding="utf-8")

        # Extract first line as title
        first_line = md_content.splitlines()[0].lstrip("# ").strip()
        # Get mtime as approximate session date
        mtime = datetime.fromtimestamp(jsonl_path.stat().st_mtime, tz=timezone.utc)
        metadata.append(
            {
                "file": md_path.name,
                "title": first_line,
                "date": mtime.strftime("%Y-%m-%d"),
                "session_id": session_id,
            }
        )
        print(f"  Written {md_path.name}")

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Convert Claude Code JSONL logs to Markdown.")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="Source directory of JSONL files")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent, help="Output directory for Markdown files")
    args = parser.parse_args()

    if not args.src.exists():
        print(f"Source directory not found: {args.src}", file=sys.stderr)
        sys.exit(1)

    metadata = convert_all(args.src, args.out)
    print(f"\nConverted {len(metadata)} sessions to {args.out}")


if __name__ == "__main__":
    main()
