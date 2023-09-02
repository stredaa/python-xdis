"""
Routines for formatting opcodes.
"""
from typing import Optional, Tuple


def extended_format_binary_op(
    opc, instructions: list, fmt_str: str
) -> Tuple[str, Optional[int]]:
    """
    General routine for formatting binary operations.
    A binary operations pops a two arguments off of the evaluation stack and
    pushes a single value back on the evaluation stack. Also, the instruction
    must not raise an exception and must control must flow to the next instruction.

    instructions is a list of instructions
    fmt_str is a format string that indicates the two arguments.

    the return constins the string that should be added to tos_str and
    the position in instructions of the first instruction where that contributes
    to the binary operation, that is the logical beginning instruction.
    """
    i = skip_cache(instructions, 1)
    stack_inst1 = instructions[i]
    arg1 = None
    if stack_inst1.tos_str is not None:
        arg1 = stack_inst1.tos_str
    if arg1 is not None or stack_inst1.opcode in opc.operator_set:
        if arg1 is None:
            arg1 = stack_inst1.argrepr
        arg1_start_offset = stack_inst1.start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = skip_cache(instructions, i + 1)
        stack_inst2 = instructions[j]
        if (
            stack_inst1.opcode in opc.operator_set
            and stack_inst2.opcode in opc.operator_set
        ):
            arg2 = get_instruction_arg(stack_inst2, stack_inst2.argrepr)
            start_offset = stack_inst2.start_offset
            return fmt_str % (arg2, arg1), start_offset
        elif stack_inst2.start_offset is not None:
            start_offset = stack_inst2.start_offset
            arg2 = get_instruction_arg(stack_inst2, stack_inst2.argrepr)
            if arg2 == "":
                arg2 = "..."
            return fmt_str % (arg2, arg1), start_offset
        else:
            return fmt_str % ("...", arg1), None
    return "", None


def extended_format_infix_binary_op(
    opc, instructions, op_str: str
) -> Tuple[str, Optional[int]]:
    """ """
    i = 1
    # 3.11+ has CACHE instructions
    while instructions[i].opname == "CACHE":
        i += 1
    stack_arg1 = instructions[i]
    arg1 = None
    if stack_arg1.tos_str is not None:
        arg1 = stack_arg1.tos_str
    if arg1 is not None or stack_arg1.opcode in opc.operator_set:
        if arg1 is None:
            arg1 = instructions[1].argrepr
        else:
            arg1 = f"({arg1})"
        arg1_start_offset = instructions[1].start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = i + 1
        # 3.11+ has CACHE instructions
        while instructions[j].opname == "CACHE":
            j += 1
        if (
            instructions[j].opcode in opc.operator_set
            and instructions[i].opcode in opc.operator_set
        ):
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            start_offset = instructions[j].start_offset
            return f"{arg2}{op_str}{arg1}", start_offset
        elif instructions[j].start_offset is not None:
            start_offset = instructions[j].start_offset
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            if arg2 == "":
                arg2 = "..."
            else:
                arg2 = f"({arg2})"
            return f"{arg2}{op_str}{arg1}", start_offset
        else:
            return f"...{op_str}{arg1}", None
    return "", None


def extended_format_store_op(opc, instructions: list) -> Tuple[str, Optional[int]]:
    inst = instructions[0]
    prev_inst = instructions[1]
    start_offset = prev_inst.offset
    if prev_inst.opname == "IMPORT_NAME":
        return f"{inst.argval} = import_module({inst.argval})", start_offset
    elif prev_inst.opname == "IMPORT_FROM":
        return f"{inst.argval} = import_module({prev_inst.argval})", start_offset
    elif prev_inst.opcode in opc.operator_set:
        if prev_inst.opname == "LOAD_CONST":
            argval = safe_repr(prev_inst.argval)
        elif (
            prev_inst.opcode in opc.VARGS_OPS | opc.NARGS_OPS
            and prev_inst.tos_str is None
        ):
            # In variable arguments lists and function-like calls
            # argval is a count. So we need a TOS representation
            # to do something here.
            return "", start_offset
        else:
            argval = prev_inst.argval

        argval = get_instruction_arg(prev_inst, argval)
        start_offset = prev_inst.start_offset
        if prev_inst.opname.startswith("INPLACE_"):
            # Inplace operators show their own assign
            return argval, start_offset
        return f"{inst.argval} = {argval}", start_offset

    return "", start_offset


