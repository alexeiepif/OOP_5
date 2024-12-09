#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Разработайте аналог утилиты tree в Linux.
# Используйте возможности модуля argparse для
# управления отображением дерева каталогов файловой системы.
# Добавьте дополнительные уникальные возможности в данный программный продукт.
# Выполнить индивидуальное задание 2 лабораторной работы 2.19,
# добавив аннтотации типов.
# Выполнить проверку программы с помощью утилиты mypy.

import argparse
import bisect
import sys
from io import StringIO
from pathlib import Path

from colorama import Fore, Style


class TreeNode:
    def __init__(self, state: Path, children: list["TreeNode"] = []) -> None:
        self.state = state
        self.children = children

    def add_child(self, child: "TreeNode") -> None:
        bisect.insort(self.children, child)

    def __repr__(self) -> str:
        return f"<{self.state}>"

    def __len__(self) -> int:
        return len(self.children)

    def __lt__(self, other: "TreeNode") -> bool:
        return len(self) < len(other)


class Tree:
    def __init__(self, directory: Path, args: argparse.Namespace) -> None:
        self.directory = directory
        self.args = args
        self.root = TreeNode(directory)
        self.dir_count = 0
        self.file_count = 0
        self.full = False
        self.generate_tree(self.root)

    def expand(self, node: TreeNode) -> None:
        try:
            for child in node.state.iterdir():
                if (not self.args.a) and (
                    child.name.startswith(".")
                    or child.name.startswith("__")
                    or child.name.startswith("..")
                ):
                    continue
                if self.args.d and child.is_file():
                    continue
                if child.is_dir():
                    self.dir_count += 1
                else:
                    self.file_count += 1
                if self.dir_count + self.file_count >= 200:
                    self.full = True
                    break
                node.add_child(TreeNode(child, []))

        except PermissionError:
            pass

    def generate_tree(self, node: TreeNode, level: int = 0) -> None:
        """Рекурсивно генерирует дерево, начиная с заданного узла."""
        if self.dir_count + self.file_count >= 200:
            self.full = True
            return
        if level == self.args.max_depth:
            return
        self.expand(node)
        if self.full:
            return
        for child in node.children:
            if child.state.is_dir():
                self.generate_tree(child, level + 1)

    def __print_tree(self, node: TreeNode, level: int = 0, branch: str = "") -> str:
        buffer = StringIO()
        sw = True

        for i, child in enumerate(node.children):
            color = (
                Fore.GREEN
                if not child.children and child.state.is_file()
                else Fore.YELLOW
            )
            name = (
                child.state.name
                if not self.args.f
                else child.state.relative_to(self.directory)
            )
            if i == len(node) - 1:
                sw = False
                item = f"{branch}└── "
            else:
                item = f"{branch}├── "
            if self.args.i:
                item = ""
            buffer.write(f"{item}{color}{name}{Style.RESET_ALL}\n")

            if not self.args.i:
                new_branch = f"{branch}│   " if sw else f"{branch}    "
            else:
                new_branch = ""
            buffer.write(self.__print_tree(child, level + 1, new_branch))

        result = buffer.getvalue()
        buffer.close()
        return result

    def __str__(self) -> str:
        buffer = StringIO()
        buffer.write(f"{Fore.BLUE}{self.root.state.name}{Style.RESET_ALL}\n")
        buffer.write(self.__print_tree(self.root))
        buffer.write("\n")
        if self.full and (self.dir_count + self.file_count < 200):
            buffer.write("Вывод ограничен временем\n")
        elif self.full:
            buffer.write("Вывод ограничен по длине: 200 элементов\n")
        buffer.write(
            f"{Fore.YELLOW}Directories: {self.dir_count}, "
            f"{Fore.GREEN}Files: {self.file_count}{Style.RESET_ALL}"
        )

        result = buffer.getvalue()
        buffer.close()
        return result


def main(command_line: list[str] | None = None) -> None:
    """
    Главная функция программы.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store_true", help="All files are printed.")
    parser.add_argument("-d", action="store_true", help="Print directories only.")
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
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan.")
    args = parser.parse_args(command_line)

    try:
        directory = Path(args.directory).resolve(strict=True)
    except FileNotFoundError:
        print(f"Directory '{Path(args.directory).resolve()}' does not exist.")
        sys.exit(1)

    tree = Tree(directory, args)
    print(tree)


if __name__ == "__main__":
    main()
