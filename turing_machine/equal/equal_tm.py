import re

from .state import EqualTMStateGenerator
from .command import EqualTMCommandGenerator

Q0 = 'q0'
Q1 = 'q1'
QH = 'qH'

class EqualTM:
    def __init__(self, op1, op2):
        self.state_generator = EqualTMStateGenerator()
        self.cmd_generator = EqualTMCommandGenerator()

        self.op1 = str(op1)[::-1]
        self.op2 = str(op2)[::-1]

        self.current_state = Q0
        self.head1_pos = -1
        self.head2_pos = -1
        self.output = 'True'

        self.operator = 'EQUAL'

    def get_current_state(self):
        return self.current_state
    
    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.head1_pos == len(self.op1) and self.head2_pos == len(self.op2):
                return QH
            if self.head1_pos >= len(self.op1) or self.head2_pos >= len(self.op2):
                return QH
            x = self.op1[self.head1_pos]
            y = self.op2[self.head2_pos]
            if x != y:
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
                return self.cmd_generator.get_q1_cmd('True', next_state)
            if self.head1_pos >= len(self.op1) or self.head2_pos >= len(self.op2):
                return self.cmd_generator.get_q1_cmd('False', next_state)
            if next_state == Q1:
                return self.cmd_generator.get_q1_cmd('True', next_state)
            elif next_state == QH:
                return self.cmd_generator.get_q1_cmd('False', next_state)
            else:
                raise ValueError(f'Invalid next state: {next_state}')
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
        # len(op1) != len(op2)
        if self.head1_pos >= len(self.op1) or self.head2_pos >= len(self.op2):
            self.output = 'False'
            self.current_state = QH
            return
        # op1 != op2
        x = self.op1[self.head1_pos]
        y = self.op2[self.head2_pos]
        if x != y:
            self.output = 'False'
            self.current_state = QH
            return
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
    
class EqualTMChecker:
    def __init__(self, input):
        sg = EqualTMStateGenerator()
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'EQUAL, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            s = state.replace(state_match[0], '').replace(sg.h1_token, '').replace(sg.h2_token, '').replace(sg.output_token, '').replace(sg.separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = EqualTM(op1, op2)
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