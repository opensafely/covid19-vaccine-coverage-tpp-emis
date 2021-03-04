import json
import os
import re
from itertools import groupby
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    out_path = (
        Path(os.path.abspath(__file__)).parents[1] / "tests" / "test_add_groupings.py"
    )

    with open(out_path, "w") as f:
        write_add_groupings(get_groupings(spec), f)

    os.system(f"black {out_path}")


def write_add_groupings(groupings, f):
    f.write(
        """
import numpy as np
import pandas as pd

from analysis.transform import load_raw_cohort, transform
"""
    )

    for g in groupings:
        f.write(f"def test_{g['column']}():\n")
        f.write('    raw_cohort = load_raw_cohort("tests/input.csv")\n')
        f.write("    cohort = transform(raw_cohort)\n\n")
        f.write("    for ix, row in cohort.iterrows():\n")

        max_width = max(len(s[0]) for s in g["steps"])
        for condition, (action_true, action_false), expr in g["steps"][:-1]:
            f.write(f"        # {condition.ljust(max_width)} | ")
            f.write(f"{action_true.ljust(6)} | {action_false.ljust(6)}\n")
            if action_true == "Select":
                f.write(f"        if {render_expr(expr)}:\n")
                f.write(f"            assert row['{g['column']}']\n")
            elif action_true == "Reject":
                f.write(f"        if {render_expr(expr)}:\n")
                f.write(f"            assert not row['{g['column']}']\n")
            elif action_false == "Select":
                f.write(f"        if {render_expr(negate_expr(expr))}:\n")
                f.write(f"            assert row['{g['column']}']\n")
            else:
                f.write(f"        if {render_expr(negate_expr(expr))}:\n")
                f.write(f"            assert not row['{g['column']}']\n")
            f.write("            continue\n")
            f.write("\n")

        condition, (action_true, action_false), expr = g["steps"][-1]
        f.write(f"        # {condition.ljust(max_width)} | ")
        f.write(f"{action_true.ljust(6)} | {action_false.ljust(6)}\n")
        f.write(f"        if {render_expr(expr)}:\n")
        if action_true == "Select":
            f.write(f"            assert row['{g['column']}']\n")
            f.write("        else:\n")
            f.write(f"            assert not row['{g['column']}']\n")
        else:
            f.write(f"            assert not row['{g['column']}']\n")
            f.write("        else:\n")
            f.write(f"            assert row['{g['column']}']\n")
        f.write("\n")

        f.write("\n\n")
    f.write(
            """
def gt(lhs, rhs):
    if lhs is np.nan:
        return False

    if rhs is np.nan:
        return True

    return lhs > rhs


def gte(lhs, rhs):
    if lhs is np.nan:
        return False

    if rhs is np.nan:
        return True

    return lhs >= rhs
"""
        )


def get_groupings(spec):
    for g in spec["bandings_and_groupings"][3:]:
        column = g["banding_key"].lower().replace("*", "")
        rows = g["rows"]
        conditions = [r[0] for r in rows]
        actions = [(r[1], r[2]) for r in rows]
        exprs = [build_step_expr(c) for c in conditions]

        yield {
            "group": g["banding_name"],
            "column": column,
            "steps": list(zip(conditions, actions, exprs)),
        }


def build_step_expr(c):
    assert c.startswith("IF ")
    c = c[3:]
    exprs = [build_comparison_expr(s1) for s1 in c.split(" AND ")]
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
        return f'row["{col}"]'

    if op == "V":
        val = operands[0]
        return repr(val)

    if op == ">":
        lhs, rhs = operands
        return f"gt({render_expr(lhs)}, {render_expr(rhs)})"

    if op == ">=":
        lhs, rhs = operands
        return f"gte({render_expr(lhs)}, {render_expr(rhs)})"

    if op in ["&", "|"]:
        return "(" + f" {op} ".join(render_expr(operand) for operand in operands) + ")"

    if op == "null":
        val = operands[0]
        return f"(pd.isnull({render_expr(val)}))"

    if op == "notnull":
        val = operands[0]
        return f"(pd.notnull({render_expr(val)}))"

    if op == "~":
        return f"not {render_expr(operands)}"

    assert False, op


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
