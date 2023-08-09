#!/usr/bin/env python3
"""My overly complicated Brainfuck interpreter"""
from __future__ import annotations
from enum import Enum, auto
from typing import Dict, List
import sys


class TokenEnum(Enum):
    INCREMENT_POINTER = auto()
    DECREMENT_POINTER = auto()
    INCREMENT_BYTE = auto()
    DECREMENT_BYTE = auto()
    OUTPUT_BYTE = auto()
    INPUT_BYTE = auto()
    LOOP_START = auto()
    LOOP_END = auto()


class BrainfuckToken:
    """Represents a Brainfuck command"""

    token_enum_map: Dict[str, TokenEnum] = {
        ">": TokenEnum.INCREMENT_POINTER,
        "<": TokenEnum.DECREMENT_POINTER,
        "+": TokenEnum.INCREMENT_BYTE,
        "-": TokenEnum.DECREMENT_BYTE,
        ".": TokenEnum.OUTPUT_BYTE,
        ",": TokenEnum.INPUT_BYTE,  # Not implemented.
        "[": TokenEnum.LOOP_START,
        "]": TokenEnum.LOOP_END,
    }

    def __init__(self, token_type: TokenEnum, source_char_idx: int):
        self.type: TokenEnum = token_type
        self._char_idx: int = source_char_idx

    def __repr__(self) -> str:
        return f"<BrainfuckToken.{self.type} pos[{self._char_idx}]>"

    def __str__(self) -> str:
        return repr(self)

    @classmethod
    def from_char(cls, char: str, char_idx: int) -> BrainfuckToken:
        token_type: TokenEnum = cls.token_enum_map[char]
        return cls(token_type, char_idx)


class BrainfuckLexer:
    """Brainfuck lexer/tokenizer"""

    def __init__(self, program_string: str):
        self._program = program_string

    def tokenize(self) -> List[BrainfuckToken]:
        tokens: List[BrainfuckToken] = []
        valid_whitespaces: List[str] = [" ", "\n", "\t"]
        for idx, char in enumerate(self._program):
            if char in valid_whitespaces:
                continue
            if char not in BrainfuckToken.token_enum_map:
                continue
            tokens.append(BrainfuckToken.from_char(char, idx))
        return tokens

    def __repr__(self) -> str:
        return f"<BrainfuckLexer object>"

    def __str__(self) -> str:
        return repr(self)

    @classmethod
    def from_file(cls, filepath: str) -> BrainfuckLexer:
        with open(filepath, "r", encoding="utf-8") as program:
            program_text: str = program.read()
        return cls(program_text)


class BrainfuckInterpreter:
    """Interprets a list of Brainfuck tokens"""

    def __init__(self, tokens: List[BrainfuckToken], bits: int = 8):
        self._tokens: List[BrainfuckToken] = tokens
        self._jump_table: Dict[int, int] = {}
        self.validate()
        self._calc_jump_table()
        if bits in (8, 16, 32, 64):
            self._bits = bits
            self._bitwidth = 2**bits
        else:
            self._bits = 8
            self._bitwidth = 256

    def run(self) -> str:
        pointer: int = 0
        instr: int = 0
        steps: int = 0
        data: Dict[int, int] = {}
        output = ""
        while True:
            steps += 1
            if instr >= len(self._tokens):
                break
            token = self._tokens[instr]
            typ = token.type
            data.setdefault(pointer, 0)
            # print(f"{steps=}, {instr=}, {pointer=}, data={data[pointer]}, typ")

            if typ is TokenEnum.INCREMENT_POINTER:
                pointer += 1

            elif typ is TokenEnum.DECREMENT_POINTER:
                pointer -= 1

            elif typ is TokenEnum.INCREMENT_BYTE:
                data[pointer] += 1
                if data[pointer] == self._bitwidth:
                    data[pointer] = 0

            elif typ is TokenEnum.DECREMENT_BYTE:
                data[pointer] -= 1
                if data[pointer] == -1:
                    data[pointer] = self._bitwidth - 1

            elif typ is TokenEnum.OUTPUT_BYTE:
                char = chr(data.setdefault(pointer, 0))
                output += char

            elif typ is TokenEnum.INPUT_BYTE:
                pass  # TODO: Implement this somehow

            elif typ is TokenEnum.LOOP_START:
                if not data[pointer]:
                    instr = self._jump_table[instr]
                    continue

            elif typ is TokenEnum.LOOP_END:
                if data[pointer]:
                    instr = self._jump_table[instr]
                    continue

            instr += 1
        return output

    def _calc_jump_table(self) -> None:
        jump_stack: List[int] = []
        for instr, token in enumerate(self._tokens):
            if token.type is TokenEnum.LOOP_START:
                jump_stack.append(instr)
            if token.type is TokenEnum.LOOP_END:
                start_loop = jump_stack.pop()
                self._jump_table[instr] = start_loop
                self._jump_table[start_loop] = instr + 1

    def validate(self) -> bool:
        jump_stack: List[int] = []
        for instr, token in enumerate(self._tokens):
            if token.type is TokenEnum.LOOP_START:
                jump_stack.append(instr)
            if token.type is TokenEnum.LOOP_END:
                jump_stack.pop()
        return not bool(jump_stack)

    def __repr__(self) -> str:
        return f"<BrainfuckInterpreter, {self._bits}-bit>"

    def __str__(self) -> str:
        return repr(self)

    @classmethod
    def from_file(cls, filepath: str, bits: int = 8) -> BrainfuckInterpreter:
        lexer: BrainfuckLexer = BrainfuckLexer.from_file(filepath)
        return cls(lexer.tokenize(), bits)


def main() -> None:
    if len(sys.argv) <= 1:
        return
    if len(sys.argv) == 2:
        print(BrainfuckInterpreter.from_file(sys.argv[1]).run(), end="")
        return
    for filepath in sys.argv[1:]:
        out = BrainfuckInterpreter.from_file(filepath).run()
        print(f"-- {filepath} --")
        print(f"{out}", end="")
        if out[-1] != "\n":
            print("⏎")


if __name__ == "__main__":
    main()