def extended_format_ternary_op(
    opc, instructions, fmt_str: str
) -> Tuple[str, Optional[int]]:
    """
    General routine for formatting ternary operations.
    A ternary operations pops a three arguments off of the evaluation stack and
    pushes a single value back on the evaluation stack. Also, the instruction
    must not raise an exception and must control must flow to the next instruction.

    instructions is a list of instructions
    fmt_str is a format string that indicates the two arguments.

    the return constins the string that should be added to tos_str and
    the position in instructions of the first instruction where that contributes
    to the binary operation, that is the logical beginning instruction.
    """
    i = skip_cache(instructions, 1)
    stack_inst1 = instructions[i]
    arg1 = None
    if stack_inst1.tos_str is not None:
        arg1 = stack_inst1.tos_str
    if arg1 is not None or stack_inst1.opcode in opc.operator_set:
        if arg1 is None:
            arg1 = stack_inst1.argrepr
        arg1_start_offset = stack_inst1.start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = skip_cache(instructions, i + 1)
        stack_inst2 = instructions[j]
        if (
            stack_inst1.opcode in opc.operator_set
            and stack_inst2.opcode in opc.operator_set
        ):
            arg2 = get_instruction_arg(stack_inst2, stack_inst2.argrepr)
            k = skip_cache(instructions, j + 1)
            stack_inst3 = instructions[k]
            if stack_inst3.opcode in opc.operator_set:
                start_offset = stack_inst3.start_offset
                arg3 = get_instruction_arg(stack_inst3, stack_inst3.argrepr)
                return fmt_str % (arg2, arg1, arg3), start_offset
            else:
                start_offset = stack_inst2.start_offset
                arg3 = "..."
                return fmt_str % (arg2, arg1, arg3), start_offset

        elif stack_inst2.start_offset is not None:
            start_offset = stack_inst2.start_offset
            arg2 = get_instruction_arg(stack_inst2, stack_inst2.argrepr)
            if arg2 == "":
                arg2 = "..."
            arg3 = "..."
            return fmt_str % (arg2, arg1, arg3), start_offset
        else:
            return fmt_str % ("...", "...", "..."), None
    return "", None


def extended_format_STORE_SUBSCR(opc, instructions: list) -> Tuple[str, Optional[int]]:
    return extended_format_ternary_op(
        opc,
        instructions,
        "%s[%s] = %s",
    )


def extended_format_unary_op(
    opc, instructions, fmt_str: str
) -> Tuple[str, Optional[int]]:
    stack_arg = instructions[1]
    start_offset = instructions[1].start_offset
    if stack_arg.tos_str is not None:
        return fmt_str % stack_arg.tos_str, start_offset
    if stack_arg.opcode in opc.operator_set:
        return fmt_str % stack_arg.argrepr, start_offset
    return "", None


def extended_format_ATTR(opc, instructions) -> Optional[Tuple[str, int]]:
    if instructions[1].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS:
        return (
            "%s.%s" % (instructions[1].argrepr, instructions[0].argrepr),
            instructions[1].offset,
        )


def extended_format_BINARY_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " + ")


def extended_format_BINARY_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " & ")


def extended_format_BINARY_FLOOR_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " // ")


def extended_format_BINARY_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " << ")


def extended_format_BINARY_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " %% ")


def extended_format_BINARY_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " * ")


def extended_format_BINARY_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " | ")


def extended_format_BINARY_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ** ")


def extended_format_BINARY_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " >> ")


def extended_format_BINARY_SUBSCR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(
        opc,
        instructions,
        "%s[%s]",
    )


def extended_format_BINARY_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " - ")


def extended_format_BINARY_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " / ")


def extended_format_BINARY_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ^ ")


def extended_format_BUILD_LIST(opc, instructions) -> Tuple[str, Optional[int]]:
    if instructions[0].argval == 0:
        # Degnerate case
        return "[]", instructions[0].start_offset
    return "", None


