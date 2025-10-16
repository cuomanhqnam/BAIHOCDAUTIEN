"""Daily task tracking application.

This script provides a simple command line interface for managing
personal daily tasks. Tasks are stored in a JSON file next to this
script and include a textual description, a scheduled date, and their
completion status. The CLI supports adding tasks, listing them, marking
completion, and removing finished items.

Usage examples:
    python daily_tracker.py add "Đọc sách" --date 2024-05-01
    python daily_tracker.py list --date today
    python daily_tracker.py done 3
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable, List, Optional

DATA_FILE = Path(__file__).with_name("tasks.json")
DATE_FMT = "%Y-%m-%d"


class TaskError(RuntimeError):
    """Custom error for task operations."""


@dataclass
class Task:
    """Representation of a tracked task."""

    task_id: int
    description: str
    scheduled_for: str
    completed: bool = field(default=False)

    def matches_date(self, date: Optional[str]) -> bool:
        if date is None:
            return True
        return self.scheduled_for == date

    def matches_state(self, completed: Optional[bool]) -> bool:
        if completed is None:
            return True
        return self.completed is completed

    @classmethod
    def from_dict(cls, raw: dict) -> "Task":
        return cls(
            task_id=int(raw["task_id"]),
            description=str(raw["description"]),
            scheduled_for=str(raw["scheduled_for"]),
            completed=bool(raw.get("completed", False)),
        )


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def load_tasks() -> List[Task]:
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise TaskError(
            "Không thể đọc dữ liệu nhiệm vụ. Hãy kiểm tra file tasks.json"
        ) from exc
    return [Task.from_dict(item) for item in data]


def save_tasks(tasks: Iterable[Task]) -> None:
    serialised = [asdict(task) for task in tasks]
    DATA_FILE.write_text(json.dumps(serialised, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Task management actions
# ---------------------------------------------------------------------------

def next_task_id(tasks: Iterable[Task]) -> int:
    current = [task.task_id for task in tasks]
    return max(current, default=0) + 1


def add_task(description: str, scheduled_for: str) -> Task:
    tasks = load_tasks()
    new_id = next_task_id(tasks)
    new_task = Task(task_id=new_id, description=description, scheduled_for=scheduled_for)
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


def list_tasks(date: Optional[str], show_all: bool, completed: Optional[bool]) -> List[Task]:
    tasks = load_tasks()
    if not show_all:
        tasks = [task for task in tasks if task.matches_date(date)]
    if completed is not None:
        tasks = [task for task in tasks if task.matches_state(completed)]
    return sorted(tasks, key=lambda task: (task.scheduled_for, task.task_id))


def update_task_state(task_id: int, completed: bool) -> Task:
    tasks = load_tasks()
    for task in tasks:
        if task.task_id == task_id:
            task.completed = completed
            save_tasks(tasks)
            return task
    raise TaskError(f"Không tìm thấy nhiệm vụ với mã {task_id}.")


def remove_task(task_id: int) -> Task:
    tasks = load_tasks()
    for index, task in enumerate(tasks):
        if task.task_id == task_id:
            removed = tasks.pop(index)
            save_tasks(tasks)
            return removed
    raise TaskError(f"Không tìm thấy nhiệm vụ với mã {task_id}.")


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def parse_date(value: str) -> str:
    if value.lower() == "today":
        return _dt.date.today().strftime(DATE_FMT)
    try:
        _dt.datetime.strptime(value, DATE_FMT)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Ngày không hợp lệ: '{value}'. Định dạng đúng là YYYY-MM-DD."
        ) from exc
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ứng dụng theo dõi công việc hằng ngày")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Thêm nhiệm vụ mới")
    add_parser.add_argument("description", help="Nội dung nhiệm vụ")
    add_parser.add_argument(
        "--date",
        default=_dt.date.today().strftime(DATE_FMT),
        type=parse_date,
        help="Ngày thực hiện (YYYY-MM-DD hoặc 'today'). Mặc định là hôm nay.",
    )

    list_parser = subparsers.add_parser("list", help="Liệt kê nhiệm vụ")
    list_parser.add_argument(
        "--date",
        default=_dt.date.today().strftime(DATE_FMT),
        type=parse_date,
        help="Ngày cần xem (YYYY-MM-DD hoặc 'today').",
    )
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Hiển thị tất cả nhiệm vụ bất kể ngày nào.",
    )
    state_group = list_parser.add_mutually_exclusive_group()
    state_group.add_argument("--completed", action="store_true", help="Chỉ hiển thị nhiệm vụ đã hoàn thành.")
    state_group.add_argument("--pending", action="store_true", help="Chỉ hiển thị nhiệm vụ chưa hoàn thành.")

    done_parser = subparsers.add_parser("done", help="Đánh dấu hoàn thành")
    done_parser.add_argument("task_id", type=int, help="Mã nhiệm vụ")
    done_parser.add_argument(
        "--undone",
        action="store_true",
        help="Bỏ đánh dấu hoàn thành (trở về trạng thái chưa làm).",
    )

    remove_parser = subparsers.add_parser("remove", help="Xoá nhiệm vụ")
    remove_parser.add_argument("task_id", type=int, help="Mã nhiệm vụ cần xoá")

    return parser


def render_tasks(tasks: Iterable[Task]) -> str:
    lines = []
    for task in tasks:
        status = "✅" if task.completed else "⬜"
        lines.append(f"[{task.task_id:03d}] {status} {task.scheduled_for} - {task.description}")
    if not lines:
        return "Không có nhiệm vụ nào khớp với yêu cầu."
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "add":
            new_task = add_task(args.description, args.date)
            print(f"Đã thêm nhiệm vụ {new_task.task_id}: {new_task.description}")
        elif args.command == "list":
            completed_state = None
            if args.completed:
                completed_state = True
            elif args.pending:
                completed_state = False
            tasks = list_tasks(args.date, args.all, completed_state)
            print(render_tasks(tasks))
        elif args.command == "done":
            updated = update_task_state(args.task_id, not args.undone)
            state = "hoàn thành" if updated.completed else "chưa hoàn thành"
            print(f"Nhiệm vụ {updated.task_id} hiện {state}.")
        elif args.command == "remove":
            removed = remove_task(args.task_id)
            print(f"Đã xoá nhiệm vụ {removed.task_id}: {removed.description}")
        else:  # pragma: no cover - defensive
            parser.error("Lệnh không được hỗ trợ")
            return 2
    except TaskError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
