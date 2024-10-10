import re

from .templates import templates

Q0 = 'q0'
Q1 = 'q1'
Q2 = 'q2'
Q3 = 'q3'
QH = 'qH'

class TMAligner:
    def __init__(self):
        self.legal_tasks = ['add', 'reflection', 'left_mask', 'sub', 'equal', 'greater_than', 'less_than', 'mul', 'div']
        self.legal_operators = ['+', '-', '*', '//', '>', '<', '==']
        self.op_2_task = {
            '+': 'add',
            '-': 'sub', 
            '*': 'mul',
            '//': 'div', 
            '>': 'greater_than', 
            '<': 'less_than',
            '==': 'equal',
        }
        self.task_2_op = {
            'add': '+',
            'sub': '-',
            'mul': '*',
            'div': '//',
            'greater_than': '>',
            'less_than': '<',
            'equal': '==',
        }
        self.op1 = None
        self.op2 = None
        self.operator = None

        self.sep = '|'

        self.token_dict = dict(
            # state
            q0_token = Q0,
            h1_token = '[HEAD1]',
            h2_token = '[HEAD2]',
            c_token = '[C]',
            output_token = '[OUTPUT]',
            count_token = '[COUNT]',
            # command
            q1_token = Q1,
            cmd_token = 'CMD',
            call_token = '[CALL]',
            right_token = 'RIGHT',
            left_token = 'LEFT',
            true_token = 'True',
            false_token = 'False',
        )

    def input_to_tm(self, input):
        ops_pattern = '|'.join(re.escape(op) for op in self.legal_operators)
        pattern = rf'(\d+)\s*({ops_pattern})\s*(\d+)\s*='
        match = re.match(pattern, input)
        if not match:
            raise ValueError(f'Invalid input: {input}')
        try:
            op1, operator, op2 = match.groups()
        except:
            raise ValueError('Invalid input')
        
        operator_name = self.op_2_task[operator]
        template = templates[operator_name]
        q0_state_template = template['q0_state_template']
        q0_cmd_template = template['q0_cmd_template']

        op1 = op1[::-1]
        op2 = op2[::-1]
        sep = self.sep
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)

        token_dict = self.token_dict
        token_dict.update(
            operator = self.op_2_task[operator].upper(),
            op1 = op1,
            op2 = op2,
            count = 0 if operator == '//' else 1,
        )

        def extend_token_dict_input(token_dict, operator, op1, op2):
            if operator == '*':
                token_dict['count'] = ''
                token_dict['output'] = op1
            if operator == '//':
                token_dict['count'] = op2
            return token_dict

        token_dict = extend_token_dict_input(token_dict, operator, op1, op2)

        q0_state = q0_state_template.format(**token_dict)
        q0_cmd = q0_cmd_template.format(**token_dict)

        return q0_state + '\n' + q0_cmd + '\n'

    def tm_to_output(self, output, op1, op2, operator):
        # This function only translate output to text expression,
        # but not check whether the expression is correct.
        output = output.strip()
        idx = output.rfind(' ')
        result = output[idx+1:]
        if self.sep in result:
            result = (result.replace(self.sep, ''))[::-1]
        output_template = '{op1}{operator}{op2}={result}'
        if operator not in self.legal_operators:
            # translate task to operator
            operator = self.task_2_op[operator.lower()]
        return output_template.format(op1=op1, operator=operator, op2=op2, result=result)