def extended_format_BUILD_MAP(opc, instructions) -> Tuple[str, Optional[int]]:
    if instructions[0].argval == 0:
        # Degnerate case
        return "{}", instructions[0].start_offset
    return "", None


def extended_format_BUILD_SET(opc, instructions) -> Tuple[str, Optional[int]]:
    if instructions[0].argval == 0:
        # Degnerate case
        return "set()", instructions[0].start_offset
    return "", None


def extended_format_BUILD_SLICE(opc, instructions) -> Tuple[str, Optional[int]]:
    argc = instructions[0].argval
    assert argc in (2, 3)
    arglist, arg_count, i = get_arglist(instructions, 1, argc)
    if arg_count == 0:
        arglist = ["" if arg == "None" else arg for arg in arglist]
        return ":".join(reversed(arglist)), instructions[i].start_offset

    if instructions[0].argval == 0:
        # Degnerate case
        return "set()", instructions[0].start_offset
    return "", None


def extended_format_BUILD_TUPLE(opc, instructions) -> Tuple[str, Optional[int]]:
    arg_count = instructions[0].argval
    if arg_count == 0:
        # Degnerate case
        return "()", instructions[0].start_offset
    arglist, arg_count, i = get_arglist(instructions, 0, arg_count)
    if arg_count == 0:
        return f'({", ".join(reversed(arglist))})', instructions[i].start_offset
    return "", None


def extended_format_COMPARE_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(
        opc,
        instructions,
        f" {instructions[0].argval} ",
    )


def extended_format_CALL_FUNCTION(opc, instructions):
    """call_function_inst should be a "CALL_FUNCTION" instruction. Look in
    `instructions` to see if we can find a method name.  If not we'll
    return None.

    """
    # From opcode description: arg_count indicates the total number of
    # positional and keyword arguments.

    call_inst = instructions[0]
    arg_count = call_inst.argval
    s = ""

    arglist, arg_count, i = get_arglist(instructions, 0, arg_count)

    if arg_count != 0:
        return "", None

    assert i is not None
    fn_inst = instructions[i + 1]
    if fn_inst.opcode in opc.operator_set:
        start_offset = fn_inst.offset
        if instructions[1].opname == "MAKE_FUNCTION":
            arglist[0] = instructions[2].argval

        fn_name = fn_inst.tos_str if fn_inst.tos_str else fn_inst.argrepr
        if opc.version_tuple >= (3, 6):
            arglist.reverse()
        s = f'{fn_name}({", ".join(arglist)})'
        return s, start_offset
    return "", None


def extended_format_IMPORT_NAME(opc, instructions) -> Tuple[str, Optional[int]]:
    inst = instructions[0]
    start_offset = inst.start_offset
    return f"import_module({inst.argval})", start_offset


def extended_format_INPLACE_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " += ")


def extended_format_INPLACE_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " &= ")


def extended_format_INPLACE_FLOOR_DIVIDE(
    opc, instructions
) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " //= ")


def extended_format_INPLACE_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " <<= ")


def extended_format_INPLACE_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " %%= ")


def extended_format_INPLACE_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " *= ")


def extended_format_INPLACE_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " |= ")


def extended_format_INPLACE_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " **= ")


def extended_format_INPLACE_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " /= ")


def extended_format_INPLACE_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " >>= ")


def extended_format_INPLACE_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " -= ")


def extended_format_INPLACE_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ^= ")


def extended_format_IS_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(
        opc,
        instructions,
        f"%s {format_IS_OP(instructions[0].arg)} %s",
    )


# Can combine with extended_format_MAKE_FUNCTION_36?
def extended_format_MAKE_FUNCTION_10_27(opc, instructions) -> Tuple[str, int]:
    """
    instructions[0] should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.

    This code works for Python versions up to and including 2.7.
    Python docs for MAKE_FUNCTION and MAKE_CLOSURE the was changed in 33, but testing
    shows that the change was really made in Python 3.0 or so.
    """
    # From opcode description: argc indicates the total number of positional
    # and keyword arguments.  Sometimes the function name is in the stack arg
    # positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    code_inst = instructions[2]
    start_offset = code_inst.offset
    if code_inst.opname == "LOAD_CONST" and hasattr(code_inst.argval, "co_name"):
        s += f"make_function({short_code_repr(name_inst.argval)}"
        return s, start_offset
    return s, start_offset


