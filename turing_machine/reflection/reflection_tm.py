import re

from .state import ReflectionTMStateGenerator
from .command import ReflectionTMCommandGenerator

Q0 = 'q0'
Q1 = 'q1'
Q2 = 'q2'
QH = 'qH'

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - REFLECTION, q0, [HEAD1] 9999[HEAD2] 1234 [OUTPUT]
    - REFLECTION, q1,  [HEAD1]9999 [HEAD2]1234 [OUTPUT]
    - REFLECTION, q1,  9[HEAD1]999 1[HEAD2]234 8[OUTPUT]
    - REFLECTION, q1,  9999[HEAD1] 1234[HEAD2] 8765[OUTPUT]
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] 8, [OUTPUT] RIGHT, q1
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] 7, [OUTPUT] RIGHT, q1
    - CMD [OUTPUT], qH
"""

class ReflectionTM:
    def __init__(self, op1, op2):
        assert op1 >= 0 and op2 >= 0, "Both operands must be non-negative integers."
        assert op1 >= op2, f"The first operand must be greater than or equal to the second operand. But got: op1 = {op1}, op2 = {op2}"

        self.state_generator = ReflectionTMStateGenerator()
        self.cmd_generator = ReflectionTMCommandGenerator()

        self.op1 = str(op1)
        for ch in self.op1:
            assert ch == '9', "The digits in the first operand must be 9."
        self.op2 = str(op2)[::-1]

        self.current_state = Q0
        self.head1_pos = -1
        self.head2_pos = -1
        self.output_pos = -1
        self.output = ''

        self.operator = 'REFLECTION'

    def get_current_state(self):
        return self.current_state

    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.head1_pos >= len(self.op1) and self.head2_pos >= len(self.op2):
                return Q2
            else:
                return Q1
        elif self.current_state == Q2:
            if self.output_pos < 0:
                return QH
            if self.output[self.output_pos] == '0':
                return Q2
            else:
                return QH
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def get_state(self):
        if self.current_state == Q0:
            return self.state_generator.get_q0_state(self.op1, self.op2)
        elif self.current_state == Q1:
            return self.state_generator.get_q1_state(self.op1, self.op2, self.head1_pos, self.head2_pos, self.output)
        elif self.current_state == Q2:
            output = self.output[:self.output_pos + 1]
            return self.state_generator.get_q2_state(self.op1, self.op2, output)
        elif self.current_state == QH:
            output = self.output[:self.output_pos + 1]
            if len(output) == 0:
                output = '0'
            return self.state_generator.get_qH_state(self.op1, self.op2, output)
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def get_cmd(self):
        if self.current_state == Q0:
            return self.cmd_generator.get_q0_cmd()
        elif self.current_state == Q1:
            x = int(self.op2[self.head2_pos]) if self.head2_pos < len(self.op2) else 0
            y = 9 - x
            next_state = self.get_next_state()
            h1_r = self.head1_pos < len(self.op1)
            h2_r = self.head2_pos < len(self.op2)
            return self.cmd_generator.get_q1_cmd(y, next_state, h1_r, h2_r)
        elif self.current_state == Q2:
            next_state = self.get_next_state()
            return self.cmd_generator.get_q2_cmd(next_state)
        elif self.current_state == QH:
            return 'No command to execute. Halt state.'
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def one_step(self):
        if self.current_state == Q0:
            self._one_step_q0()
        elif self.current_state == Q1:
            self._one_step_q1()
        elif self.current_state == Q2:
            self._one_step_q2()
        elif self.current_state == QH:
            self._one_step_qH()
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
    
    def _one_step_q0(self):
        self.head1_pos += 1
        self.head2_pos += 1
        self.current_state = Q1

    def _one_step_q1(self):
        if self.head1_pos >= len(self.op1) and self.head2_pos >= len(self.op2):
            self.current_state = Q2
            self.output_pos = len(self.output) - 1
            return
        # compute
        x = self.op2[self.head2_pos] if self.head2_pos < len(self.op2) else '0'
        y = str(9 - int(x))
        # update
        self.output += y
        self.head1_pos += 1
        self.head2_pos += 1
        self.current_state = Q1

    def _one_step_q2(self):
        if self.output_pos < 0:
            self.current_state = QH
            return
        if self.output[self.output_pos] == '0':
            self.output_pos -= 1
            return
        self.current_state = QH

    def _one_step_qH(self):
        self.current_state = QH
        print('Halt')

    def many_step(self):
        pass

    def get_transition_seq(self):
        seq = []
        while self.current_state != QH:
            seq.append((self.get_state(), self.get_cmd()))
            self.one_step()
        seq.append((self.get_state(), self.get_cmd()))
        return seq

class ReflectionTMChecker:
    def __init__(self, input):
        sg = ReflectionTMStateGenerator()
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'REFLECTION, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            s = state.replace(state_match[0], '').replace(sg.h1_token, '').replace(sg.h2_token, '').replace(sg.output_token, '').replace(sg.separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = ReflectionTM(op1, op2)
            self.tm.one_step()
        except:
            raise ValueError('Invalid input format.')

    def one_step(self):
        if self.tm.get_current_state() == QH:
            return
        self.tm.one_step()

    def check(self, model_output):
        splits = model_output.strip().split('\n')
        state, cmd = splits[0], splits[1]
        return self.tm.get_state() == state and self.tm.get_cmd() == cmd