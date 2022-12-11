# Introduction

# Grammars

*Grammars* are used to define the syntax formal languages, and are typically (part of) the input to generic parsers or parser generators.  We will be interested in a class of grammars known as *context-free* grammars.

## Motivational Example

To motivate *context-free* grammars, let's consider the syntax of arithmetic expressions.  We will suppose that we have the typical operators `+ - * /`, and for simplicity we'll only consider expressions involving non-negative integers.

According to [wikipedia](https://en.wikipedia.org/wiki/Formal_grammar)

> In formal language theory, a grammar (when the context is not given, often called a formal grammar for clarity) describes how to form strings from a language's alphabet that are valid according to the language's syntax. A grammar does not describe the meaning of the strings or what can be done with them in whatever context—only their form. A formal grammar is defined as a set of production rules for such strings in a formal language.

# Parsers

Suppose we would like to interpret arithmetic expressions in some text, and evaluate them given the values of the variables.

## Recursive Descent Parsers

### `recursive_descent_parser.py`

# Dynamic Programming

## Memoization

### `memoize.py`

# Demonstration

## Evaluation Visitor