from dataclasses import dataclass
from enum import Enum

from transitions import Machine


class Group(Enum):
    CLEAR = 1
    NUMBER = 2
    OPERATOR = 3
    EQUAL = 4
    ERROR = 999


@dataclass
class Token:
    group: Group
    data: str


def decode(data: str) -> Token:
    if data in "c":
        return Token(Group.CLEAR, data)
    if data in "0123456789":
        return Token(Group.NUMBER, data)
    if data in "+-*/":
        return Token(Group.OPERATOR, data)
    if data in "=":
        return Token(Group.EQUAL, data)
    return Token(Group.ERROR, data)


@dataclass
class TinyCalc:
    disp: float = 0
    temp: float = 0
    operator: str | None = None

    def _first_number(self, token: Token) -> None:
        self.disp = int(token.data)

    def _rest_number(self, token: Token) -> None:
        self.disp = self.disp * 10 + int(token.data)

    def _op(self, token: Token) -> None:
        if self.operator == "+":
            self.disp = self.temp + self.disp
            self.temp = self.disp
        if self.operator == "-":
            self.disp = self.temp - self.disp
            self.temp = self.disp
        if self.operator == "*":
            self.disp = self.temp * self.disp
            self.temp = self.disp
        if self.operator == "/":
            self.disp = self.temp / self.disp
            self.temp = self.disp
        if self.operator == None:
            self.temp = self.disp

    def on_clear(self, token: Token) -> None:
        self.disp = 0
        self.temp = 0
        self.operator = None

    def on_number(self, token: Token) -> None:
        if self.state in ["s0", "s2"]:
            self._first_number(token)
        else:
            self._rest_number(token)

    def on_number_1(self, token: Token) -> None:
        self._first_number(token)

    def on_number_2(self, token: Token) -> None:
        self._rest_number(token)

    def on_operator(self, token: Token) -> None:
        self._op(token)
        self.operator = token.data

    def on_equal(self, token: Token) -> None:
        self._op(token)
        self.operator = None


def run(model: TinyCalc, machine: Machine, events: str) -> None:
    tokens = [decode(s) for s in events]

    for token in tokens:
        if token.group == Group.CLEAR:
            model.clear(token)
        if token.group == Group.NUMBER:
            import re

            trigger = next(
                s
                for s in machine.get_triggers(model.state)
                if re.search(r"num[0-9]+", s)
            )
            model.trigger(trigger, token)
        if token.group == Group.OPERATOR:
            model.op(token)
        if token.group == Group.EQUAL:
            model.eq(token)
        print(model.state, token, model)


def main():
    from pprint import pprint

    states = ["s0", "s1", "s2", "err"]
    transitions = [
        dict(trigger="clear", source="*", dest="s0", before="on_clear"),
        #        dict(trigger="num", source="*", dest="s1", before="on_number"),
        dict(trigger="num1", source=["s0", "s2"], dest="s1", before="on_number_1"),
        dict(trigger="num2", source="s1", dest="s1", before="on_number_2"),
        dict(trigger="op", source="s1", dest="s2", before="on_operator"),
        dict(trigger="eq", source="s1", dest="s2", before="on_equal"),
    ]
    model = TinyCalc()
    machine = Machine(
        model=model, states=states, transitions=transitions, initial=states[0]
    )

    run(model, machine, "c1+10+100=")


if __name__ == "__main__":
    main()
