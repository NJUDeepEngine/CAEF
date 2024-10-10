import re

from .state import TMStateGenerator
from .command import TMCommandGenerator

Q0 = 'q0'
Q1 = 'q1'
QC = 'qC'
QH = 'qH'

r""" Turing Machine(TM) utils for LLM.

States:
    - `q0`: Initial state
    - `q1`: Reading digits and adding
    - `qC`: Handling carry
    - `qH`: Halt state

Transition Rules
1. Start at `q0`, set carry `c` to 0 and move to `q1`.
2. In `q1`, read digits from both numbers and carry `c`:
   - If reading `a` from number 1 and `b` from number 2:
     - Write `(a+b+c)%10` and move to `qC`.
   - Else if reading `a` from number 1 or `a` from number 2:
     - Write `(a+c)%10` and move to `qC`.
3. In `qC`, handle carry:
   - Set carry `c` to 1 if `(a+b+c) >= 10`, else set carry `c` to 0.
   - Move to `q1`.
4. Repeat until all digits are processed.
5. If at the end, there’s a carry, write it and move to `qH`.

Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - ADD, q0, [HEAD1] 345[HEAD2] 678 [C] [OUTPUT]
    - ADD, q1,  [HEAD1]345 [HEAD2]678 [C]0 [OUTPUT]
    - ADD, q1,  34[HEAD1]5 67[HEAD2]8 [C]1 91[OUTPUT]
    - ADD, qc,  345[HEAD1] 678[HEAD2] [C]1 914[OUTPUT]
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD: [C] 0, [HEAD1] R, [HEAD2] R, q1
    - CMD: [OUTPUT] 9, [OUTPUT] R, qC
    - CMD: [OUTPUT] 4, [OUTPUT] R, qC
    - CMD: [C] 1, [HEAD1] R, [HEAD2] R, q1

"""

class AdditionTM():
    def __init__(self, op1, op2):
        assert op1 >= 0 and op2 >= 0, "Both operands must be non-negative integers."
        self.state_generator = TMStateGenerator()
        self.cmd_generator = TMCommandGenerator()

        self.op1 = str(op1)[::-1]
        self.op2 = str(op2)[::-1]

        self.current_state = Q0
        self.head1_pos = -1
        self.head2_pos = -1
        self.carry_out = 0
        self.output = ''

        self.operator = 'ADD'

    def get_current_state(self):
        return self.current_state
    
    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.head1_pos >= len(self.op1) and self.head2_pos >= len(self.op2):
                return QH
            else:
                return Q1
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_state(self):
        if self.current_state == Q0:
            return self.state_generator.get_q0_state(self.operator, self.op1, self.op2)
        elif self.current_state == Q1:
            return self.state_generator.get_q1_state(self.operator, self.op1, self.op2, self.head1_pos, self.head2_pos, self.carry_out, self.output)
        elif self.current_state == QH:
            return self.state_generator.get_qH_state(self.operator, self.op1, self.op2, self.carry_out, self.output)
        else:
            raise ValueError(f'Invalid state: {self.current_state}')

    def get_cmd(self):
        if self.current_state == Q0:
            return self.cmd_generator.get_q0_cmd()
        elif self.current_state == Q1:
            a = int(self.op1[self.head1_pos]) if self.head1_pos < len(self.op1) else 0
            b = int(self.op2[self.head2_pos]) if self.head2_pos < len(self.op2) else 0
            s = a + b + int(self.carry_out)
            output = str(s % 10)
            carry_out = str(s // 10)
            h1_r = self.head1_pos < len(self.op1)
            h2_r = self.head2_pos < len(self.op2)
            next_state = self.get_next_state()
            return self.cmd_generator.get_q1_cmd(output, next_state, carry_out, h1_r, h2_r)
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
        self.head1_pos += 1
        self.head2_pos += 1
        self.carry_out = 0
        self.current_state = Q1

    def _one_step_q1(self):
        # compute
        a = int(self.op1[self.head1_pos]) if self.head1_pos < len(self.op1) else 0
        b = int(self.op2[self.head2_pos]) if self.head2_pos < len(self.op2) else 0
        s = a + b + int(self.carry_out)
    
        # update state
        if self.head1_pos >= len(self.op1) and self.head2_pos >= len(self.op2):
            if s > 0: # prevent writing leading 0
                self.output += str(s % 10)
            self.current_state = QH
        else:
            self.output += str(s % 10)
            self.carry_out = str(s // 10)
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

    def self_check(self):
        if self.current_state != QH:
            print('❌ Self check failed. Turing machine is not in halt state.')
            return
        
        output = int(self.output[::-1])
        true_output = int(self.op1[::-1]) + int(self.op2[::-1])
        if output == true_output:
            print('✅ Self check passed.')
        else:
            print(f'Expected: {true_output}, Got: {output}')
            print('❌ Self check failed. Output is incorrect.')


class AdditionTMChecker():
    def __init__(self, input):
        sg = TMStateGenerator()
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'ADD, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            idx = state.find('[C]')
            s = state[:idx] 
            s = s.replace(state_match[0], '').replace(sg.h1_token, '').replace(sg.h2_token, '').replace(sg.separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = AdditionTM(op1, op2)
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
