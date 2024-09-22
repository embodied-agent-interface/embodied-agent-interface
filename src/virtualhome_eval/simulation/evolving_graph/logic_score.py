import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
import re


class Expression:
    def evaluate(self, context):
        raise NotImplementedError("This method should be implemented by subclasses.")


class Literal(Expression):
    def __init__(self, name):
        self.name = name

    def evaluate(self, context):
        return context.get(self.name, False)

    def __repr__(self):
        return self.name


class Not(Expression):
    def __init__(self, expression):
        self.expression = expression

    def evaluate(self, context):
        return not self.expression.evaluate(context)

    def __repr__(self):
        return f"(not {self.expression})"


class And(Expression):
    def __init__(self, *args):
        self.args = args

    def evaluate(self, context):
        return all(arg.evaluate(context) for arg in self.args)

    def __repr__(self):
        return f"({' and '.join(map(str, self.args))})"


class Or(Expression):
    def __init__(self, *args):
        self.args = args

    def evaluate(self, context):
        return all(arg.evaluate(context) for arg in self.args)

    def __repr__(self):
        return f"({' or '.join(map(str, self.args))})"


class When(Expression):
    def __init__(self, condition, consequence):
        self.condition = condition
        self.consequence = consequence

    def evaluate(self, context):
        return (
            self.consequence.evaluate(context)
            if self.condition.evaluate(context)
            else True
        )

    def __repr__(self):
        return f"(when {self.condition} {self.consequence})"


class Exists(Expression):
    def __init__(self, variable, body):
        self.variable = variable
        self.body = body

    def evaluate(self, context):
        # Simplified evaluation logic for demonstration
        return all(
            self.body.evaluate({**context, self.variable: val}) for val in [True, False]
        )

    def __repr__(self):
        return f"(exists {self.variable} {self.body})"


class Forall(Expression):
    def __init__(self, variable, body):
        self.variable = variable
        self.body = body

    def evaluate(self, context):
        # Simplified evaluation logic for demonstration
        return all(
            self.body.evaluate({**context, self.variable: val}) for val in [True, False]
        )

    def __repr__(self):
        return f"(forall {self.variable} {self.body})"


def parse_expression(expression):
    if isinstance(expression, str) or isinstance(expression, bool):
        return Literal(str(expression))
    op, *args = expression
    if op == "not":
        assert len(args) == 1, "NOT operator should have exactly one argument"
        return Not(parse_expression(args[0]))
    elif op == "when":
        assert len(args) == 2, "WHEN operator should have exactly two arguments"
        return When(parse_expression(args[0]), parse_expression(args[1]))
    elif op == "exists" or op == "forall":
        assert (
            len(args) == 2
        ), "EXISTS and FORALL operators should have exactly two arguments"
        if op == "exists":
            return Exists(args[0], parse_expression(args[1]))
        else:
            return Forall(args[0], parse_expression(args[1]))
    parsed_args = [parse_expression(arg) for arg in args]
    if op == "and":
        return And(*parsed_args)
    elif op == "or":
        return Or(*parsed_args)