def extended_format_RAISE_VARARGS_older(opc, instructions) -> Tuple[Optional[str], int]:
    raise_inst = instructions[0]
    assert raise_inst.opname == "RAISE_VARARGS"
    argc = raise_inst.argval
    start_offset = raise_inst.start_offset
    if argc == 0:
        return "reraise", start_offset
    elif argc == 1:
        exception_name_inst = instructions[1]
        start_offset = exception_name_inst.start_offset
        exception_name = (
            exception_name_inst.tos_str
            if exception_name_inst.tos_str
            else exception_name_inst.argrepr
        )
        if exception_name is not None:
            return f"raise {exception_name}()", start_offset
    return format_RAISE_VARARGS_older(raise_inst.argval), start_offset


def extended_format_RETURN_VALUE(opc, instructions: list) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "return %s")


def extended_format_UNARY_INVERT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "~(%s)")


def extended_format_UNARY_NEGATIVE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "-(%s)")


def extended_format_UNARY_NOT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "not (%s)")


def format_extended_arg(arg):
    return str(arg * (1 << 16))


def format_CALL_FUNCTION_pos_name_encoded(argc):
    """Encoded positional and named args. Used to
    up to about 3.6 where wordcodes are used and
    a different encoding occurs. Pypy36 though
    sticks to this encoded version though."""
    name_default, pos_args = divmod(argc, 256)
    return "%d positional, %d named" % (pos_args, name_default)


def format_IS_OP(arg: int) -> str:
    return "is" if arg == 0 else "is not"


def format_MAKE_FUNCTION_10_27(argc: int) -> str:
    """
    ``argc`` is the operand  of a  "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction.

    This code works for Python versions up to and including 2.7.
    Python docs for MAKE_FUNCTION and MAKE_CLOSURE the was changed in 33, but testing
    shows that the change was really made in Python 3.0 or so.
    """
    return f"{argc} default parameters"


# Up until 3.7
def format_RAISE_VARARGS_older(argc):
    assert 0 <= argc <= 3
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception"
    elif argc == 2:
        return "exception, parameter"
    elif argc == 3:
        return "exception, parameter, traceback"


def get_arglist(
    instructions: list, i: int, arg_count: int
) -> Tuple[list, int, Optional[int]]:
    """
    For a variable-length instruction like BUILD_TUPLE, or
    a varlabie-name argument list, like CALL_FUNCTION
    accumulate and find the beginning of the list and return:
    * argument list
    * the instruction index of the first instruction

    """
    arglist = []
    i = 0
    inst = None
    while arg_count > 0:
        i += 1
        inst = instructions[i]
        arg_count -= 1
        arg = inst.tos_str if inst.tos_str else inst.argrepr
        if arg is not None:
            arglist.append(arg)
        elif not arg:
            return arglist, arg_count, i
        else:
            arglist.append("???")
        if inst.is_jump_target:
            i += 1
            break
        start_offset = inst.start_offset
        if start_offset is not None:
            j = i
            while j < len(instructions) - 1:
                j += 1
                inst2 = instructions[j]
                if inst2.offset == start_offset:
                    inst = inst2
                    if inst2.start_offset is None or inst2.start_offset == start_offset:
                        i = j
                        break
                    else:
                        start_offset = inst2.start_offset

        pass
    return arglist, arg_count, i


def get_instruction_arg(inst, argval=None) -> str:
    argval = inst.argrepr if argval is None else argval
    return inst.tos_str if inst.tos_str is not None else argval


def resolved_attrs(instructions: list) -> Tuple[str, int]:
    """ """
    # we can probably speed up using the "tos_str" field.
    resolved = []
    start_offset = 0
    for inst in instructions:
        name = inst.argrepr
        if name:
            if name[0] == "'" and name[-1] == "'":
                name = name[1:-1]
        else:
            name = ""
        resolved.append(name)
        if inst.opname != "LOAD_ATTR":
            start_offset = inst.offset
            break
    return ".".join(reversed(resolved)), start_offset


