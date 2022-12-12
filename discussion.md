# Introduction

# Grammars

*Grammars* are used to define the syntax formal languages, and are typically (part of) the input to generic parsers or parser generators.  We will be interested in a class of grammars known as *context-free* grammars.

## Motivational Example

To motivate *context-free* grammars, let's consider the syntax of arithmetic expressions.  We will suppose that we have the typical operators `+ - * /`, parenthesis for grouping `()` and for simplicity we'll only consider expressions involving non-negative integers (`0 1 2 ...`).  Here are some simple arithmetic expressions:

* `1`
* `1 + 2`
* `1 + 2 * 3`
* `(1 + 2) * 3`
* `1 * 2 + 3`
* `(1 * 2) + 3`

In general, we can notice some patterns.  Let `n` be a placeholder for a non-negative integers.

* If `E` is an expression, then so is `E + n` (likewise for `- * /`)
* If `E` is an expression, then so is `(E)`

In fact, we can summarize the syntax of all expressions we've been considering as follows:

* `n` is an expression, where `n` is a non-negative integers
* if `E1` and `E2` are expressions, then so is `E1 op E2` where `op` is one of `+ - * /`
* if `E` is an expression, then so is `(E)`

Before continuing, you should convince yourself that the above description includes all the examples previously given.

## Formal Grammars

We're now prepared to define grammars more formally.  Once we've done that, we will use them to parse formal languages (e.g. arithmetic expressions or programming languages).

