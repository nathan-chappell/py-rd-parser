from run import run

if __name__ == "__main__":
    run(
        [
            ("ws", r"\s+"),
            ("add_op", r"\+|-"),
            ("mul_op", r"\*|/"),
            ("lbrace", r"\("),
            ("rbrace", r"\)"),
            ("var", r"[a-zA-Z_]+"),
            ("int", r"\d+"),
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
        [
            "x * y + z * ( x + y )",
            """x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) *
                ( x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) +
                    x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) ) + (
                        ( z + z * x + y * z + x ) * ( z + z * x + y * z + x ) * ( z + z * x + y * z + x ) * ( z + z * x + y * z + x )
            )""",
        ],
    )

    # run(
    #     [
    #         ("ws", r"\s+"),
    #         ("add_op", r"\+|-"),
    #         ("mul_op", r"\*|/"),
    #         ("lbrace", r"\("),
    #         ("rbrace", r"\)"),
    #         ("var", r"[a-zA-Z_]+"),
    #         ("int", r"\d+"),
    #     ],
    #     [
    #         ("AddExpr", "MulExpr add_op AddExpr"),
    #         ("AddExpr", "MulExpr"),
    #         ("MulExpr", "Factor mul_op MulExpr"),
    #         ("MulExpr", "Factor"),
    #         ("Factor", "lbrace AddExpr rbrace"),
    #         ("Factor", "var"),
    #         ("Factor", "int"),
    #     ],
    #     "AddExpr",
    #     [
    #         "x * y + z * ( x + y )",
    #         """x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) *
    #             ( x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) +
    #                 x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) )""",
    #     ],
    # )
