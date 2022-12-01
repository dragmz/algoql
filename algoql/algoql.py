from textx import metamodel_from_file
from .algorand import Algorand
from os import path
from typing import Dict
import base64

def execute(query: str):
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "algoql.tx"))

    mm = metamodel_from_file(filepath)

    a = Algorand()
    m = mm.model_from_str(query)

    def resolve_path(data: Dict, path):
        for part in path.parts:
            data = data.get(part)

        return data

    def resolve_path_alias(path, alias):
        name = alias

        if alias is None:
            name = path.parts[-1]

        return name


    def resolve_op(data, op):
        if op.name == 'BASE64DECODE':
            try:
                decoded = resolve_path(data, op.args[0])
                decoded = base64.b64decode(decoded)

                if len(op.args) == 2:
                    decoded = decoded.decode(op.args[1])

                return decoded
            except:
                return None
        elif op == '' or op == None:
            return value
        else:
            raise Exception(f"unknown op: {op}")

    def resolve_column(data, column):
        if column.ref.path is not None:
            return resolve_path(data, column.ref.path)
        elif column.ref.op is not None:
            return resolve_op(data, column.ref.op)
        else:
            raise Exception("invalid column")

    def resolve_cond(data, cond):
        if cond.binop.a.path is not None:
            return resolve_path(data, cond.binop.a.path)
        elif cond.binop.a.op is not None:
            return resolve_op(data, cond.binop.a.op)
        else:
            raise Exception("invalid binop")

    def run_filters(filters):
        if len(filters) == 0:
            return True

        for filter in filters:
            for alt in filter.alts:
                if run_alt(alt):
                    return True

        return False
    def test_condition(data: Dict, cond):
        def resolve_test_value(value):
            if value == 'NULL':
                return None

            return value

        if cond.binop is not None:
            actual = resolve_cond(data, cond)

            if cond.binop.operator == '=':
                test = resolve_test_value(cond.binop.b)
                if not (actual == test):
                    return False
            elif cond.binop.operator == '!=':
                test = resolve_test_value(cond.binop.b)
                if not (actual != test):
                    return False
            elif cond.binop.operator == 'IS NOT':
                test = resolve_test_value(cond.binop.b)
                if not (actual != test):
                    return False
            elif cond.binop.operator == 'IS':
                test = resolve_test_value(cond.binop.b)
                if not (actual == test):
                    return False
            else:
                raise Exception(f"unknown operator: {cond.binop.operator}")
        elif cond.group is not None:
            return run_filters(cond.group.filters)
        else:
            raise Exception("unknown cond")

        return True

    for block in a.blocks():
        for s in m.statements:
            tables = {}

            main_table = None
            main_name = None

            for item in s.tables:
                name = resolve_path_alias(item.path, item.alias)
                table = resolve_path(block, item.path)

                if main_table is None:
                    if not type(table) in (tuple, list):
                        table = [table]

                    main_table = table
                    main_name = name
                else:
                    tables[name] = table

            for item in main_table:
                data = {main_name: item}

                for other_name, other_table in tables.items():
                    data[other_name] = other_table

                def run_alt(alt):
                    for cond in alt.conds:
                        if not test_condition(data, cond):
                            return False

                    return True

                if run_filters(s.filters):
                    row = {}

                    index = 0
                    for column in s.columns:
                        if column.ref.path is not None:
                            name = resolve_path_alias(column.ref.path, column.alias)
                        elif column.alias is not None:
                            name = column.alias
                        else:
                            name = str(index)

                        value = resolve_column(data, column)

                        row[name] = value
                        index += 1

                    yield row