According to [wikipedia](https://en.wikipedia.org/wiki/Formal_grammar)

> In formal language theory, a grammar (when the context is not given, often called a formal grammar for clarity) describes how to form strings from a language's alphabet that are valid according to the language's syntax. A grammar does not describe the meaning of the strings or what can be done with them in whatever context—only their form. A formal grammar is defined as a set of production rules for such strings in a formal language.

This sounds similar to how we've tried to describe the syntax of arithmetic expressions, but they've used the jargon *production rule*, which we haven't introduced.  It will be useful to first give the grammar of arithmetic expressions, then elaborate the definition.

```
# Arithmetic Expressions Grammar 1
Start: Expression

    Expression -> number
    Expression -> Expression op Expression
    Expression -> ( Expression )

    number -> 0 | 1 | 2 | ...
    op -> + | - | * | /
```

So, this is a nice little chart or something, what are we supposed to do with it?  The basic idea is this.  Suppose you want to make an arithmetic expression.  Start with the `Expression` symbol.  Now you have three choices, either turn `Expression` into `number`, `Expression op Expression`, or `( Expression )`.  Take the second choice, now you have `Expression op Expression`.  Now you have to choose what to do with those symbols too.  Let the `Expression`s turn into `number`, and `op` turn into `+`.  Then we'd have `number + number`.  Finally, let the `number`s turn into `0`, and you get `0 + 0`.  To summarize, we made the following transformations:

`Expression -> Expression op Expression -> number + number -> 0 + 0`

## Formal Grammars, More Formally

 Formally, a *context-free grammar*, or simply *grammar*, is given by:

 1. Two lists of symbols, the *terminals* and *non-terminals*
 2. A *start-symbol*, which is a *non-terminal*
 3. A list of *production rules*.  Each *production rule* consists of:
    * A *non-terminal* called the *head*
    * A sequence of *terminals* and *non-terminals* called the *body*

The __*language*__ of a *grammar* is all sequences of *terminals* which can be created by expanding *non-terminals* (recursively), starting with the *start-symbol*.  By "recursively expanding" we mean that if you expand a *non-terminal*, and it creates more *non-terminals*, you can continue expanding them.

These definitions are sufficiently rigorous, without being overly formal.  See [wikipedia](https://en.wikipedia.org/wiki/Context-free_grammar) for more discussion.  We will instead look at the the implementation of a grammar used here.

### `grammar.py`

Here is our definition of a grammar:

```py
# grammar.py
@dataclass
class Grammar:
    name: str
    terminals: T.List[NamedTerminal]
    productions: T.List[TProduction]
    start_symbol: THead
    examples: T.Dict[str, str]
```

Note that we use the following convention in all files: `import typing as T`.  `grammar.py` uses the following defintions from `common_types.py`:

```py
# common_types.py
NamedTerminal = T.Tuple[str, str]
THead = str
TBody = str
TProduction = T.Tuple[THead, TBody]
```

These types correspond to the definition of a *grammar* one-to-one, except for the `NamedTerminal`.  The `NamedTerminal` is given by a `name`, and a `pattern`.  The pattern will be used for lexical analysis (discussed below), and the name corresponds to the *terminal* from the definition.

The first thing to point out is that `Grammar` has no "list of *non-terminals*."  These are given implicitly in the productions.  The `terminals` field exists primarily because it is convenient for lexical analysis.  The `examples` field is pure convenience, and arguably should be excluded.

It's worth noting, that with some reasonable conventions, a grammar can be given completely by its list of productions `productions: T.List[TProduction]`.  We suppose that all *non-terminals* appear in the head of at least one `production`, and that *non-terminals* are given in `PascalCase` and *terminals* are given in `snake_case`.  Then we can tell if a symbol is a *terminal* by checking if the first character is lower case.  We could also suppose that the first *head* of the first *production* is the start symbol.

Indeed this was the original implementation, and those are good conventions to follow even if you have a more elaborated definition of a grammar.  The more elaborate definition proved to be more convenient while testing and refactoring.

Now we have defined a new abstraction, the *grammar*, but it is yet to demonstrate its usefulness.

# Parsers

Suppose we would like to interpret arithmetic expressions in some text, and evaluate them.  This seems like a pretty reasonable thing to do, in fact it seems like it's what programming languages do - or, rather, their runtimes.  Concretely, suppose we have the expression `1 + 2 * 3`.  How can we evaluate it?  

One technique utilizes a data structure called the *abstract syntax tree (AST)*.  Here is what such a tree would look like for `1 + 2 * 3`:

```
  +
 / \
1   *
   / \
  2   3
```

Before figuring out how we'd create such a tree, let's first see how we can use it to evaluate the expression.  Let's say we're at the `+` node.  The value of our node should be the value of our left child plus the value of our right child.  So, we recurse into our children, and return the sum of the result.  Our left child is just `1`, so evaluating that node just results in `1`.  The right child is a `*`, so again we recurse into our children, and return their product.  This gives us `6`, which after summing with `1` gives us the result `7`, which is what we wanted.

Our purpose now is to show how we can use a grammar to produce an *AST*.  This will be the result of the final implementation, but for now we discuss parsers more generally.

## Parsers more generally

We refer to [wikipedia](https://en.wikipedia.org/wiki/Parsing) for a definition:

> Parsing, syntax analysis, or syntactic analysis is the process of analyzing a string of symbols, either in natural language, computer languages or data structures, conforming to the rules of a formal grammar... Within computational linguistics the term is used to refer to the formal analysis by a computer of a sentence or other string of words into its constituents, resulting in a parse tree showing their syntactic relation to each other

In my words, a *parser* takes some *text* as input, and produces some *internal representation* as output.  There are a number of considerations for both the *text* and desired output.

* Is the *text* binary or "textual"?
* Does the entire input need to be read before it can be parsed?  (I.e. can we parse from a stream?)

While there is no conceptual difference between parsing binary or "string-like" (we'll assume python `str` type for our implementation) sequences of symbols, there tend to be different practical implications.  First of all, it seems like it would be good practice to keep the logic which parses some "high-level language" separated from the logic that interprets bytes as ints or characters.  This is basic [separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns).  As a result, the complete system that takes bytes to *AST* will typically be a [Layered System](https://www.ics.uci.edu/~fielding/pubs/dissertation/net_arch_styles.htm#sec_3_4_2).

### Lexical Analysis

The reason to mention all this is that it is often useful to introduce another "layer" between the input and the construction of the *AST.*  This layer is often called *lexical analysis*.  The *lexical analyzer* will take the input, in our case some `str`, and will transform it into a sequence of *lexemes*.  These lexemes will typically carry information about the source it came from, and the *terminal* to which it is associated.  Here is our implementation of *lexeme*:

```py
@dataclass
class Lexeme:
    name: str
    value: str
    start: int
    end: int
    line: T.Optional[int] = None
    column: T.Optional[int] = None
```

The actual code contains a method to allow a *lexeme* to be compared to a string by `name`.  Here `name` is expected to be the name of a *terminal*, `value` is the substring that was matched, `start` and `end` define the span of the match `[start,end)`.  `line` and `column` are source information.  They won't be particularly important to us here, but since they are important in practice I've included them.

## Recursive Descent Parsers

At this point we should describe our parsing algorithm.  I've taken the python code, and removed the "noise" to make it clear as possible.  In particular, code related to keeping track of the "current_lexeme" is removed - it is mainly updating and resetting some variable which tracks the current "index."  `lexemes` is the sequence of lexemes.  `target` is the symbol which should be parsed.  `index` is the position in `lexemes` where `target` should be parsed.

```py
def parse(lexemes, target, index):
    for head, body in productions_for_target:
        assert head == target
        try:
            children = []
            for symbol in body:
                if current_lexeme_matches_symbol:   children.append(AstNode(symbol, current_lexeme))
                elif symbol_is_non_terminal:        children.append(parse(lexemes, symbol, index))
                else: FAIL()
            return AstNode(target, children)
        except Failure:
            restart
    raise ParseException()
```

The algorithm proceeds by iterating through the productions for the target symbol.  For each production, it tries to match each symbol in sequence.  If the symbol is a *terminal*, then it can add a child to the list of children immediately.  If the symbol is a *non-terminal*, then it must get the child by recursively calling `parse`.  Note that when a single production fails to match, an exception is raised.  It is immediately caught, and the algorithm "restarts" with the next production.  If some production matches, then an `AstNode` is returned, otherwise an exception is raised.

It should be clear why this parsing technique is known as "recursive descent."  From the point of view of the grammar, we basically just keep trying to recursively expand symbols, left-to-right, until we fail to match an expected lexeme or succeed.  If you think that this sounds inefficient, well it is!  And if you think that this algorithm is just going to go into an infinite recursion, it will!  We'll deal with the inefficiency later, but we should address the other point immediately.

### Avoiding Infinite (Left) Recursion

Suppose our grammar is as follows:

```
    E -> E + E
    E -> E
    E -> number
```

And suppose we wish to use *recursive descent* to parse the expression `0 + 1`, starting from `E`.  The first prodcution we will descend into is `E + E`.  The first symbol of the production is `E`, which is a *non-terminal*, so we execute the statement starting with `elif symbol_is_non_terminal`, and immediately recurse into `parse(...)` again.  We have not made any "progress" in parsing, and we are now trying to parse the same symbol at the same location, therefore we are stuck in infinite recursion.

The solution is a form of preprocessing sometimes called "normalization."  A full discussion can be found on [wikipedia](https://en.wikipedia.org/wiki/Left_recursion#Removing_left_recursion), here we will illustrate the idea so that you should be able to remove *left recursion* from your relatively simple grammars directly.  If you need a more systematic approach, consult the formal algorithm.

The key idea depends on the notion of "making progress" that was eluded to before.  Let's consider "making progress" to be incrementing our index into the sequence of `lexemes`.  That is, every time our parser matches a *non-terminal*, our parser has made progress.  This tells us what we need to do to make sure that our grammar doesn't go into an infinite loop: remove all "paths" through our grammar that go from a *non-terminal* to the same *non-terminal*, and insert productions that will "simulate" those "paths" but guarantee progress as we've defined it.  That's a mouthful, here is this idea applied to the grammar above.

First, the production `E -> E + E` has to go.  In general, every rule like `E -> E ...` must be changed.  What to change them to?  One idea is to see what `E` will eventually change into (say, `E'`), and replace the left-most occurrence of `E` in the production body with that symbol (e.g. `E'`).  In our case, `E` eventually must turn into `number`, so we apply the described tranformation and end up with:

```
    E -> number + E
    E -> number
    E -> number
```

We can now eliminate equivalent productions, leading to the simplified:

```
    E -> number + E
    E -> number
```

The question is, does this lead to the same language?  Well, yes it does!  The language of the first grammar was a string of numbers separated by `+` signs, which is also clearly the language of the above grammar.

### Evaluating an Expression (naively)

In the following sections we will address concerns that primarily occur when trying to process an *AST* produced by our parsing algorithm.  We first provide a *naive* evaluation algorithm, in order to demonstrate its shortcomings and the shortcomings of the grammars we consider.  Here is the algorithm:

```
Evaluate node (AST Node from parsing an Expression)
    if node is a leaf:
        return its value
    else:
        lhs = evaluate left-child
        rhs = evaluate left-child
        return lhs op rhs
```

Here `lhs op rhs` means to apply the operator specified by the node.  Consider the following parse tree:

```
    -    
   / \   
  1   +  
     / \ 
    1   1
```

Our algorithm evaluates the tree by evaluating the root (`-`).  The `lhs` will be `1`, and the rhs is recursively calculated as `1 + 1 = 2`, so the result is `1 - 2 = -1`.

### Dealing with Operator Precedence

Now consider the following grammar, with *left recursion* removed:

```
    E -> number op E
    E -> number
    op -> '+' | '*'
```

Suppose we try to parse the expression `2 * 2 + 1`.  According to standard convention, this expression should be evaluated as `(2 * 2) + 1 = 4 + 1 = 5`.  The parse tree created by our grammar and recursive descent will look like:

```
    *    
   / \   
  2   +  
     / \ 
    2   1
```

Our naive implementation calculates `2 * (2 + 1) = 2 * 3 = 6` which is not correct.  The problem is that the grammar does not distinguish between `+` and `*`, and so cannot address [operator precedence](https://en.wikipedia.org/wiki/Order_of_operations).  Our parser, with this grammar, will always group operations to the right: `a op b op c op d ... = a op (b op (c op (d op ...)))`.  Fortunately, we can fix this with a little "trick."  Consider the following grammar:

```
    E -> ME + E
    E -> ME
    ME -> number * ME
    ME -> number
```

Here `ME` can be thought of as abbreviating "multiplicative-expression."  Our grammar will now parse a sum of mulitplicative expressions, which will each in turn be a product of numbers (perhaps just one).  Now our grammar will parse according to the following productions:

`E -> ME + E -> number * ME + E -> number * number + E -> number * number + ME -> number * number + number`

and results in the following parse tree:

```
    +
   / \
  *   1
 / \ 
2   2
```

This tree, as is easily verified, will naively evaluate to the correct result.

### Troubleshooting: Syntax or Semantics?

The previous section demonstrates a common problem when trying to write a parser.  You won't always attempt to use such generic techniques as we're discussing, however you will always be troubleshooting two different things at once:

* Is my implementation of the parser correct?
* Is my understanding of the language correct?

One advantage of using a parsing technique where the description of the language and implementation of the parser are separate is that you can easily troubleshoot either on or the other.  If you were to implement each *non-terminal* as a method of a class, for instance, then troubleshooting either the language or the parser requires changing the same code.  There are other advantages of not using a generic technique and declarative grammar as we are using, but it does force the issue described.  This can and should directly inform your decisions early on: if you have a strong understanding of the language you are parsing, and it is unlikely to change, you won't get much benefit from using a generic parsing system (unless you are unable to write a decent parser - not enough time perhaps).  On the other hand, if the precise language you need to parse is somewhat uncertain or is likely to change significantly, then a generic system may be useful until requirements stabilize or specific optimizations become necessary.

### Operator Associativity

There is a further consideration.  We've described our *naive evaluation* strategy, and shown before that our grammar had to be modified for our strategy to be correct.  We were able to reflect operator precedence at the grammar-level.  We are not able, using our *recursive-descent*, to handle operator associativity (well, we are only able to handle right-associativity as it stands.  This is still an area of research, you may wish to look at [this paper](https://www.researchgate.net/publication/220177599_A_new_top-down_parsing_algorithm_to_accommodate_ambiguity_and_left_recursion_in_polynomial_time) for other ways to handle this issue).

Consider the following grammar:

```
E -> E op E
E -> number
op -> '+' | '-'
```

And suppose we wish to evaluate the expression `1 - 1 + 1`.  According to standard convention, this should be evaluated as `(1 - 1) + 1 = 1`.  It is important to notice that this is not the same as `1 - (1 + 1) = -1`.  The problem here is that the subtraction operator `-` is not [associative](https://en.wikipedia.org/wiki/Associative_property), that means that in general `(a - b) - c =/= a - (b - c)`.  Here is our parse tree:

```
    -    
   / \   
  1   +  
     / \ 
    1   1
```

When we *naively evaluate* this tree, we get `1 - (1 + 1) = -1` which is not correct.  Unfortunately, the same type of trick won't work as before.  The reason for this has to do with the fact that we are trying our parse from "left to right".  Because a simple parser-engine and declarative syntax were important goals for us, we will opt not to try to fix this issue within the grammar and our parser.  We will call such an issue a "semantic issue," and blame the *naive evaluation* instead.

So the fix is to come up with a *non-naive evaluation* strategy.  We haven't shown the strategy until now because there were considerations that went into the construction of the final expression grammar that needed to be addressed.  Here is the relevant fragment of the grammar:

```
    AddExpr -> MulExpr add_op AddExpr
    AddExpr -> MulExpr
    MulExpr -> Factor mul_op MulExpr
    MulExpr -> Factor
    Factor -> int
```

Nothing should be surprising here at this point.  *Left recursion* has been eliminated, and `add_op` has been given a higher precedence than `mul_op`.  The *non-terminal* `Factor` has been introduced, as we will eventually want to allow *variables* and *parenthesized expressions*.

Now for the (relevant parts of the) evaluation strategy.  We've ommited cases where a node has a single child and `evaluate` should descend without doing anything useful.

```py
def evaluate_expression(node, eval_left = identity_function):
    # see below for `eval_left`
    if node_is_binary_operation:
        # eval_left is passed down to accomodate left-associative operators
        lhs = eval_left(evaluate_expression(left_child))
        _eval_left = lambda next_lhs: _apply_op(lhs, next_lhs)
        if operator_is_not_associative:
            return evaluate_expression(right_child, _eval_left)
        else:
            return apply_operator(lhs, evaluate_expression(right_child))
    else:
        # node is an int
        return int(node.lexeme.value)
```

The most interesting (and obscure) part of this function is the `eval_left` parameter, which is by default the *identity function* which just returns its argument.  To see how `eval_left` is used, consider our previous example `1 - 1 + 1`.  Our root node is `-`.  Instead of returning `lhs - rhs`, we instead return `evaluate(right_node, lambda next_lhs: lhs - next_lhs)`.  When we descend, the value calculated for the `right_child` will be `apply_operator(lhs, evaluate_expression(right_child))`, which is `(lambda next_lhs: lhs - next_lhs)(1) + 1`, which is `(1 - 1) + 1`, WHICH IS correct.

This isn't an exactly "obvious" or "trivial" solution to the problem, but the problem is very common and potentially subtle, so I recommend you keep it in mind when writing your own grammars.

# Dynamic Programming

Now we address the question of efficiency.  To highlight that there is a problem to be solved, we consider the following grammar:

```
    AddExpr -> MulExpr add_op AddExpr
    AddExpr -> MulExpr
    MulExpr -> Factor mul_op AddExpr
    MulExpr -> Factor
    Factor -> lbrace AddExpr rbrace
    Factor -> var
    Factor -> int
```

This is almost our "final" grammar for arithmetic expressions, with one error: the `AddExpr` in the third production should be `MulExpr`, so that the third line should be `MulExpr -> Factor mul_op MulExpr`.  While not the grammar we actually want, its parse is extremely inefficient.

### What do you mean "inefficient?"

In general, the statement "its inefficient" is meaningless unless tied to some [measure of complexity](https://en.wikipedia.org/wiki/Blum_axioms).  Typical measures include "time to complete" or "total space needed".  While we are typically interested in "time to complete," the actual time required to complete the execution of some function can be highly non-deterministic on modern machines, and a truly thorough analysis of algorithms implemented in modern programming languages tends to be prohbitively difficult (would you like to try to figure out how many cpu operations will be necessary to complete any of the algorithms we described?  It would take a long time and probably not be any more helpful than much simpler figures you could come up with).  We will choose our own measure, simply the number of calls to the `parse` function.  While not a precise measure of runtime, if we can keep this number small then we should be able to parse efficiently.

To demonstrate the inefficiency of the parser, suppose we want to parse expressions of the form `x * x * x * x ...`.  The following table records our measurements, where **n** refers to the number of `x`s in the expression:

| n  | total calls |  time  |
|--- | ----------- | ------ |
|  2 |      19     |  0.000 |
|  4 |      91     |  0.001 |
|  6 |     379     |  0.005 |
|  8 |    1531     |  0.009 |
| 10 |    6139     |  0.025 |
| 12 |   24571     |  0.101 |
| 14 |   98299     |  0.394 |
| 16 |  393211     |  1.652 |
| 18 | 1572859     |  6.587 |
| 20 | 6291451     | 25.693 |

**Time** has been provided to aid in intuition a little bit.  It appears that the amount of calls is growing *exponentially.*  This is particularly bad news for and algorithm - most exponential-time complexity algorithms aren't practically useful.  It seems that if we wish to use our parser for anything interesting at all we must reduce this complexity, i.e., we must optimize the parser somehow.

## Dynamic Programming (in a simplified setting)

To demonstrate the technique known as [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming), we will, just like everyone else, optimize a recursive implementation of the [Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_number).  Since we don't want to insult anyone's intelligence, here is the code:

```py
def fibonacci_naive(n: int) -> int:
    return n if n in (0,1) else fibonacci_naive(n-1) + fibonacci_naive(n-2)
```

If we wish to calculate the 20th fibonacci number, this function will be called **21891 times!**  Indeed, the nth fibonacci number is approximately `(.5 + sqrt(5))**n / sqrt(5)`, and the naive recursive implementation must reach a leaf with value `1` or `0`, so it will need to make at least than many calls (the important fact is that this number grows exponentially, even if it has a particularly curious exponent).  There is an obvious way to optimize this calculation.  We simply store `fib(n-1)` and `fib(n-2)` locally, and use them to compute the next value.  Once we've calculated enough of the values, we can return the result:

```py
def fibonacci_optimized(n: int) -> int:
    if n <= 1:
        return n
    prev_val = 0
    cur_val = 1
    i = 2
    while i <= n:
        tmp = cur_val
        cur_val = cur_val + prev_val
        prev_val = tmp
        i += 1
    return cur_val
```

Two things to notice:

1. It's much faster than the previous implementation, and will take `O(n)` time, since it must loop at most `n` times
2. It will take `𝛺(n)` time, since it must loop `n` times (therefore, it's `𝛩(n)`)
3. It's not generalizable
4. It's ugly as all hell

(4) might seem like a joke, but usually when we optimize code we would like to disturb it as little as possible to achieve sufficient improvement.  We've completely obliterated our old implementation with this one.  (3) is less important, it is significant because we are discussing a generic optimization technique.  The time bounds of (1) and (2) seem *okay,* but `𝛩(n)` can be improved somewhat.

First, we'll address (3) with the following implementation:

```py
def fibonacci_bottom_up(n: int) -> int:
    if n == 0: return 0
    fib_sequence = [0,1]
    i = 2
    while i <= n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
        i += 1
    return fib_sequence[-1]
```

This seems quite a bit simpler, and is in fact generalizable.  It leads to [our definition](https://en.wikipedia.org/wiki/Dynamic_programming#Computer_programming) of *bottom-up dynamic programming:*

> Solve the problem by first solving smaller problems, then combine their results to build solutions to bigger problems

Here the *smaller problems* are calculating the fibonacci numbers for `n-1` and `n-2`, then we combine them by adding the smaller solutions together.  A couple things to notice:

1. It's time complexity is still `𝛩(n)`
2. It's space complexity is now `𝛩(n)`
3. It's generalizable

To see that it's generalizable, say we want to compute some [generalized fibonacci sequence](https://en.wikipedia.org/wiki/Generalizations_of_Fibonacci_numbers), given by: `f(n) = f(n - 1) + f(n - 2) + f(n - 3)`.  Here is a possible implementation:

```py
def fibonacci_bottom_up(n: int) -> int:
    if n <= 1: return 0
    fib_sequence = [0,0,1]
    i = 2
    while i <= n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2] + fib_sequence[-3])
        i += 1
    return fib_sequence[-1]
```

It was very easy to alter the optimization method to cover this new form of sequence, and it should be clear how to implement it programatically (at least in principle).  Point (2) is somewhat remarkable, since before we weren't even considering space as an issue, but now we see that we need to keep an array whose size grows to size `n`.  It's worth realizing that this is typically what will happen when you wish to create "generic optimization techniques," you will have to make some tradeoffs.  The reason that this didn't come up before is that before we were using some *domain-specific information* to guide our optimization: we knew that we only needed the previous two values.  Generalizing this to sequences which depend on more previous values means that we will require more space to remember old calculations.

## Memoization

### `memoize.py`

# Demonstration

## Evaluation Visitor