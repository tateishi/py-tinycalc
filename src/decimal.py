from dataclasses import dataclass
from enum import Enum

from transitions import Machine


class Group(Enum):
    CLEAR = 1
    NUMBER = 2
    DECIMAL = 3
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
    if data in ".":
        return Token(Group.DECIMAL, data)
    return Token(Group.ERROR, data)


@dataclass
class DecimalNumber:
    reg: float = 0
    dec: float = 0.1

    def on_clear(self, token: Token) -> None:
        self.reg = 0
        self.dec = 0.1

    def on_number_1(self, token: Token) -> None:
        self.reg = int(token.data)

    def on_number_2(self, token: Token) -> None:
        self.reg = self.reg * 10 + int(token.data)

    def on_number_3(self, token: Token) -> None:
        self.reg = self.reg + int(token.data) * self.dec
        self.dec = self.dec * 0.1

    def noop(self, token: Token) -> None:
        pass



def run(model: DecimalNumber, machine: Machine, events: str) -> None:
    import re
    tokens = [decode(s) for s in events]

    for token in tokens:
        if token.group == Group.CLEAR:
            model.clear(token)
        if token.group == Group.NUMBER:
            trigger = next(
                s
                for s in machine.get_triggers(model.state)
                if re.search(r"num[0-9]+", s)
            )
            model.trigger(trigger, token)
        if token.group == Group.DECIMAL:
            trigger = next(
                s
                for s in machine.get_triggers(model.state)
                if re.search(r"dec[0-9]+", s)
            )
            model.trigger(trigger, token)
        print(model.state, token, model)


def main():
    from pprint import pprint

    states = ["init", "s0", "s1", "err"]
    transitions = [
        dict(trigger="clear", source="*", dest="init", before="on_clear"),
        dict(trigger="num1", source="init", dest="s0", before="on_number_1"),
        dict(trigger="num2", source="s0", dest="=", before="on_number_2"),
        dict(trigger="num3", source="s1", dest="=", before="on_number_3"),
        dict(trigger="dec1", source="init", dest="s1", before="noop"),
        dict(trigger="dec2", source="s0", dest="s1", before="noop"),
    ]
    model = DecimalNumber()
    machine = Machine(
        model=model, states=states, transitions=transitions, initial=states[0]
    )

    run(model, machine, "c19.123")


if __name__ == "__main__":
    main()
