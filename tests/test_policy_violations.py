
import os
from glob import glob

import pytest

src_file_list = [y for x in os.walk('src' + os.sep + 'fprime_extras')
                 for y in glob(os.path.join(x[0], '*.py'))]

policy_dict = {
    # 'Date and Time': ['datetime', 'timedelta', 'tz', '.srtptime('],
    ' No Print Statements: Use Logging Instead': [' print('],
    ' Do not use __file__ for logger name': ['getLogger(__file']
}


def matrix(list_a, list_b):
    '''
    Output a new list that has every possible combination of items from
    each list.
    '''
    ret = []
    for i in list_a:
        for j in list_b:
            ret.append((i, j))
    return ret


policy_list = []
for k in policy_dict.keys():
    for i in policy_dict[k]:
        policy_list.append((k, i))

print(matrix(src_file_list, policy_list))

policies = [(m[0], m[1][1], m[1][0])
            for m in matrix(src_file_list, policy_list)]


@pytest.mark.parametrize("filename, keyword, policy", policies)
def test_policy_violations(filename, keyword, policy):
    '''
    Simple test for finding basic usage policy violations.  If the
    keyword is found in the file, the test fails.  The policy is
    printed, and the line number and line containing each instance
    is listed.

    Args:
        filename (string): path and name of file to search
        keyword (string): forbidden string to find in file
        policy (string): name of policy to print, if found
    '''
    line_no = 0
    violations = []
    with open(filename) as f:
        for line in f:
            line_no += 1
            if keyword in line:
                txt = 'Found "{}" in file {} on line {} : {}'.format(
                    keyword, filename, line_no, line)
                violations.append(txt)
    if len(violations) > 0:
        violations.insert(0, 'Violation of {} policy:\n'.format(policy))
        assert False, ''.join(violations)
