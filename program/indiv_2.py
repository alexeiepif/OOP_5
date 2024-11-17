#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Разработайте аналог утилиты tree в Linux.
# Используйте возможности модуля argparse для
# управления отображением дерева каталогов файловой системы.
# Добавьте дополнительные уникальные возможности в данный программный продукт.
# Выполнить индивидуальное задание 2 лабораторной работы 2.19,
# добавив аннтотации типов.
# Выполнить проверку программы с помощью утилиты mypy.

import argparse
import sys
from pathlib import Path
from typing import Any

from colorama import Fore, Style


def print_tree(
    tree: dict[Path, Any], lines: bool, level: int = 0, levels: list[bool] = []
) -> None:
    """
    Отрисовка дерева каталогов в виде иерархической структуры.
    """
    if not tree:
        return

    for i, (node, child) in enumerate(tree.items()):
        if i == len(tree) - 1 and level != 0:
            levels[level - 1] = False
        if not lines:
            branch = "".join("│   " if lev else "    " for lev in levels[:-1])
            branch += "└── " if i == len(tree) - 1 else "├── "
        else:
            branch = ""
        if level == 0:
            # Синий цвет для корневой папки
            print(Fore.BLUE + str(node) + Style.RESET_ALL)
        else:
            # Для файлов: зеленый цвет, для папок: желтый цвет
            color = Fore.GREEN if child is not None else Fore.YELLOW
            print(branch + color + str(node) + Style.RESET_ALL)

        print_tree(child, lines, level + 1, levels + [True])


def tree(directory: Path, args: argparse.Namespace) -> None:
    """
    Создание структуры дерева каталогов в виде словаря.
    """

    sw = False
    files = 0
    folders = 0
    folder_tree: dict[Path, Any] = {}
    count = 0

    path_list: list[Path] = []
    all_files = args.a
    max_depth = args.max_depth
    only_dir = args.d
    counter = 0
    for path in directory.rglob("*"):
        try:
            if counter < 100000:
                counter += 1
            else:
                sw = True
                break
            if len(path_list) >= 1000:
                break
            if (
                max_depth
                and len(path.parts) - len(directory.parts) > max_depth
            ):
                continue
            if only_dir and not path.is_dir():
                continue
            if (not all_files) and (
                any(part.startswith(".") for part in path.parts)
            ):
                continue
            path_list.append(path)
        except PermissionError:
            pass
    path_list.sort()

    for path in path_list:
        count += 1
        relative_path = path.relative_to(directory)
        parts = relative_path.parts

        if args.f:
            path_work = relative_path
        else:
            path_work = Path(relative_path.name)
        current_level = folder_tree
        p = Path()
        for part in parts[:-1]:
            if args.f:
                p = p / part
            else:
                p = Path(part)
            current_level = current_level[p]

        if path.is_dir():
            current_level[path_work] = current_level.get(path_work, {})
            folders += 1
        else:
            current_level[path_work] = None
            files += 1
        if folders + files >= 1000:
            sw = True
            break

    print_tree({Path(directory.name): folder_tree}, args.i)

    if sw:
        if folders + files < 1000:
            str_1 = "Вывод ограничен временем"
        else:
            str_1 = "Вывод ограничен по длине: 1000 элементов"
        print(Fore.RED, str_1, Style.RESET_ALL)
    print(
        Fore.YELLOW,
        files,
        Style.RESET_ALL,
        "files, ",
        Fore.GREEN,
        folders,
        Style.RESET_ALL,
        "folders.",
    )


def main(command_line: str | None = None) -> None:
    """
    Главная функция программы.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", action="store_true", help="All files are printed."
    )
    parser.add_argument(
        "-d", action="store_true", help="Print directories only."
    )
    parser.add_argument("-f", action="store_true", help="Print relative path.")
    parser.add_argument(
        "-m",
        "--max_depth",
        type=int,
        default=None,
        help="Max depth of directories.",
    )
    parser.add_argument(
        "-i",
        action="store_true",
        help="Tree does not print the indentation lines."
        " Useful when used in conjunction with the -f option.",
    )
    parser.add_argument(
        "directory", nargs="?", default=".", help="Directory to scan."
    )
    args = parser.parse_args(command_line)

    try:
        directory = Path(args.directory).resolve(strict=True)
    except FileNotFoundError:
        print(f"Directory '{Path(args.directory).resolve()}' does not exist.")
        sys.exit(1)

    tree(directory, args)


if __name__ == "__main__":
    main()
