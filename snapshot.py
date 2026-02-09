import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from decouple import config

MAIN_DIR = Path(config("MAIN_DIR"))
SNAPSHOT_FILE = Path(config("SNAPSHOT_FILE"))

# 별로 의미없는 디렉토리
EXCLUDE_DIRS = {
    "Library",
    ".git",
    ".venv",
    "__pycache__",
    ".idea",
    ".vscode",
    ".streamlit",
    ".devcontainer",
}
# macOS 패키지 확장자
PACKAGE_EXTENSIONS = {
    ".app",
    ".framework",
    ".bundle",
    ".pkg",
}

def get_used_file(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ['mdls', '-name', 'kMDItemLastUsedDate', str(path)],
            capture_output=True,
            text=True, 
            timeout=2 # mdls 명령어가 2초이상 지속되면 다음껄로 넘어감
        )
        output = result.stdout.strip()
        if '=' not in output:
            return None
        return output.split('=', 1)[1].strip()
    except Exception:
        return None

def create_snapshot() -> dict:
    start_time = time.perf_counter()

    snapshot = {
        "snapshot_time" : datetime.now().isoformat(),
        "items" : {}
    }
    for index, item in enumerate(MAIN_DIR.rglob('*'), start=1):
        if index % 100 == 0:
            print(f"{index}개 처리완료")
        if item.name.startswith('.'):
            continue
        if any(part in EXCLUDE_DIRS for part in item.parts):
            continue
        # 디렉토리는 패키지가 아닌 경우 mdls 대상에서 제외
        if item.is_dir() and not any(part.endswith(ext) for ext in PACKAGE_EXTENSIONS for part in item.parts):
            continue
        # 최상위 디렉토리인지 확인하는 로직
        if any(part.endswith(ext) for ext in PACKAGE_EXTENSIONS for part in item.parts):
            if (
                item.is_dir() 
                and item.suffix in PACKAGE_EXTENSIONS
                and not any(parent.suffix in PACKAGE_EXTENSIONS for parent in item.parents)
                ):
                last_used = get_used_file(item)
                if last_used:
                    snapshot['items'][str(item)] = last_used
            continue
        # 일반 파일만 mdls 호출 (디렉토리는 제외)
        if not item.is_file():
            continue

        last_used = get_used_file(item)
        if last_used:
            snapshot['items'][str(item)] = last_used
            
    end_time = time.perf_counter()
    time_cost = end_time - start_time
    print(f'스냅샷 완료: 총 {index}개 검사, 소요 시간 {time_cost:.2f}초')
    return snapshot

if __name__ == "__main__":
    snapshot = create_snapshot()
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)