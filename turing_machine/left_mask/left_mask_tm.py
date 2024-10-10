import re

from .state import TMStateGenerator
from .command import TMCommandGenerator

Q0 = 'q0'
Q1 = 'q1'
Q2 = 'q2'
QH = 'qH'

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - LEFT_MASK, q0, [HEAD] 45321 [OUTPUT]
    - LEFT_MASK, q1,  [HEAD]45321 [OUTPUT]
    - LEFT_MASK, q1,  4[HEAD]5321 4[OUTPUT]
    - LEFT_MASK, q1,  45321[HEAD] 45321[OUTPUT]
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD] R, q1
    - CMD [HEAD] R, [OUTPUT] 4, [OUTPUT] RIGHT, q1
    - CMD [HEAD] R, [OUTPUT] 5, [OUTPUT] RIGHT, q1
    - CMD [OUTPUT] LEFT, [OUTPUT] 0, qH
"""

class LeftMaskTM:
    def __init__(self, op):
        self.state_generator = TMStateGenerator()
        self.cmd_generator = TMCommandGenerator()

        self.op = str(op)[::-1]

        self.current_state = Q0
        self.head_pos = -1
        self.output_pos = -1
        self.output = ''

        self.operator = 'LEFT_MASK'

    def get_current_state(self):
        return self.current_state

    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.head_pos >= len(self.op):
                return Q2
            else:
                return Q1
        elif self.current_state == Q2:
            if self.output_pos < 0 or int(self.output[self.output_pos]) != 0:
                return QH
            else:
                return Q2
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_state(self):
        if self.current_state == Q0:
            return self.state_generator.get_q0_state(self.op)
        elif self.current_state == Q1:
            return self.state_generator.get_q1_state(self.op, self.head_pos, self.output)
        elif self.current_state == Q2:
            return self.state_generator.get_q2_state(self.op, self.output)
        elif self.current_state == QH:
            return self.state_generator.get_qH_state(self.op, self.output)
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_cmd(self):
        if self.current_state == Q0:
            return self.cmd_generator.get_q0_cmd()
        elif self.current_state == Q1:
            x = self.op[self.head_pos] if self.head_pos < len(self.op) else 0
            return self.cmd_generator.get_q1_cmd(x, self.get_next_state())
        elif self.current_state == Q2:
            return self.cmd_generator.get_q2_cmd(self.get_next_state())
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
        self.head_pos += 1
        self.current_state = Q1

    def _one_step_q1(self):
        if self.head_pos >= len(self.op):
            self.output = self.output[:-1]
            self.output_pos -= 1
            self.current_state = Q2
            return
        x = self.op[self.head_pos]
        self.output += x
        self.head_pos += 1
        self.output_pos += 1
        self.current_state = Q1

    def _one_step_q2(self):
        if self.output_pos < 0:
            self.current_state = QH
            return
        x = int(self.output[self.output_pos])
        if x != 0:
            self.current_state = QH
        else:
            self.output = self.output[:-1]
            self.output_pos -= 1
            self.current_state = Q2

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
    
class LeftMaskTMChecker():
    def __init__(self, input):
        sg = TMStateGenerator()
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'LEFT_MASK, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            s = state.replace(state_match[0], '').replace(sg.h_token, '').replace(sg.output_token, '').replace(sg.separator, '').strip()
            op = int(s[::-1])
            self.tm = LeftMaskTM(op)
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