def match_expressions(expr1, expr2):
    matched_expr1 = []
    unmatched_expr1 = []
    unmatched_expr2 = []
    # Check for type and direct string comparison
    if isinstance(expr1, Literal) and isinstance(expr2, Literal):
        if expr1.name == expr2.name:
            matched_expr1.append(expr1)
            return (1, matched_expr1, unmatched_expr1, unmatched_expr2)
        else:
            return (0, matched_expr1, [expr1], [expr2])

    if type(expr1) != type(expr2):
        return (0, [], [expr1], [expr2])

    # Handle Not, Exists, Forall expressions
    if isinstance(expr1, Not):
        score, matched_sub, um1, um2 = match_expressions(
            expr1.expression, expr2.expression
        )
        if score > 0:
            matched_expr1.append(expr1)
        else:
            unmatched_expr1.append(expr1)
            unmatched_expr2.append(expr2)
        return (score, matched_expr1, unmatched_expr1, unmatched_expr2)

    if isinstance(expr1, When):
        cond_score, cond_matched_sub, cond_um1, cond_um2 = match_expressions(
            expr1.condition, expr2.condition
        )
        cons_score, cons_matched_sub, cons_um1, cons_um2 = match_expressions(
            expr1.consequence, expr2.consequence
        )
        score = 1 if cond_score == 1 and cons_score == 1 else 0
        if score == 1:
            matched_expr1.append(expr1)
        else:
            unmatched_expr1.append(expr1)
            unmatched_expr2.append(expr2)
        return (score, matched_expr1, unmatched_expr1, unmatched_expr2)

    if isinstance(expr1, (Exists, Forall)):
        if expr1.variable == expr2.variable:
            score, matched_sub, um1, um2 = match_expressions(expr1.body, expr2.body)
            if score > 0:
                matched_expr1.append(expr1)
            else:
                unmatched_expr1.append(expr1)
                unmatched_expr2.append(expr2)
            return (score, matched_expr1, unmatched_expr1, unmatched_expr2)
        else:
            return (0, matched_expr1, [expr1], [expr2])

    # Handle And, Or expressions
    if isinstance(expr1, (And, Or)):
        sub1 = expr1.args
        sub2 = expr2.args
        size1, size2 = len(sub1), len(sub2)
        adj_matrix = np.zeros((size1, size2), dtype=int)
        matched_parts = []

        for i in range(size1):
            for j in range(size2):
                adj_matrix[i, j], matched_sub, _, _ = match_expressions(
                    sub1[i], sub2[j]
                )
                if adj_matrix[i, j] > 0:
                    matched_parts.extend(matched_sub)

        sparse_matrix = csr_matrix(adj_matrix)
        match_result = maximum_bipartite_matching(sparse_matrix, perm_type="column")
        total_match = sum(
            adj_matrix[i, match_result[i]]
            for i in range(size1)
            if match_result[i] != -1
        )
        max_possible_match = min(size1, size2)

        # Collect unmatched expressions
        unmatched_expr1 = [
            sub1[i]
            for i in range(size1)
            if i not in match_result or match_result[i] == -1
        ]
        unmatched_expr2 = [sub2[j] for j in range(size2) if j not in match_result.T]

        return (
            total_match / max_possible_match if max_possible_match > 0 else 0,
            matched_parts,
            unmatched_expr1,
            unmatched_expr2,
        )

    return (0, matched_expr1, [expr1], [expr2])


# Example use case
# Example
# expr1 = parse_expression(('or', ('exists', 'x', 'y'), ('forall', 'y', ('or', 'c', 'd'))))
# expr2 = parse_expression(('or', ('exists', 'x', 'y'), False))

# score = match_expressions(expr1, expr2)
# print("Similarity Score:", score)


def tokenize(expression):
    # pattern = r'\(|\)|\b(and|or|not|exists|forall)\b|[\w-]+(?:\s[\?\w-]+)*'
    tokens = []
    buffer = ""

    for char in expression:
        if char in "()":
            if buffer:
                tokens.append(buffer.strip())
                buffer = ""
            tokens.append(char)
        elif re.match(r"\s", char):
            if buffer:
                buffer += char
        else:
            buffer += char

    # Add the last token if any
    if buffer:
        tokens.append(buffer.strip())

    return tokens


def parse_pddl_expr(tokens):
    stack = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "(":
            stack.append(token)
        elif token == ")":
            if stack[-1] == "(":
                stack.pop()
                stack.append("()")
                i += 1
                continue
            subexpr = []
            while stack and stack[-1] != "(":
                subexpr.append(stack.pop())
            stack.pop()  # Remove the '('
            subexpr.reverse()

            # Determine how to process the collected subexpression
            if subexpr[0] in {"and", "or"}:
                stack.append((subexpr[0], *subexpr[1:]))
            elif subexpr[0] == "not":
                assert (
                    len(subexpr) == 2
                ), f"NOT should have exactly one argument,  {subexpr=}"
                stack.append(("not", subexpr[1]))
            elif subexpr[0] in {"exists", "forall"}:
                assert (
                    len(subexpr) == 3
                ), f"EXISTS and FORALL should have exactly two arguments, {subexpr=}"
                stack.append((subexpr[0], subexpr[1], subexpr[2]))
            elif subexpr[0] == "when":
                assert (
                    len(subexpr) == 3
                ), f"WHEN should have exactly two arguments, {subexpr=}"
                stack.append(("when", subexpr[1], subexpr[2]))
            else:
                # print(f'{subexpr=}')
                stack.append(" ".join(subexpr))
        else:
            stack.append(token)
        i += 1

    if len(stack) == 1:
        return stack[0]
    else:
        raise Exception("Parsing error, check the structure of the input expression")


def parse_pddl_input(expression):
    tokens = tokenize(expression)
    # print(f'{tokens=}')
    return parse_pddl_expr(tokens)


def replace_in_tuple(tup, old_variable, new_variable):
    if not isinstance(tup, tuple):
        return tup.replace(old_variable, new_variable)

    return tuple(replace_in_tuple(item, old_variable, new_variable) for item in tup)


