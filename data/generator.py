import random
from typing import Literal, Optional

from turing_machine.addition.addition_tm import AdditionTM
from turing_machine.reflection.reflection_tm import ReflectionTM
from turing_machine.left_mask.left_mask_tm import LeftMaskTM
from turing_machine.subtraction.sub_tm import SubtractionTM
from turing_machine.equal.equal_tm import EqualTM
from turing_machine.greater_than.greater_than_tm import GreaterThanTM
from turing_machine.less_than.less_than_tm import LessThanTM
from turing_machine.multiplication.mul_tm import MultiplicationTM
from turing_machine.division.div_tm import DivisionTM
from turing_machine.alignment.aligner import TMAligner

def get_9s(n_digits):
    return int('9' * n_digits)

class NDigitGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)

    def generate(self, n_digits):
        assert n_digits > 0
        minimal = 10 ** (n_digits - 1) if n_digits > 1 else 0
        maximal = 10 ** n_digits - 1
        return self.random.randint(minimal, maximal)
    
    def generate_range(self, minimal, maximal):
        return self.random.randint(minimal, maximal)
    
class AddSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate_ops(self, a_n_digits, b_n_digits):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        return op1, op2
    
    def generate(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        add_tm = AdditionTM(op1, op2)
        seq = add_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        input = f'{op1}+{op2}='
        output = str(op1 + op2)
        return input, output

    def generate_with_op(self, op1, op2):
        add_tm = AdditionTM(op1, op2)
        seq = add_tm.get_transition_seq()
        return seq

class ReflectionSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate(self, a_n_digits, b_n_digits):
        op1 = get_9s(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        reflection_tm = ReflectionTM(op1, op2)
        seq = reflection_tm.get_transition_seq()
        return seq

    def generate_leading_zero(self, a_n_digits, b_n_digits):
        assert a_n_digits == b_n_digits, "a_n_digits must be equal to b_n_digits."
        op1 = get_9s(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        length = self.random.randint(1, b_n_digits)
        op2 = str(op2)
        op2 = '9' * length + op2[length:]
        op2 = int(op2)
        reflection_tm = ReflectionTM(op1, op2)
        seq = reflection_tm.get_transition_seq()
        return seq
    
    def generate_with_op(self, op1, op2):
        assert op1 == get_9s(len(str(op1)))
        reflection_tm = ReflectionTM(op1, op2)
        seq = reflection_tm.get_transition_seq()
        return seq

    
class LeftMaskSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate(self, n_digits, leading_zero=False):
        if leading_zero:
            op = self.n_digit_generator.generate(n_digits)
            if str(op)[1] == '0':
                op += self.random.randint(1, 9) * (10 ** (len(str(op)) - 2))
        else:
            num_leading_zero = self.random.randint(1, n_digits-1)
            op = self.random.randint(1, 9) * (10 ** (n_digits - 1))
            if num_leading_zero != n_digits - 1:
                op += self.n_digit_generator.generate(n_digits - num_leading_zero - 1)
                
        left_mask_tm = LeftMaskTM(op)
        seq = left_mask_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op):
        left_mask_tm = LeftMaskTM(op)
        seq = left_mask_tm.get_transition_seq()
        return seq
    
class SubSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)

    def generate(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)        
        sub_tm = SubtractionTM(op1, op2)
        seq = sub_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2):
        assert op1 >= op2, "op1 must be greater than op2."
        sub_tm = SubtractionTM(op1, op2)
        seq = sub_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        input = f'{op1}-{op2}='
        output = str(op1 - op2)
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        if op1 < op2:
            op1, op2 = op2, op1
        return op1, op2
    
class EqualSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'random']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        equal_tm = EqualTM(op1, op2)
        seq = equal_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2):
        equal_tm = EqualTM(op1, op2)
        seq = equal_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'random']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        input = f'{op1}=={op2}='
        output = 'True' if op1 == op2 else 'False'
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'random']]):
        op1 = self.n_digit_generator.generate(a_n_digits)
        if option == 'equal':
            op2 = op1
        else:
            op2 = self.n_digit_generator.generate(b_n_digits)
        return op1, op2

class GreaterThanSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        greater_than_tm = GreaterThanTM(op1, op2)
        seq = greater_than_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2):
        greater_than_tm = GreaterThanTM(op1, op2)
        seq = greater_than_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        input = f'{op1}>{op2}='
        output = str(op1 > op2)
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        if option:
            if option == 'equal':
                op2 = op1
            elif option == 'greater' and op1 <= op2:
                op1, op2 = op2, op1
            elif option == 'less' and op1 >= op2:
                op1, op2 = op2, op1
        return op1, op2
    
class LessThanSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
    
    def generate(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        greater_than_tm = LessThanTM(op1, op2)
        seq = greater_than_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2):
        greater_than_tm = LessThanTM(op1, op2)
        seq = greater_than_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits, option)
        input = f'{op1}<{op2}='
        output = str(op1 < op2)
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits, option: Optional[Literal['equal', 'greater', 'less']]):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        if option:
            if option == 'equal':
                op2 = op1
            elif option == 'greater' and op1 <= op2:
                op1, op2 = op2, op1
            elif option == 'less' and op1 >= op2:
                op1, op2 = op2, op1
        return op1, op2

class MulSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
        self.visited = dict()
        self.cnt = 0
    
    def _get_max_num(self, n_digits):
        minimal = 10 ** (n_digits - 1) if n_digits > 1 else 0
        maximal = 10 ** n_digits - 1
        return maximal - minimal + 1

    def generate(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        mul_tm = MultiplicationTM(op1, op2)
        seq = mul_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2, only_input_output=False):
        mul_tm = MultiplicationTM(op1, op2)
        if only_input_output:
            seq = mul_tm.get_input_output()
        else:
            seq = mul_tm.get_transition_seq()
        return seq

    def generate_with_fixed_op2(self, a_n_digits, op2):
        op1 = self.n_digit_generator.generate(a_n_digits)
        mul_tm = MultiplicationTM(op1, op2)
        seq = mul_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        input = f'{op1}*{op2}='
        output = str(op1 * op2)
        return input, output
    
    def generate_raw_with_fixed_op2(self, a_n_digits, op2=None):
        op1 = self.n_digit_generator.generate(a_n_digits)
        if not op2:
            op2 = self.n_digit_generator.generate_range(1, 15)
        input = f'{op1}*{op2}='
        output = str(op1 * op2)
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        return op1, op2


class DivSeqGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
        self.visited = dict()
    
    def _get_max_num(self, n_digits):
        minimal = 10 ** (n_digits - 1) if n_digits > 1 else 0
        maximal = 10 ** n_digits - 1
        return maximal - minimal + 1

    def generate(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        div_tm = DivisionTM(op1, op2)
        seq = div_tm.get_transition_seq()
        return seq

    def generate_with_op(self, op1, op2, only_input_output=False):
        div_tm = DivisionTM(op1, op2)
        if only_input_output:
            seq = div_tm.get_input_output()
        else:
            seq = div_tm.get_transition_seq()
        return seq

    def generate_with_fixed_result(self, b_n_digits, result):
        op2 = self.n_digit_generator.generate(b_n_digits)
        op1 = result * op2 + self.random.randint(0, op2 - 1)
        div_tm = DivisionTM(op1, op2)
        seq = div_tm.get_transition_seq()
        return seq
    
    def generate_raw(self, a_n_digits, b_n_digits):
        op1, op2 = self.generate_ops(a_n_digits, b_n_digits)
        input = f'{op1}//{op2}='
        output = str(op1 // op2)
        return input, output
    
    def generate_raw_with_fixed_result(self, b_n_digits, result=None):
        if not result:
            result = self.n_digit_generator.generate_range(2, 3)
        op2 = 0
        while op2 == 0:
            op2 = self.n_digit_generator.generate(b_n_digits)
        op1 = result * op2
        if op2 > 1:
            op1 += self.random.randint(0, op2 - 1)
        input = f'{op1}//{op2}='
        output = str(op1 // op2)
        return input, output
    
    def generate_ops(self, a_n_digits, b_n_digits):
        cnt = 0
        while True:
            if cnt >= 50:
                return None
            op1 = self.n_digit_generator.generate(a_n_digits)
            op2 = self.n_digit_generator.generate(b_n_digits)
            if op2 == 0 or op1 // op2 >= 10 ** 6:
                cnt += 1
                continue
            break
        return op1, op2

class AlignerPairGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.n_digit_generator = NDigitGenerator(seed)
        self.template = '{op1}{operator}{op2}='
        self.operator_gen_dict = {
            'add': AddSeqGenerator(seed),
            'reflection': ReflectionSeqGenerator(seed),
            'left_mask': LeftMaskSeqGenerator(seed),
            'sub': SubSeqGenerator(seed),
            'equal': EqualSeqGenerator(seed),
            'greater_than': GreaterThanSeqGenerator(seed),
            'less_than': LessThanSeqGenerator(seed),
            'mul': MulSeqGenerator(seed),
            'div': DivSeqGenerator(seed),
        }

    def _check_input_ops(self, op1, op2, operator):
        if operator == '*':
            if len(str(op1)) > 10 or len(str(op2)) > 5:
                return False
        if operator == '//':
            if op2 == 0:
                return False
            if len(str(op1)) > 10 or len(str(op2)) > 10:
                return False
            if len(str(op1 // op2)) >= 5:
                return False
        return True
    
    def _check_output_ops(self, op1, op2, operator):
        if operator == 'mul':
            if len(str(op1)) > 10 or len(str(op2)) > 5:
                return False
        if operator == 'div':
            if op2 == 0:
                return False
            if len(str(op1)) > 10 or len(str(op2)) > 10:
                return False
            if len(str(op1 // op2)) >= 5:
                return False
        return True

    def _adapt_ops_input(self, op1, op2, operator):
        if operator == '-' and op1 < op2:
            op1, op2 = op2, op1
        if operator == '==':
            rand_val = self.random.randint(0, 1)
            if rand_val == 0:
                op2 = op1
        return op1, op2
    
    def _adapt_ops_output(self, op1, op2, operator):
        if operator == 'sub' and op1 < op2:
            op1, op2 = op2, op1
        if operator == 'equal':
            rand_val = self.random.randint(0, 1)
            if rand_val == 0:
                op2 = op1
        return op1, op2

    def generate_input_pair(self, a_n_digits, b_n_digits, operator=None):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        aligner = TMAligner()
        if not operator:
            operaters = aligner.legal_operators
            operator = self.random.choice(list(operaters))
        op1, op2 = self._adapt_ops_input(op1, op2, operator)        
        if not self._check_input_ops(op1, op2, operator):
            return None
        input = self.template.format(op1=op1, operator=operator, op2=op2)
        output = aligner.input_to_tm(input)
        return input, output
    
    def generate_output_pair(self, a_n_digits, b_n_digits, operator=None):
        op1 = self.n_digit_generator.generate(a_n_digits)
        op2 = self.n_digit_generator.generate(b_n_digits)
        aligner = TMAligner()
        if not operator:
            operaters = aligner.task_2_op.keys()
            operator = self.random.choice(list(operaters))
        generator = self.operator_gen_dict[operator]
        op1, op2 = self._adapt_ops_output(op1, op2, operator)
        if not self._check_output_ops(op1, op2, operator):
            return None
        seq = generator.generate_with_op(op1, op2)
        splits = seq[-1][1].split('\n')
        if len(splits) == 2:
            state, cmd = splits[0], splits[1]
        else:
            state, cmd = seq[-1][0], seq[-1][1]  
            
        output = aligner.tm_to_output(state, op1, op2, operator)
        return state + '\n' + cmd, output