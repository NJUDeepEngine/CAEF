import re

from .state import LessThanTMStateGenerator
from .command import LessThanTMCommandGenerator

Q0 = 'q0'
Q1 = 'q1'
QH = 'qH'

class LessThanTM:
    def __init__(self, op1, op2):
        self.state_generator = LessThanTMStateGenerator()
        self.cmd_generator = LessThanTMCommandGenerator()

        self.op1 = str(op1)[::-1]
        self.op2 = str(op2)[::-1]

        self.current_state = Q0
        self.head1_pos = -1
        self.head2_pos = -1
        self.output = 'False'

        self.operator = 'LESS_THAN'

    def get_current_state(self):
        return self.current_state
    
    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.head1_pos >= len(self.op1) or self.head2_pos >= len(self.op2):
                return QH 
            return Q1       
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_state(self):
        if self.current_state == Q0:
            return self.state_generator.get_q0_state(self.op1, self.op2)
        elif self.current_state == Q1:
            return self.state_generator.get_q1_state(self.op1, self.op2, self.head1_pos, self.head2_pos, self.output)
        elif self.current_state == QH:
            return self.state_generator.get_qH_state(self.op1, self.op2, self.head1_pos, self.head2_pos, self.output)
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_cmd(self):
        if self.current_state == Q0:
            return self.cmd_generator.get_q0_cmd()
        elif self.current_state == Q1:
            next_state = self.get_next_state()
            if self.head1_pos == len(self.op1) and self.head2_pos == len(self.op2):
                return self.cmd_generator.get_q1_cmd(next_state)
            if self.head1_pos >= len(self.op1):
                return self.cmd_generator.get_q1_cmd(next_state, 'True')
            if self.head2_pos >= len(self.op2):
                return self.cmd_generator.get_q1_cmd(next_state, 'False')
            output_act = None
            x = int(self.op1[self.head1_pos])
            y = int(self.op2[self.head2_pos])
            if x > y:
                output_act = 'False'
            if x < y:
                output_act= 'True'
            return self.cmd_generator.get_q1_cmd(next_state, output_act)
        elif self.current_state == QH:
            return 'No command to execute. Halt state.'
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def one_step(self):
        if self.current_state == Q0:
            self._one_step_q0()
        elif self.current_state == Q1:
            self._one_step_q1()
        elif self.current_state == QH:
            self._one_step_qH()
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def _one_step_q0(self):
        self.current_state = Q1
        self.head1_pos += 1
        self.head2_pos += 1

    def _one_step_q1(self):
        # len(op1) == len(op2)
        if self.head1_pos == len(self.op1) and self.head2_pos == len(self.op2):
            self.current_state = QH
            return
        # len(op1) < len(op2)
        if self.head1_pos >= len(self.op1):
            self.output = 'True'
            self.current_state = QH
            return
        # len(op1) > len(op2)
        if self.head2_pos >= len(self.op2):
            self.output = 'False'
            self.current_state = QH
            return
        
        x = int(self.op1[self.head1_pos])
        y = int(self.op2[self.head2_pos])
        if x > y:
            self.output = 'False'
        if x < y:
            self.output = 'True'
        
        self.head1_pos += 1
        self.head2_pos += 1
        self.current_state = Q1

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
    
class LessThanTMChecker:
    def __init__(self, input):
        sg = LessThanTMStateGenerator()
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'LESS_THAN, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            s = state.replace(state_match[0], '').replace(sg.h1_token, '').replace(sg.h2_token, '').replace(sg.output_token, '').replace(sg.separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = LessThanTM(op1, op2)
            self.tm.one_step()
        except:
            raise ValueError('Invalid input format.')
        
    def one_step(self):
        if self.tm.get_current_state() == QH:
            return
        self.tm.one_step()

    def check(self, model_output):
        splits = model_output.strip().split('\n')
        try:
            state, cmd = splits[0], splits[1]
            return self.tm.get_state() == state and self.tm.get_cmd() == cmd
        except:
            return False