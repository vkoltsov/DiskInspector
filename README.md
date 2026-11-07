# DiskInspector

[![CI](https://github.com/vkoltsov/DiskInspector/actions/workflows/ci.yml/badge.svg)](https://github.com/vkoltsov/DiskInspector/actions/workflows/ci.yml)

Утилита на Python для анализа занятого места на диске.

Рекурсивно сканирует указанный каталог и выводит ТОП-10 каталогов
2-го и 3-го уровня, занимающих больше всего места, с размером и долей
в процентах от общего объёма.

## Использование

```bash
python disk_inspector.py C:\            # весь диск C:
python disk_inspector.py D:\Games -n 20 # конкретный каталог, топ-20
```

- `ROOT` — корневой каталог сканирования (по умолчанию `C:\`)
- `-n` / `--top` — размер топа (по умолчанию 10)

## Особенности

- Один проход по дереву каталогов (`os.walk`), без повторного сканирования
- Размеры каталогов считаются с учётом всех вложенных подкаталогов
- Символические ссылки пропускаются (нет двойного подсчёта и зацикливания)
- Недоступные файлы пропускаются с подсчётом их количества

Для сканирования целого системного диска рекомендуется запуск от имени администратора.

## Тесты и CI

Проект использует GitHub Actions (`.github/workflows/ci.yml`). При каждом пуше
и pull request в `main` запускаются:

- **Lint** — проверка кода через [ruff](https://docs.astral.sh/ruff/)
- **Smoke test** — матрица Ubuntu/Windows × Python 3.10/3.12: строится тестовое
  дерево каталогов с файлами известного размера, скрипт запускается на нём,
  и проверяется корректность топа каталогов 2-го и 3-го уровня

Запустить проверки локально:

```bash
# Линт
pip install ruff
ruff check disk_inspector.py

# Smoke test (Linux / Git Bash)
mkdir -p test_root/level1_a/big_dir test_root/level1_a/small_dir test_root/level1_b/medium_dir
dd if=/dev/zero of=test_root/level1_a/big_dir/big.bin bs=1M count=20
dd if=/dev/zero of=test_root/level1_b/medium_dir/mid.bin bs=1M count=10
python disk_inspector.py test_root -n 5
```

В выводе первым в топе 2-го уровня должен быть `test_root\level1_a\big_dir`.
