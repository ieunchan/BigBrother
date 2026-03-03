import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from decouple import config

FILE_MAIN_DIR = Path(config("FILE_MAIN_DIR"))
FILE_STATUS = Path(config("FILE_STATUS"))
PROJECT_DIR = Path(__file__).parent.resolve()

# 이 모듈은 "파일 시스템 변화 감지"를 담당한다.
# 단순히 파일 존재 여부만이 아니라
# 1) 수정 시간(mtime)
# 2) Finder 기준 최근 사용일(mdls)
# 을 함께 추적하여 보다 현실적인 사용 흔적을 기록한다.

# 감시 대상에서 제외할 디렉토리 목록
# 시스템 디렉토리 / 개발 관련 폴더 / 캐시 영역은 노이즈가 많기 때문에 제외한다.
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

# 파일 시스템의 "수정 시간"을 가져온다.
# mtime은 파일이 실제로 변경되었는지를 판단하는 핵심 지표다.
def get_mtime(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

# Finder 기준 "최근 사용일"을 가져온다.
# macOS는 mdls를 통해 열람 흔적을 일부 추적할 수 있다.
# mtime과 달리, 단순 열람도 감지 가능하다는 점이 핵심이다.
def get_last_used(path: Path) -> str | None:
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
        value = output.split("=", 1)[1].strip()
        if value == "(null)":
            return None
        return value
    except Exception:
        return None

# 현재 시점의 파일 상태를 스냅샷으로 기록한다.
# 이 스냅샷은 이후 비교를 위한 기준 데이터가 된다.
def create_snapshot() -> dict:
    snapshot = {
        "snapshot_time": datetime.now().isoformat(),
        "items": {},
    }

    count = 0

    for item in FILE_MAIN_DIR.rglob("*"):
        count += 1

        # 숨김 파일은 기본적으로 제외
        if item.name.startswith("."):
            continue

        # 노이즈가 많은 디렉토리는 제외
        if any(part in EXCLUDE_DIRS for part in item.parts):
            continue

        # BigBrother 자체 프로젝트 영역은 감시하지 않는다.
        # 자기 자신을 감시하면 무한 변경 로그가 발생한다.
        if str(item).startswith(str(PROJECT_DIR)):
            continue

        # logs 디렉토리 전체는 감시 제외 (자기 로그 변경으로 인한 노이즈 제거)
        if "logs" in item.parts:
            continue

        mtime = get_mtime(item)
        last_used = get_last_used(item)

        # 둘 중 하나라도 존재하면 기록
        if mtime is not None or last_used is not None:
            snapshot["items"][str(item)] = {
                "수정된 시간": mtime,
                "최근 사용일": last_used,
            }

    print(f"스냅샷 완료: 총 {count}개 검사")
    return snapshot

# 직전 실행 시 저장해둔 스냅샷을 로드한다.
# 이전 상태와 비교하기 위한 기준 데이터다.
def load_previous_snapshot(snapshot_path: Path) -> dict | None:
    if not snapshot_path.exists():
        return None
    with open(snapshot_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 이전 스냅샷과 현재 스냅샷을 비교한다.
# 파일 추가 / 삭제 / 수정 / 열람 변화를 모두 탐지한다.
def compare_snapshots(pre: dict, curr: dict) -> dict:
    pre_items = pre.get("items", {})
    curr_items = curr.get("items", {})

    added = {k: v for k, v in curr_items.items() if k not in pre_items}
    removed = {k: v for k, v in pre_items.items() if k not in curr_items}
    updated = {}

    for path in curr_items:
        if path in pre_items:
            pre_data = pre_items[path]
            curr_data = curr_items[path]

            # 최근 사용일 또는 수정 시간이 달라졌다면
            # 파일이 사용되었거나 변경된 것으로 간주한다.
            if (
                pre_data.get("최근 사용일") != curr_data.get("최근 사용일")
                or pre_data.get("수정된 시간") != curr_data.get("수정된 시간")
            ):
                updated[path] = {
                    "before": pre_data,
                    "after": curr_data,
                }

    return {
        "compare_time": datetime.now().isoformat(),
        "pre_snapshot_time": pre.get("snapshot_time"),
        "curr_snapshot_time": curr.get("snapshot_time"),
        "Added": added,
        "Removed": removed,
        "Updated": updated,
    }

# 메인에서 호출되는 지속 감시 루프
# interval 초마다 스냅샷을 찍고
# 이전 상태와 비교하여 변화가 있다면 기록한다.
def start_file_monitor(interval: int = 10):
    pre_snapshot_path = FILE_STATUS.with_suffix(".pre.json")

    while True:
        snapshot = create_snapshot()

        current_path = FILE_STATUS.with_suffix(".current.json")
        with open(current_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        pre_snapshot = load_previous_snapshot(pre_snapshot_path)

        if pre_snapshot is not None:
            result = compare_snapshots(pre_snapshot, snapshot)
            result_path = FILE_STATUS.with_suffix(".compare.json")
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("스냅샷 비교 완료")

        # 이번 스냅샷을 다음 비교의 기준으로 교체
        current_path.replace(pre_snapshot_path)

        time.sleep(interval)