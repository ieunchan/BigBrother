from pathlib import Path
import subprocess
import json
from datetime import datetime

MAIN_DIR = Path("/Users/ieunchan/Desktop")
SNAPSHOT_FILE = Path("file_snapshot.json")

# Finder 기준으로 의미 없는 디렉토리
EXCLUDE_DIRS = {
    "Library",
    ".git",
    ".venv",
    "__pycache__",
    ".idea",
    ".vscode",
    ".streamlit",
    ".devcontainer",
    ".app",
    ""
}

# macOS 패키지 확장자
PACKAGE_EXTENSIONS = {
    ".app",
    ".framework",
    ".bundle",
    ".pkg",
}

def get_last_used_file(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["mdls", "-name", "kMDItemLastUsedDate", str(path)],
            capture_output=True,
            text=True,
            timeout=2,
        )

        output = result.stdout.strip()
        if "=" not in output:
            return None

        return output.split("=", 1)[1].strip()

    except Exception:
        return None

# ===============================
# 스냅샷 생성
# ===============================

def create_snapshot() -> dict:
    snapshot = {
        "snapshot_time": datetime.now().isoformat(),
        "items": {}
    }

    print("스냅샷 시작")

    for idx, item in enumerate(MAIN_DIR.rglob("*"), start=1):
        if idx % 500 == 0:
            print(f"{idx}개 처리 중...")

        # 1️⃣ 숨김 파일 / 디렉토리 제외
        if item.name.startswith("."):
            continue

        # 2️⃣ 개발 / 시스템 디렉토리 제외 (.idea, .vscode 등)
        if any(part in EXCLUDE_DIRS for part in item.parts):
            continue

        # 3️⃣ macOS 패키지 내부 진입 차단
        if any(part.endswith(ext) for ext in PACKAGE_EXTENSIONS for part in item.parts):
            # 최상위 패키지만 기록
            if (
                item.is_dir()
                and item.suffix in PACKAGE_EXTENSIONS
                and not any(parent.suffix in PACKAGE_EXTENSIONS for parent in item.parents)
            ):
                last_used = get_last_used_file(item)
                if last_used:
                    snapshot["items"][str(item)] = last_used
            continue

        # 4️⃣ 일반 파일만 기록
        if not item.is_file():
            continue

        last_used = get_last_used_file(item)
        if last_used:
            snapshot["items"][str(item)] = last_used

    print("스냅샷 완료")
    return snapshot

# ===============================
# 저장
# ===============================

def save_snapshot(snapshot: dict):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"저장 완료: {SNAPSHOT_FILE.resolve()}")

if __name__ == "__main__":
    snapshot = create_snapshot()
    save_snapshot(snapshot)