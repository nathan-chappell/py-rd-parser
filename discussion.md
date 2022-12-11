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

Suppose that we have been given some *grammar*.  We know that it describes some *language.*  Suppose we have some *text* `T`, and we know

## Recursive Descent Parsers

### `recursive_descent_parser.py`

# Dynamic Programming

## Memoization

### `memoize.py`

# Demonstration

## Evaluation Visitor