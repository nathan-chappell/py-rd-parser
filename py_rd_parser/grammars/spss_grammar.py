from typing import List, Iterable

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
    ("newline", r"\n"),
    # ("end_of_statement", r"\.\s*\n"),
    ("asterisk", r"\*"),
    ("compare_op", r"<=|=<|>="),
    ("assignment_op", r"="),
    ("add_sub_op", r"\+|-"),  # '*' is asterisk
    ("div_op", r"/"),
    ("dot", r"\."),
    ("left_brace", r"\("),
    ("right_brace", r"\)"),
    ("sqstring", r"'[^']*'"),
    # ("single_quote", r"'"),
    # ("number", r"0|[1-9][0-9]*"),
    ("number", r"[0-9]+"),
    ("identifier", r"[a-zA-Z0-9_]+"),
    ("ws", r"[ \t]+"),
    ("other", r"."),
]

# skip_lexemes = ["ws", "newline"]


def remove_lexeme_type(_type: str):
    return lambda lexemes: filter(lambda lexeme: lexeme.type != _type, lexemes)


def concat_newline(lexemes: Iterable["Lexeme"]):
    skip_newline = False
    for lexeme in lexemes:
        if lexeme.type == "newline" and skip_newline:
            continue
        skip_newline = lexeme.type == "newline" and not skip_newline
        yield lexeme


def insert_end_of_statement(lexemes: Iterable["Lexeme"]):
    lexeme_iterator = iter(lexemes)
    previous_lexeme = next(lexeme_iterator)
    new_previous_type = None
    for lexeme in lexeme_iterator:
        if (previous_lexeme.type, lexeme.type) in [
            ("dot", "newline"),
            ("newline", "keyword"),
        ] and new_previous_type != "end_of_statement":
            new_previous_type = "end_of_statement"
        else:
            new_previous_type = previous_lexeme.type
        yield previous_lexeme._replace(type=new_previous_type)
        previous_lexeme = lexeme
    yield lexeme


preprocess_lexemes = [
    remove_lexeme_type("ws"),
    concat_newline,
    insert_end_of_statement,
    remove_lexeme_type("newline"),
]


expression_grammar = [
    # "Expression -> ParenExpression",
    # "Expression -> Factor",
    "Expression -> AddSubExpression Expression_rest?",
    "Expression_rest -> compare_op Expression",
    "AddSubExpression -> MulDivExpression AddSubExpression_rest?",
    "AddSubExpression_rest -> add_sub_op Expression",
    "MulDivExpression -> Factor MulDivExpression_rest?",
    "MulDivExpression_rest -> MulDivOp Expression",
    "MulDivOp -> div_op | asterisk",
    "Factor -> Variable | Constant | ParenExpression",
    "ParenExpression -> left_brace Expression right_brace",
    "Variable -> identifier",
    "Constant -> SignedNumber | Number",
    "SignedNumber -> add_sub_op Number",
    "Number -> Float | Int",
    "Number -> Int",
    "Float -> number dot number",
    "Int -> number",
]

grammar = [
    # "Script -> Statements",
    "Script -> Statement* EOF",
    "Statement -> Statement_ end_of_statement",
    # "Statement -> Statement_ EndOfStatement",
    # "EndOfStatement -> end_of_statement",
    # "EndOfStatement -> newline | end_of_statement",
    "Statement_ -> ComputeStatement | ExecuteStatement | EmptyLine"
    " | Comment | DeleteStatement | RecodeStatement | LabelsStatement",
    "DeleteStatement -> 'DELETE' 'VARIABLES' identifier*",
    "RecodeStatement -> 'RECODE' identifier Case* 'INTO' identifier",
    "LabelsStatement -> 'VARIABLE' 'LABELS' identifier sqstring",
    "ExecuteStatement -> 'EXECUTE'",
    "ComputeStatement -> 'COMPUTE' identifier assignment_op Expression",
    "Case -> left_brace Case_ right_brace",
    "Case_ -> MissingCase | LowestThruCase | ElseCase| ValueCase",
    "MissingCase -> 'MISSING' assignment_op 'SYSMIS'",
    "LowestThruCase -> 'Lowest' 'thru' Number assignment_op Number",
    "ElseCase -> 'ELSE' assignment_op Number",
    "ValueCase -> Number assignment_op Number",
    "Comment -> asterisk not_end_of_statement*",
    "EmptyLine -> newline",
    *expression_grammar,
]
