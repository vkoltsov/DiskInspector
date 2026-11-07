"""
Disk Inspector — анализ занятого места на диске.

Рекурсивно сканирует указанный корневой каталог и выводит
ТОП-10 каталогов 2-го и 3-го уровня (относительно корня),
занимающих больше всего места.

Пример уровней для корня C:\\ :
    C:\\Users            — 1 уровень
    C:\\Users\\Vladimir  — 2 уровень
    C:\\Users\\Vladimir\\Documents — 3 уровень

Использование:
    python disk_inspector.py [ROOT] [-n N]

    ROOT  — корневой каталог сканирования (по умолчанию C:\\)
    -n    — размер топа (по умолчанию 10)
"""

import argparse
import os
import sys
import time
from collections import defaultdict


def format_size(size_bytes: int) -> str:
    """Человекочитаемый размер: 1.5 GB, 320 MB и т.п."""
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if size < 1024.0 or unit == "PB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def scan_sizes(root: str):
    """
    Один проход по дереву каталогов.

    Возвращает словарь {путь_каталога: суммарный размер с учётом подкаталогов}.
    Размер каждого файла добавляется всем его родительским каталогам,
    поэтому достаточно одного прохода os.walk.
    """
    root = os.path.abspath(root)
    dir_sizes = defaultdict(int)
    errors = 0
    files_seen = 0

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Не заходим в символические ссылки, чтобы не считать дважды
        dirnames[:] = [d for d in dirnames
                       if not os.path.islink(os.path.join(dirpath, d))]

        dir_files_size = 0
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                if os.path.islink(fp):
                    continue
                dir_files_size += os.lstat(fp).st_size
                files_seen += 1
            except (OSError, PermissionError):
                errors += 1

        # Накопить размер файлов этого каталога во всех предках до корня
        current = dirpath
        while True:
            dir_sizes[current] += dir_files_size
            if current == root:
                break
            current = os.path.dirname(current)

    return dir_sizes, errors, files_seen


def relative_depth(path: str, root: str) -> int:
    """Глубина каталога относительно корня: root -> 0, root\\a -> 1 и т.д."""
    rel = os.path.relpath(path, root)
    if rel == ".":
        return 0
    return rel.count(os.sep) + 1


def print_top(dir_sizes: dict, root: str, depth: int, top_n: int):
    """Выводит ТОП-N каталогов заданного уровня по занятому месту."""
    candidates = [(p, s) for p, s in dir_sizes.items()
                  if relative_depth(p, root) == depth]
    candidates.sort(key=lambda item: item[1], reverse=True)

    print(f"\n{'=' * 72}")
    print(f"  ТОП-{top_n} каталогов {depth}-го уровня по размеру")
    print(f"{'=' * 72}")

    if not candidates:
        print("  (каталогов этого уровня не найдено)")
        return

    total_root = dir_sizes.get(root, 0)
    print(f"  {'#':>3}  {'Размер':>12}  {'% от корня':>10}  Путь")
    print(f"  {'-' * 3}  {'-' * 12}  {'-' * 10}  {'-' * 40}")

    for i, (path, size) in enumerate(candidates[:top_n], 1):
        pct = (size / total_root * 100) if total_root else 0.0
        print(f"  {i:>3}  {format_size(size):>12}  {pct:>9.1f}%  {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Анализ занятого места: ТОП каталогов 2 и 3 уровня.")
    parser.add_argument("root", nargs="?", default=r"C:\\",
                        help="Корневой каталог сканирования (по умолчанию C:\\)")
    parser.add_argument("-n", "--top", type=int, default=10,
                        help="Размер топа (по умолчанию 10)")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Ошибка: каталог не найден: {root}", file=sys.stderr)
        sys.exit(2)

    print(f"Сканирование: {root}")
    started = time.perf_counter()

    dir_sizes, errors, files_seen = scan_sizes(root)

    elapsed = time.perf_counter() - started
    total = dir_sizes.get(root, 0)

    print(f"\nГотово за {elapsed:.1f} с. Файлов: {files_seen:,}, "
          f"суммарный размер: {format_size(total)}")
    if errors:
        print(f"Внимание: {errors} файлов пропущено (нет доступа / ошибки чтения)")

    print_top(dir_sizes, root, depth=2, top_n=args.top)
    print_top(dir_sizes, root, depth=3, top_n=args.top)


if __name__ == "__main__":
    main()
