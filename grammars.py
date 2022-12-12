from dataclasses import replace

from grammar import Grammar


expression_grammar = Grammar(
    "Expressions",
    [
        ("ws", r"\s+"),
        ("add_op", r"\+|-"),
        ("mul_op", r"\*|/"),
        ("lbrace", r"\("),
        ("rbrace", r"\)"),
        ("var", r"[a-zA-Z_]+"),
        ("int", r"0|[1-9][0-9]*"),
        ("float", r"((0|[1-9][0-9]*)\.)|(\.[0-9]+)|((0|[1-9][0-9]*)\.[0-9]+)"),
    ],
    [
        ("AddExpr", "MulExpr add_op AddExpr"),
        ("AddExpr", "MulExpr"),
        ("MulExpr", "Factor mul_op MulExpr"),
        ("MulExpr", "Factor"),
        ("Factor", "lbrace AddExpr rbrace"),
        ("Factor", "var"),
        ("Factor", "int"),
    ],
    "AddExpr",
    {
        "simple": "x * y + z * ( x + y )",
        **{
            f'ugly_{i}': ' * '.join(['x']*i) for i in range(2,21,2)
        }
        # "ugly": ' * '.join(['x']*20)
        # "taylor sin": "",
        # "big and ugly": """x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) *
        #         ( x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) +
        #             x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) ) + (
        #                 ( z + z * x + y * z + x ) * ( z + z * x + y * z + x ) * ( z + z * x + y * z + x ) * ( z + z * x + y * z + x ) )""",
    },
)

bad_expression_grammar = replace(
    expression_grammar,
    name="Expressions (bad)",
    productions=[
        ("AddExpr", "MulExpr add_op AddExpr"),
        ("AddExpr", "MulExpr"),
        ("MulExpr", "Factor mul_op AddExpr"),  # HERE
        ("MulExpr", "Factor"),
        ("Factor", "lbrace AddExpr rbrace"),
        ("Factor", "var"),
        ("Factor", "int"),
    ],
)
