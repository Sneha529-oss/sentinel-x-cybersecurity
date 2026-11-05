"""
SENTINEL X - Regex Parser & Shunting-Yard
PRN: 202401110046

Parses regular expressions for the automata engine:
1. Validates balanced parentheses and operator syntax.
2. Inserts explicit concatenation tokens.
3. Converts infix regex to postfix notation using Dijkstra's Shunting-Yard algorithm.
"""

class RegexParseError(Exception):
    """Custom exception for regex parsing errors."""
    pass

EPSILON = "ε"

def tokenize_and_insert_concat(pattern: str) -> list:
    """
    Scans the pattern, handles escape sequences, and inserts explicit concatenation
    operators (denoted as '·') where two tokens are adjacent.
    """
    if not pattern:
        raise RegexParseError("Regular expression cannot be empty.")

    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        char = pattern[i]

        if char == '\\':
            if i + 1 >= n:
                raise RegexParseError("Trailing backslash in regular expression.")
            next_char = pattern[i + 1]
            # Escaped character is treated as a literal symbol
            tokens.append({"type": "SYMBOL", "val": next_char})
            i += 2
        elif char in ['*', '+', '?']:
            if not tokens or tokens[-1]["type"] in ["UNION", "CONCAT", "LPAREN"]:
                raise RegexParseError(f"Quantifier '{char}' follows nothing valid.")
            tokens.append({"type": "QUANTIFIER", "val": char})
            i += 1
        elif char == '|':
            if not tokens or tokens[-1]["type"] in ["UNION", "LPAREN"]:
                raise RegexParseError("Alternation '|' must have a left operand.")
            tokens.append({"type": "UNION", "val": "|"})
            i += 1
        elif char == '(':
            tokens.append({"type": "LPAREN", "val": "("})
            i += 1
        elif char == ')':
            if not tokens or tokens[-1]["type"] in ["UNION", "LPAREN"]:
                raise RegexParseError("Empty or invalid group before ')'.")
            tokens.append({"type": "RPAREN", "val": ")"})
            i += 1
        elif char in [' ', '\t', '\r', '\n']:
            # Allow whitespace separation if unescaped or treat as literal if needed
            # For automata expressions, whitespace is often ignorable unless escaped.
            i += 1
        else:
            tokens.append({"type": "SYMBOL", "val": char})
            i += 1

    if not tokens:
        raise RegexParseError("No valid tokens found in expression.")

    if tokens[-1]["type"] == "UNION":
        raise RegexParseError("Trailing alternation '|' without right operand.")

    # Insert explicit concatenation
    # Concatenation occurs between:
    # (SYMBOL, QUANTIFIER, RPAREN) and (SYMBOL, LPAREN)
    concat_tokens = []
    for idx in range(len(tokens)):
        t1 = tokens[idx]
        concat_tokens.append(t1)

        if idx + 1 < len(tokens):
            t2 = tokens[idx + 1]
            can_end_term = (t1["type"] in ["SYMBOL", "QUANTIFIER", "RPAREN"])
            can_start_term = (t2["type"] in ["SYMBOL", "LPAREN"])

            if can_end_term and can_start_term:
                concat_tokens.append({"type": "CONCAT", "val": "·"})

    return concat_tokens

def infix_to_postfix(pattern: str) -> list:
    """
    Converts an infix regex into postfix notation using Dijkstra's Shunting-Yard algorithm.
    Operator precedence:
      *, +, ? (unary postfix) > · (concatenation) > | (alternation)
    """
    tokens = tokenize_and_insert_concat(pattern)

    precedence = {
        "|": 1,
        "·": 2,
        "*": 3,
        "+": 3,
        "?": 3
    }

    output = []
    op_stack = []

    for token in tokens:
        ttype = token["type"]
        val = token["val"]

        if ttype == "SYMBOL":
            output.append(token)
        elif ttype == "QUANTIFIER":
            # Postfix unary operators are output immediately or pushed
            # Since *, +, ? are already postfix in infix notation, we can append directly
            output.append(token)
        elif ttype == "LPAREN":
            op_stack.append(token)
        elif ttype == "RPAREN":
            matched_lparen = False
            while op_stack:
                top = op_stack.pop()
                if top["type"] == "LPAREN":
                    matched_lparen = True
                    break
                output.append(top)
            if not matched_lparen:
                raise RegexParseError("Unbalanced parentheses: missing opening '('.")
        elif ttype in ["CONCAT", "UNION"]:
            curr_prec = precedence[val]
            while op_stack:
                top = op_stack[-1]
                if top["type"] == "LPAREN":
                    break
                top_prec = precedence.get(top["val"], 0)
                if top_prec >= curr_prec:
                    output.append(op_stack.pop())
                else:
                    break
            op_stack.append(token)

    while op_stack:
        top = op_stack.pop()
        if top["type"] == "LPAREN":
            raise RegexParseError("Unbalanced parentheses: missing closing ')'.")
        output.append(top)

    return output

def parse_regex_to_postfix(pattern: str) -> list:
    """Convenience entry point that validates and returns postfix tokens."""
    return infix_to_postfix(pattern)

