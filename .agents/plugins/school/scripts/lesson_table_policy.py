"""Shared boundary between practical lesson actions and methodology explanations."""

import re


FRAMEWORK_PATTERN = re.compile(
    r"\b(?:UDL|UbD|PBL|Rosenshine(?:[’']s)?|Wiliam|Marzano|Tomlinson|Hattie)\b"
    r"|universal design for learning|understanding by design|visible learning"
    r"|explicit instruction|visible thinking|dialogic teaching"
    r"|(?:project|problem|inquiry)[ -]based learning|design thinking"
    r"|archer[–— -]hughes|agarwal[–— -]bain"
    r"|розеншайн\w*|универсальн\w* дизайн\w* обучен\w*"
    r"|оқытудың әмбебап дизайны|әмбебап оқу дизайны"
    r"|марзано\w*|томлинсон\w*|хэтти\w*|уильям\w*"
    r"|видим\w* обучен\w*|көрінетін оқу|явн\w* обучен\w*"
    r"|тікелей оқыту|дизайн[ -]мышление|дизайн[ -]ойлау",
    re.IGNORECASE,
)


def contains_framework(text: str) -> bool:
    return bool(FRAMEWORK_PATTERN.search(text))