def safe_repr(obj, max_len: int = 20) -> str:
    """
    String repr with length at most ``max_len``
    """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if len(result) > max_len:
        return result[:max_len] + "..."
    return result


def short_code_repr(code) -> str:
    """
    A shortened string representation of a code object
    """
    if hasattr(code, "co_name"):
        return f"<code object {code.co_name}>"
    else:
        return f"<code object {code}>"


def skip_cache(instructions: list, i: int) -> int:
    """Python 3.11+ has CACHE instructions.
    Skip over those starting at index i and return
    the index of the first instruction that is not CACHE
    or return the length of the list if we can't find
    such an instruction.
    """
    n = len(instructions)
    while instructions[i].opname == "CACHE" and i < n:
        i += 1
    return i


# fmt: off
opcode_arg_fmt_base = opcode_arg_fmt34 = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

# The below are roughly Python 3.3 based. Python 3.11 removes some of these.
opcode_extended_fmt_base = {
    "BINARY_ADD":            extended_format_BINARY_ADD,
    "BINARY_AND":            extended_format_BINARY_AND,
    "BINARY_FLOOR_DIVIDE":   extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO":         extended_format_BINARY_MODULO,
    "BINARY_MULTIPLY":       extended_format_BINARY_MULTIPLY,
    "BINARY_RSHIFT":         extended_format_BINARY_RSHIFT,
    "BINARY_SUBSCR":         extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT":       extended_format_BINARY_SUBTRACT,
    "BINARY_TRUE_DIVIDE":    extended_format_BINARY_TRUE_DIVIDE,
    "BINARY_LSHIFT":         extended_format_BINARY_LSHIFT,
    "BINARY_OR":             extended_format_BINARY_OR,
    "BINARY_POWER":          extended_format_BINARY_POWER,
    "BINARY_XOR":            extended_format_BINARY_XOR,
    "BUILD_LIST":            extended_format_BUILD_LIST,
    "BUILD_MAP":             extended_format_BUILD_MAP,
    "BUILD_SET":             extended_format_BUILD_SET,
    "BUILD_SLICE":           extended_format_BUILD_SLICE,
    "BUILD_TUPLE":           extended_format_BUILD_TUPLE,
    "CALL_FUNCTION":         extended_format_CALL_FUNCTION,
    "COMPARE_OP":            extended_format_COMPARE_OP,
    "IMPORT_NAME":           extended_format_IMPORT_NAME,
    "INPLACE_ADD":           extended_format_INPLACE_ADD,
    "INPLACE_AND":           extended_format_INPLACE_AND,
    "INPLACE_FLOOR_DIVIDE":  extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_LSHIFT":        extended_format_INPLACE_LSHIFT,
    "INPLACE_MODULO":        extended_format_INPLACE_MODULO,
    "INPLACE_MULTIPLY":      extended_format_INPLACE_MULTIPLY,
    "INPLACE_OR":            extended_format_INPLACE_OR,
    "INPLACE_POWER":         extended_format_INPLACE_POWER,
    "INPLACE_RSHIFT":        extended_format_INPLACE_RSHIFT,
    "INPLACE_SUBTRACT":      extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE":   extended_format_INPLACE_TRUE_DIVIDE,
    "INPLACE_XOR":           extended_format_INPLACE_XOR,
    "IS_OP":                 extended_format_IS_OP,
    "LOAD_ATTR":             extended_format_ATTR,
    # "LOAD_DEREF":            extended_format_ATTR, # not quite right
    "RAISE_VARARGS":         extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE":          extended_format_RETURN_VALUE,
    "STORE_ATTR":            extended_format_ATTR,
    "STORE_FAST":            extended_format_store_op,
    "STORE_NAME":            extended_format_store_op,
    "STORE_SUBSCR":          extended_format_STORE_SUBSCR,
    "UNARY_INVERT":          extended_format_UNARY_INVERT,
    "UNARY_NEGATIVE":        extended_format_UNARY_NEGATIVE,
    "UNARY_NOT":             extended_format_UNARY_NOT,
}
# fmt: on
