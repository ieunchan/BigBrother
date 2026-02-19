import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from decouple import config

MAIN_DIR = Path(config('MAIN_DIR'))
SNAPSHOT_FILE = Path(config('SNAPSHOT_FILE'))
PROJECT_DIR = Path(__file__).parent.resolve()

# 검사하지 않을 디렉토리 목록
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
# 1️ 파일 시스템 변경 시간 (mtime)
def get_mtime(path: Path) -> str | None:
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return None
# 2️ Finder 기반 최근 사용일
def get_last_used(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ['mdls', '-name', 'kMDItemLastUsedDate', str(path)],
            capture_output=True,
            text=True,
            timeout=2
        )
        output = result.stdout.strip()
        if '=' not in output:
            return None
        value = output.split('=', 1)[1].strip()
        if value == '(null)':
            return None
        return value

    except Exception:
        return None
# 3️ 스냅샷 생성
def create_snapshot() -> dict:
    start_time = time.perf_counter()
    snapshot = {'snapshot_time': {}, 'items': {}}
    for index, item in enumerate(MAIN_DIR.rglob('*'), start=1):
        if index % 100 == 0:
            print(f'현재 {index}개 처리 완료')
        if item.name.startswith('.'):
            continue
        if any(part in EXCLUDE_DIRS for part in item.parts):
            continue
        mtime = get_mtime(item)
        last_used = get_last_used(item)
        
        if mtime is not None or last_used is not None:
            snapshot['items'][str(item)] = {
                '수정된 시간' : mtime,
                '최근 사용일' : last_used
            }
    end_time = time.perf_counter()
    print(f'스냅샷 완료: 총 {index}개의 파일 검사, 소요시간: {end_time - start_time:.2f}초 소요.')
    return snapshot
# 4️ 이전 스냅샷 로딩
def load_previous_snapshot(snapshot_path: Path) -> dict:
    if not snapshot_path.exists():
        return None
    with open(snapshot_path, 'r', encoding='utf-8') as pre_file:
        return json.load(pre_file)
# 5️ 스냅샷 비교
def compare_snapshots(pre: dict, curr: dict) -> dict:
    pre_item = pre.get('items', {})
    curr_item = curr.get('items', {})

    added = {k: v for k,v in curr_item.items() if k not in pre_item}
    removed = {k: v for k,v in pre_item.items() if k not in curr_item}
    updated = {}

    for path in curr_item:
        if path.startswith(str(PROJECT_DIR)):
            continue
        if path in pre_item:
            pre_data = pre_item[path]
            curr_data = curr_item[path]
            if pre_data != curr_data:
                updated[path] = {
                    'before': pre_data,
                    'after' : curr_data
                }
    return {
        'compare_time' : datetime.now().isoformat(),
        'pre_snapshot_time' : pre.get('snapshot_time'),
        'curr_snapshot_time' : curr.get('snapshot_time'),
        'Added' : added,
        'Removed' : removed,
        'Updated' : updated
    }
# 6️ 실행부
if __name__ == '__main__':
    snapshot = create_snapshot()
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as file:
        json.dump(snapshot, file, ensure_ascii=False, indent=2)
    
    pre_snapshot_path = SNAPSHOT_FILE.with_suffix('.pre.json')
    pre_snapshot = load_previous_snapshot(pre_snapshot_path)

    if pre_snapshot is not None:
        result = compare_snapshots(pre_snapshot, snapshot)
        result_file = SNAPSHOT_FILE.with_suffix('.compare.json')
        
        with open(result_file, 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
        print("스냅샷 결과 생성 완료")
    
    SNAPSHOT_FILE.replace(pre_snapshot_path)