def align_expressions(expr1, expr2):
    if isinstance(expr1, str) and isinstance(expr2, str):
        return expr1, expr2
    if isinstance(expr1, str) or expr1 == "()":
        return expr1, expr2 if isinstance(expr2, tuple) else expr2
    if isinstance(expr2, str) or expr2 == "()":
        return expr1 if isinstance(expr1, tuple) else expr1, expr2

    if isinstance(expr1, tuple):
        op1, *args1 = expr1
    else:
        op1, args1 = expr1, []

    if isinstance(expr2, tuple):
        op2, *args2 = expr2
    else:
        op2, args2 = expr2, []

    aligned_args1, aligned_args2 = [], []

    if op1 == op2 and op1 in {"exists", "forall"}:
        var1, body1 = args1
        var2, body2 = args2
        var1_name = var1.split("-")[0].strip()
        var2_name = var2.split("-")[0].strip()
        # recursively replace the variable name in the tuple
        var2 = replace_in_tuple(var2, var2_name, var1_name)
        body2 = replace_in_tuple(body2, var2_name, var1_name)
        aligned_args1.append(var1)
        aligned_args2.append(var2)
        aligned_args1.append(body1)
        aligned_args2.append(body2)
        return (op1, *aligned_args1), (op2, *aligned_args2)

    # Adjust behavior based on the operator type
    if op1 in {"and", "or"} and op2 in {"and", "or"}:
        max_length = max(len(args1), len(args2))
        for i in range(max_length):
            sub_expr1 = args1[i] if i < len(args1) else "()"
            sub_expr2 = args2[i] if i < len(args2) else "()"
            aligned_sub_expr1, aligned_sub_expr2 = align_expressions(
                sub_expr1, sub_expr2
            )
            aligned_args1.append(aligned_sub_expr1)
            aligned_args2.append(aligned_sub_expr2)
        return (op1, *aligned_args1), (op2, *aligned_args2)
    else:
        # For NOT, WHEN, FORALL, EXISTS, treat as atomic units
        return expr1, expr2


def extract_predicates(expression):
    predicates = set()

    if isinstance(expression, Literal):
        # Assuming any Literal is a predicate unless structured parsing indicates otherwise
        pd = expression.name.split(" ")[0]
        predicates.add(pd)
    elif isinstance(expression, Not):
        predicates.update(extract_predicates(expression.expression))
    elif isinstance(expression, (And, Or)):
        for arg in expression.args:
            predicates.update(extract_predicates(arg))
    elif isinstance(expression, When):
        predicates.update(extract_predicates(expression.condition))
        predicates.update(extract_predicates(expression.consequence))
    elif isinstance(expression, (Exists, Forall)):
        # Dive into the body of the quantified expression to find predicates
        predicates.update(extract_predicates(expression.body))

    return predicates


def identify_predicates(unmatched_expressions):
    all_predicates = set()
    for expr in unmatched_expressions:
        predicates = extract_predicates(expr)
        all_predicates.update(predicates)
    return all_predicates


def calculate_logic_score(input_str1, input_str2):
    try:
        parsed_expression1 = parse_pddl_input(input_str1)
        parsed_expression2 = parse_pddl_input(input_str2)
        aligned_expr1, aligned_expr2 = align_expressions(
            parsed_expression1, parsed_expression2
        )
        expr1 = parse_expression(aligned_expr1)
        expr2 = parse_expression(aligned_expr2)
        score, matched, unmatched_expr1, unmatched_expr2 = match_expressions(
            expr1, expr2
        )
    except Exception as e:
        # print("Calculation failed!")
        # raise e
        # print(f"{input_str1=}")
        # print(f"{input_str2=}")
        score, matched, unmatched_expr1, unmatched_expr2 = (
            0.0,
            [],
            [input_str1],
            [input_str2],
        )
    # get predicates in unmatched_expr
    predicates_unmatched1 = identify_predicates(unmatched_expr1)
    predicates_unmatched2 = identify_predicates(unmatched_expr2)
    predicates_matched = identify_predicates(matched)

    return score, predicates_matched, predicates_unmatched1, predicates_unmatched2


# Example usage

# input_str1 = "(and (next_to ?char ?obj) (forall (?close_obj - object) (when (exists (?c - object) (when (next_to ?c d) b)) e)) (forall (?close_obj - object) (when (obj_next_to ?close_obj ?obj) (next_to ?char ?close_obj))))"
# input_str2 = "(and (next_to ?char ?obj) (forall (?far_obj - object) (when (exists (?a - object) (when (next_to ?a d) b)) e) f) (forall (?close_obj - object) (when (obj_next_to ?close_obj ?obj) (next_to ?char ?close_obj))))"

input_str1 = "(forall (?close_obj - object) (when (exists (?c - object) (when (next_to ?c d) b)) e))"
input_str2 = "(forall (?close_obj - object) (when (exists (?c - object) (when (next_to ?c d) b)) e))"

