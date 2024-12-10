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
    def __init__(self, state: Path) -> None:
        self.state = state
        self.children: list["TreeNode"] = []

    def add_child(self, child: "TreeNode") -> None:
        bisect.insort(self.children, child)

    def __repr__(self) -> str:
        return f"<{self.state}>"

    def __len__(self) -> int:
        return len(self.children)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TreeNode):
            return NotImplemented
        return self.state == other.state and self.children == other.children

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
        self.generate_tree(self.root, 0)

    def expand(self, node: TreeNode) -> None:
        try:
            for child in node.state.iterdir():
                if not self.__should_include(child):
                    continue
                self.__increment_counts(child)
                if self.full:
                    break
                node.add_child(TreeNode(child))
        except PermissionError:
            pass

    def generate_tree(self, node: TreeNode, level: int) -> None:
        if self.full or level == self.args.max_depth:
            return
        self.expand(node)
        for child in node.children:
            if child.state.is_dir():
                self.generate_tree(child, level + 1)

    def __should_include(self, child: Path) -> bool:
        if not self.args.a and child.name.startswith((".", "__")):
            return False
        if self.args.d and child.is_file():
            return False
        return True

    def __increment_counts(self, child: Path) -> None:
        if child.is_dir():
            self.dir_count += 1
        else:
            self.file_count += 1
        if self.dir_count + self.file_count >= 200:
            self.full = True

    def __format_tree(self, node: TreeNode, branch: str = "") -> str:
        result = StringIO()
        for i, child in enumerate(node.children):
            item = f"{branch}{'└── ' if i == len(node.children) - 1 else '├── '}"
            name = (
                child.state.name
                if not self.args.f
                else child.state.relative_to(self.directory)
            )
            color = Fore.GREEN if child.state.is_file() else Fore.YELLOW
            result.write(f"{item}{color}{name}{Style.RESET_ALL}\n")
            new_branch = f"{branch}{'    ' if i == len(node.children) - 1 else '│   '}"
            result.write(self.__format_tree(child, new_branch))
        return result.getvalue()

    def __str__(self) -> str:
        header = f"{Fore.BLUE}{self.root.state.name}{Style.RESET_ALL}\n"
        body = self.__format_tree(self.root)
        footer = f"\n{Fore.YELLOW}Directories: {self.dir_count}, "
        footer += f"{Fore.GREEN}Files: {self.file_count}{Style.RESET_ALL}"
        if self.full:
            footer += f"{Fore.RED}\nOutput limited to 200 elements.{Style.RESET_ALL}"
        return header + body + footer


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
