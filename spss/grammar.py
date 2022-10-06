# keywords = [
#     "COMPUTE",
#     "DELETE",
#     "ELSE",
#     "EXECUTE",
#     "INTO",
#     "LABELS",
#     "Lowest",
#     "MISSING",
#     "RECODE",
#     "SYSMIS",
#     "thru",
#     "VARIABLES",
# ]

regex_lexemes = [
    ("newline", r'\n'),
    ("end_of_statement", r'\.\n'),
    ("asterisk", r'\*'),
    ("op_comp", r'<=|=<|>='),
    ("assignment_op", r'='),
    ("op", r'\+|-|/'), # '*' is asterisk
    ("dot", r'\.'),
    ("left_brace", r'\('),
    ("right_brace", r'\)'),
    ("sqstring", r"'[^']*'"),
    # ("single_quote", r"'"),
    ("number", r'0|[1-9][0-9]*'),
    ("identifier", r'[a-zA-Z0-9_]+'),
    ("ws", r'[ \t]+'),
    ("other", r'.'),
]

_any_lexeme = set(['keyword'] + [name for name, _ in regex_lexemes])

grammar = [
    # "Script -> Statements",
    "Script -> BOM Statements",
    "BOM -> Any Any Any",
    "BOM -> Any Any",
    *(f"Any -> {lexeme}" for lexeme in _any_lexeme),
    "Statements -> Statement Statements",
    "Statements -> Statement EOF",
    "Statement -> Comment",
    "Statement -> EmptyLine",
    "Statement -> DeleteStatement",
    "Statement -> RecodeStatement",
    "Statement -> LabelsStatement",
    "Statement -> ExecuteStatement",
    "Statement -> ComputeStatement",
    "DeleteStatement -> 'DELETE' 'VARIABLES' Identifiers end_of_statement",
    "RecodeStatement -> 'RECODE' identifier Cases 'INTO' identifier end_of_statement",
    "LabelsStatement -> 'VARIABLE' 'LABELS' identifier sqstring end_of_statement",
    "ExecuteStatement -> 'EXECUTE' end_of_statement",
    "ComputeStatement -> 'COMPUTE' identifier assignment_op Expression",
    "Identifiers -> identifier Identifiers",
    "Identifiers -> identifier",
    "Cases -> Case Cases",
    "Cases -> Case",
    "Case -> left_brace Case_ right_brace",
    "Case_ -> MissingCase",
    "Case_ -> LowestThruCase",
    "Case_ -> ValueCase",
    "Case_ -> ElseCase",
    "MissingCase -> 'MISSING' assignment_op 'SYSMIS'",
    "LowestThruCase -> 'Lowest' 'thru' Number assignment_op Number",
    "ValueCase -> Number assignment_op Number",
    "ElseCase -> 'ELSE' assignment_op Number",
    "Comment -> asterisk NotEOSs end_of_statement",
    "NotEOSs -> NotEOS NotEOSs",
    "NotEOSs -> NotEOS",
    *(f"NotEOS -> {lexeme}" for lexeme in _any_lexeme - {'end_of_statement'}),
    "EmptyLine -> newline",
    # "Sqstring -> single_quote NotSQs single_quote",
    # "NotSQs -> NotSQ NotSQs",
    # "NotSQs -> NotSQ",
    # *(f"NotSQ -> {lexeme}" for lexeme in _any_lexeme - {'single_quote'}),
    "Number -> Float",
    "Number -> Int",
    "Float -> number dot number",
    "Int -> number",
]

