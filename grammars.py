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

fp_language_grammar = Grammar(
    name="fpLang",
    terminals=[
        ("ws", r"\s+"),
        ("right_arrow", r"->"),
        ("let", r"let"),
        ("semicolon", r";"),
        ("assignment_op", r"="),
        ("add_op", r"\+|-"),
        ("mul_op", r"\*|/"),
        ("lbrace", r"\("),
        ("rbrace", r"\)"),
        ("identifier", r"[a-zA-Z_]+"),
        ("int", r"0|[1-9][0-9]*"),
        ("float", r"((0|[1-9][0-9]*)\.)|(\.[0-9]+)|((0|[1-9][0-9]*)\.[0-9]+)"),
    ],
    productions=[
        ("Program", "Statements Expression"),
        ("Program", "Expression"),
        ("Statements", "Statement Statements"),
        ("Statements", "Statement"),
        ("Statement", "let identifier assignment_op Expression semicolon"),
        ("Expression", "Abstraction"),
        ("Expression", "Application"),
        ("Expression", "SubExpression"),
        ("Abstraction", "identifier right_arrow Expression"),
        ("Application", "BracedExpression SubExpression"),
        ("Application", "identifier SubExpression"),
        ("SubExpression", "BracedExpression"),
        ("SubExpression", "AddExpr"),
        ("BracedExpression", "lbrace Expression rbrace"),

        ("AddExpr", "Application"),
        ("AddExpr", "MulExpr add_op AddExpr"),
        ("AddExpr", "MulExpr"),
        ("MulExpr", "Factor mul_op MulExpr"),
        ("MulExpr", "Factor"),
        ("Factor", "lbrace AddExpr rbrace"),
        ("Factor", "identifier"),
        ("Factor", "int"),
        ("Factor", "float"),
    ],
    start_symbol="Program",
    examples={
        "application": "(x -> x + 1) 1",
        "statement": "let f = x -> x + 1; f 2",
        "higher-order-fns": "((f -> x -> f f x) (x -> x * x)) 3",
        # "statements": """
        #     let Y = f_ -> (x -> f_ x x) (x -> f_ x x);
        #     let fact_ = f -> n -> n == 0 ? 1 : n * f (n - 1);
        #     let fact = Y fact_;
        # """,
    },
)