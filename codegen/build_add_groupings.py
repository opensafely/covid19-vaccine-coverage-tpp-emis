import json
import os
import re
from itertools import groupby
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    out_path = (
        Path(os.path.abspath(__file__)).parents[1] / "analysis" / "add_groupings.py"
    )

    with open(out_path, "w") as f:
        write_add_groupings(get_groupings(spec), f)

    os.system(f"black {out_path}")


def write_add_groupings(groupings, f):
    f.write("from comparisons import gt, gte, lt, lte\n\n\n")
    f.write("def add_groupings(df):\n")
    for g in groupings:
        f.write(f"    # {g['group']}\n")
        f.write("    #\n")
        max_width = max(len(r[0]) for r in g["rows"])
        for r in g["rows"]:
            f.write(
                f"    # {r[0].ljust(max_width)} | {r[1].ljust(6)} | {r[2].ljust(6)}\n"
            )
        f.write(f'    df["{g["column"]}"] = {g["expr"]}\n\n')


def get_groupings(spec):
    for g in spec["bandings_and_groupings"][3:]:
        column = g["banding_key"].lower().replace("*", "")
        rows = g["rows"]
        actions = [r[1][0] + r[2][0] for r in rows]

        assert all(action in ["SN", "RN", "NS", "NR"] for action in actions[:-1])
        assert actions[-1] in ["SR", "RS"]

        step_exprs = [build_step_expr(r) for r in g["rows"]]
        expr = combine_step_exprs(actions, step_exprs)
        rendered = render_expr(expr)

        yield {
            "group": g["banding_name"],
            "rows": g["rows"],
            "column": column,
            "expr": rendered,
        }


def build_step_expr(r):
    s = r[0]
    assert s.startswith("IF ")
    s = s[3:]
    exprs = [build_comparison_expr(s1) for s1 in s.split(" AND ")]
    if len(exprs) == 1:
        return exprs[0]
    else:
        return ["&", exprs]


def build_comparison_expr(s):
    s = s.split("(")[0].strip()
    s = s.replace(" _DAT", "_DAT")
    s = re.sub("([^_])GROUP", r"\1_GROUP", s)  # eg s/IMMUNOGROUP/IMMUNO_GROUP/
    s = re.sub(r"(ASTRXM\d) ", r"\1_DAT ", s)  # eg s/ASTRXM1 /ASTRXM1_DAT /
    s = re.sub(" ?= ?", "=", s)
    s = re.sub(" ?> ?", ">", s)
    s = re.sub(" ?< ?", "<", s)
    s = s.lower()

    if m := re.match(r"(\w+)=null$", s):
        col = m.groups()[0]
        if col.endswith("_group"):
            return ["L", [col]]
        else:
            return ["null", [("L", [col])]]

    if m := re.match(r"(\w+)<>null$", s):
        col = m.groups()[0]
        if col.endswith("_group"):
            return ["L", [col]]
        else:
            return ["notnull", [("L", [col])]]

    if m := re.match(r"(\w+)(>=?)(\w+)$", s):
        lhs, op, rhs = m.groups()
        try:
            rhs = int(rhs)
            return [op, [("L", [lhs]), ("V", [rhs])]]
        except ValueError:
            return [op, [("L", [lhs]), ("L", [rhs])]]

    assert False, s


def combine_step_exprs(actions, step_exprs):
    n = len(actions)
    ix = n - 1

    if actions[-1] == "SR":
        combined_expr = step_exprs[ix]
    elif actions[-1] == "RS":
        combined_expr = negate_expr(step_exprs[ix])
    else:
        assert False, actions[-1]

    ix -= 1

    for action, group in groupby(actions[:-1][::-1]):
        l = len(list(group))
        step_exprs_for_group = [step_exprs[ix - i] for i in reversed(range(l))]
        negated_step_exprs_for_group = [
            negate_expr(expr) for expr in step_exprs_for_group
        ]

        if action == "SN":
            if combined_expr[0] == "|":
                combined_expr[1] = step_exprs_for_group + combined_expr[1]
            else:
                combined_expr = ["|", step_exprs_for_group + [combined_expr]]

        elif action == "NS":
            if combined_expr[0] == "|":
                combined_expr[1] = negated_step_exprs_for_group + combined_expr[1]
            else:
                combined_expr = ["|", negated_step_exprs_for_group + [combined_expr]]

        elif action == "RN":
            if combined_expr[0] == "&":
                combined_expr[1] = negated_step_exprs_for_group + combined_expr[1]
            else:
                combined_expr = ["&", negated_step_exprs_for_group + [combined_expr]]

        elif action == "NR":
            if combined_expr[0] == "&":
                combined_expr[1] = step_exprs_for_group + combined_expr[1]
            else:
                combined_expr = ["&", step_exprs_for_group + [combined_expr]]

        else:
            assert False, action

        ix -= l

    return combined_expr


def negate_expr(expr):
    op, operands = expr

    if op == "==":
        return "!=", operands

    if op == "!=":
        return "==", operands

    if op == ">":
        lhs, rhs = operands
        return "<=", [lhs, rhs]

    if op == ">=":
        lhs, rhs = operands
        return "<", [lhs, rhs]

    if op == "&":
        return "|", [negate_expr(operand) for operand in operands]

    if op == "|":
        return "&", [negate_expr(operand) for operand in operands]

    if op == "null":
        return "notnull", operands

    if op == "notnull":
        return "null", operands

    if op == "L":
        return "~", [op, operands]

    assert False, op


def render_expr(expr):
    op, operands = expr

    if op == "L":
        col = operands[0]
        return f'df["{col}"]'

    if op == "V":
        val = operands[0]
        return repr(val)

    if op in [">", ">=", "<", "<="]:
        lhs, rhs = operands
        
        if rhs[0] == "V":
            return f"({render_expr(lhs)} {op} {render_expr(rhs)})"

        fn = {">": "gt", ">=": "gte", "<": "lt", "<=": "lte"}[op]
        return f"{fn}({render_expr(lhs)}, {render_expr(rhs)})"

    if op in ["&", "|"]:
        return "(" + f" {op} ".join(render_expr(operand) for operand in operands) + ")"

    if op == "null":
        val = operands[0]
        return f"{render_expr(val)}.isnull()"

    if op == "notnull":
        val = operands[0]
        return f"{render_expr(val)}.notnull()"

    assert False, op


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
