import re
import pdb
import math

def format_comment(depth, inps, rets=None, tab='    '):
    """
    inputs:
        inps: Dict of inputs and their types
        rets: List of return arguments and their types. Can be None.

    returns:
        String describing the type
    """
    # TODO: receive tab as a required parameter, which is automatically acquired
    # previous level functions.
    indent = tab * depth
    text_base = """{}\"\"\"[Please put one line of explanation here.]
    [Elaborate here.]
    Inputs:
    {}
    Returns:
    {}
    {}\"\"\"\n"""

    parameters_base = "{}: {} of [put explanation here]"

    betw = '\n' + tab
    inp_string = betw.join(
        [indent + parameters_base.format(x, inps[x]) for x in inps])
    if rets is not None:
        ret_string = betw.join(
            [indent + parameters_base.format(x, rets[x]) for x in rets])
    else:
        ret_string = '[Parser could not get return data information.]'
    return text_base.format(indent, inp_string, ret_string, indent)


def get_line_depth(line):
    line = line.replace('\n', '')
    leading_whitespace = re.match(r'^([\t ]*)', line)[0]
    if leading_whitespace.startswith('\t'):
        depth = len(leading_whitespace)
    elif leading_whitespace.startswith(' '):
        depth = math.ceil(len(leading_whitespace) / 4)
    elif not leading_whitespace:
        depth = 0

    return depth



def find_functions(file_path):
    # TODO: support nested functions
    func_start = re.compile(r'^[\t ]*def [A-Za-z0-9_]*\(.*')
    sig_end = re.compile(r'.*:\n$')
    functions = []
    depth = 0
    with open(file_path, 'r') as code:
        data = code.readlines()
        func = []
        for idx, line in enumerate(data):
            if not line.strip():
                continue

            if len(func) == 2:
                if get_line_depth(line) < depth:
                    func.append(idx - 1)
                elif idx == len(data) - 1:
                    func.append(idx)
                else:
                    continue
                func.append(depth)
                functions.append(func)
                func = []
            if func_start.match(line):
                if depth and get_line_depth(line) >= depth:
                    continue
                func.append(idx)
                depth = get_line_depth(line) + 1

            if sig_end.match(line) and len(func) == 1:
                func.append(idx)
                continue

    return functions, data


def parser(funtions, data):
    ret_stmt = re.compile(r'^[\t ]*return .*')
    inp_pattern = re.compile(r'\(\s*[A-Za-z0-9_,\s]+\)')

    comments = []
    for func in funtions:
        ret_line = None
        signature = ''.join(data[func[0]:func[1] + 1])
        inps = inp_pattern.search(signature)[0]
        inps = re.sub(r'\s', '', inps)
        inps = inps[1:-1]
        inps = inps.split(',')
        inps = {x: '[Type]' for x in inps}

        whole_func = data[func[0]:func[2] + 1]
        for line in reversed(whole_func):
            if not line.strip():
                continue
            if ret_stmt.match(line):
                ret_line = line
            else:
                break

        ret_line = ret_line.replace('return', '').strip()
        rets = None
        if ',' not in ret_line:
            rets = {ret_line: '[Type]'}

        comments.append(format_comment(func[-1], inps, rets=rets))

    return comments


def writer(functions, comments, data, file_path):
    for idx, func in enumerate(reversed(functions)):
        data.insert(func[1] + 1, comments[len(comments) - 1 - idx])

    with open(file_path, 'w') as f:
        f.writelines(data)


if __name__ == "__main__":
    f, d = find_functions('test.py')
    comm = parser(f, d)
    writer(f, comm, d, 'test_with_comment.py')