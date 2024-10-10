import re

from .call_state import TMCallStateGenerator
from .call_command import TMCallCommandGenerator
from .input import TMInputGenerator

Q0 = 'q0'
Q1 = 'q1'
Q2 = 'q2'
Q3 = 'q3'
Q4 = 'q4'
QH = 'qH'

r""" Turing Machine(TM) utils for LLM subtraction.

States:
- q0: Initial state.
- q1: Reflection finished.
- q2: Addition 1 finished.
- q3: Addition 2 finished.
- q4: Left mask finished.
- qH: Halt state.

Operations:
47819 - 12345 = 35474
- step 1: reflection, 99999 - 12345 = 87654
- step 2: addtion, 47819 + 87654 = 135473
- step 3: addtion, 135473 + 1 = 135474
- step 4: left mask, 35474

Example:
---
iteration 1:
- input
SUB, q0, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1
CMD q1
- output
SUB, q1, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1                     # state
CMD [CALL] REFLECTION, q2                                        # command
REFLECTION, q0, [HEAD1] |9|9|9|9|9[HEAD2] |5|4|3|2|1 [OUTPUT]    # state for call
CMD [HEAD1] RIGHT, [HEAD2] RIGHT, q1                             # command for call

---
iteration 2:
- input
SUB, q1, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1                     # copied from last output
[CALL] REFLECTION, q2                                            # copied from last output
REFLECTION, qH,  |9|9|9|9|9[HEAD1] |5|4|3|2|1[HEAD2] |4|5|6|7|8  # final state after call
No command to execute. Halt state.                               # message after call
- output
SUB, q2, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1                     # state
CMD [CALL] ADD, q3                                               # command
ADD, q0, [HEAD1] |9|1|8|7|4[HEAD2] |4|5|6|7|8 [C] [OUTPUT]       # state for call
CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1                     # command for call

---
iteration 3:
- input
SUB, q2, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 
[CALL] ADD, q3
ADD, qH,  |9|1|8|7|4[HEAD1] |4|5|6|7|8[HEAD2] [C]0 |3|7|4|5|3|1
No command to execute. Halt state.
- output
SUB, q3, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 
[CALL] ADD, q4
ADD, q0, [HEAD1] |3|7|4|5|3|1[HEAD2] |1 [C] [OUTPUT]
CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1

---
iteration 4:
- input
SUB, q3, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 
[CALL] ADD, q4
ADD, qH,  |3|7|4|5|3|1[HEAD1] |1[HEAD2] [C]0 |4|7|4|5|3|1
No command to execute. Halt state.
- output
SUB, q4, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 
[CALL] LEFT_MASK, qH
LEFT_MASK, q0, [HEAD] |4|7|4|5|3|1 [OUTPUT]
CMD [HEAD] RIGHT, q1

---
iteration 5:
- input
SUB, q4, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 
[CALL] LEFT_MASK, qH
LEFT_MASK, qH,  |4|7|4|5|3|1[HEAD] |4|7|4|5|3
No command to execute. Halt state.
- output
SUB, qH, [HEAD1]|9|1|8|7|4 [HEAD2]|5|4|3|2|1 |4|7|4|5|3
No command to execute. Halt state.
"""

class SubtractionTM:
    def __init__(self, op1, op2):
        self.call_state_generator = TMCallStateGenerator()
        self.call_cmd_generator = TMCallCommandGenerator()
        self.input_generator = TMInputGenerator()

        self.op1 = op1
        self.op2 = op2

        # original operands, before reverse
        self.q1_op1 = '9' * len(str(self.op1))
        self.q1_op2 = str(self.op2)
        self.q1_output = str(int(self.q1_op1) - self.op2)

        self.q2_op1 = str(self.op1)
        self.q2_op2 = str(int(self.q1_op1) - self.op2)
        self.q2_output = str(int(self.q2_op1) + int(self.q2_op2))

        self.q3_op = self.q2_output
        self.q3_output = str(int(self.q3_op) + 1)

        self.q4_op = self.q3_output
        self.q4_output = self.q4_op[1:]

        self.current_state = Q0
        self.operator = 'SUB'
        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.cmd_token = 'CMD'
        self.call_token = '[CALL]'
        self.reflection_token = 'REFLECTION'
        self.add_token = 'ADD'
        self.left_mask_token = 'LEFT_MASK'
        self.output_token = '[OUTPUT]'
        self.separator = '|'


    def get_cuurent_state(self):
        return self.current_state
    
    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            return Q2
        elif self.current_state == Q2:
            return Q3
        elif self.current_state == Q3:
            return Q4
        elif self.current_state == Q4:
            return QH
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
    
    def get_state(self):
        state_template = '{operator}, {state}, {h1_token}{op1} {h2_token}{op2} {output}'
        rev = lambda x: str(x)[::-1]

        op1 = rev(self.op1)
        op2 = rev(self.op2)
        output = rev(self.op1 - self.op2) if self.current_state == QH else ''
        sep = self.separator
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)
            output = sep + sep.join(output) if len(output) > 0 else ''

        return state_template.format(operator=self.operator,
                                        state=self.current_state,
                                        h1_token=self.h1_token,
                                        h2_token=self.h2_token,
                                        op1=op1,
                                        op2=op2,
                                        output=output,
                                        )
    
    def get_cmd(self):
        if self.current_state == Q0:
            return f'{self.cmd_token} q1'
        if self.current_state == QH:
            return 'No command to execute. Halt state.'
        
        cmd_template = '{cmd_token} {call_token} {call_cmd}, {next_state}'
        call_cmd_dict = {
            Q1: self.reflection_token,
            Q2: self.add_token,
            Q3: self.add_token,
            Q4: self.left_mask_token,
        }
        return cmd_template.format(cmd_token=self.cmd_token,
                                    call_token=self.call_token,
                                    call_cmd=call_cmd_dict[self.current_state],
                                    next_state=self.get_next_state())
    
    def get_call_state(self, choice):
        assert choice in ['input', 'output'], 'Invalid choice, should be either "input" or "output".'
        if choice == 'input':
            return self._get_call_state_input()
        elif choice == 'output':
            return self._get_call_state_output()
        
    def _get_call_state_output(self):
        rev = lambda x: str(x)[::-1]
        if self.current_state == Q1:
            return self.call_state_generator.get_q1_output(rev(self.q1_op1), rev(self.q1_op2))
        elif self.current_state == Q2:
            return self.call_state_generator.get_q2_output(rev(self.q2_op1), rev(self.q2_op2))
        elif self.current_state == Q3:
            return self.call_state_generator.get_q3_output(rev(self.q3_op))
        elif self.current_state == Q4:
            return self.call_state_generator.get_q4_output(rev(self.q4_op))
        elif self.current_state == Q0 or self.current_state == QH:
            return ''
        else:
            raise ValueError(f'Invalid state: {self.current_state}')


    def _get_call_state_input(self):
        rev = lambda x: str(x)[::-1]
        if self.current_state == Q1:
            # reflection result
            op1 = rev(self.q1_op1)
            op2 = rev(self.q1_op2)
            output = rev(self.q1_output)
            result = self.input_generator.get_q1_input(op1, op2, output)
        elif self.current_state == Q2:
            # add result
            op1 = rev(self.q2_op1)
            op2 = rev(self.q2_op2)
            carry_out = 0
            output = rev(self.q2_output)
            result = self.input_generator.get_q2_input(op1, op2, carry_out, output)
        elif self.current_state == Q3:
            # add result
            op1 = rev(self.q3_op)
            op2 = '1'
            carry_out = 0
            output = rev(self.q3_output)
            result = self.input_generator.get_q3_input(op1, op2, carry_out, output)
        elif self.current_state == Q4:
            # left mask result
            op = rev(self.q4_op)
            output = rev(self.q4_output)
            result = self.input_generator.get_q4_input(op, output)
        elif self.current_state == Q0 or self.current_state == QH:
            result = ''
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
        return result
        
    def get_call_cmd(self, choice):
        assert choice in ['input', 'output'], 'Invalid choice, should be either "input" or "output".'
        if choice == 'output':
            if self.current_state == Q1:
                return self.call_cmd_generator.get_q1_cmd()
            elif self.current_state == Q2:
                return self.call_cmd_generator.get_q2_cmd()
            elif self.current_state == Q3:
                return self.call_cmd_generator.get_q3_cmd()
            elif self.current_state == Q4:
                return self.call_cmd_generator.get_q4_cmd()
            elif self.current_state == Q0 or self.current_state == QH:
                return ''
            else:
                raise ValueError(f'Invalid state: {self.current_state}')
        elif self.current_state == Q0:
            return ''
        else:
            return 'No command to execute. Halt state.'

    def one_step(self):
        if self.current_state == Q0:
            self.current_state = Q1
        elif self.current_state == Q1:
            self.current_state = Q2
        elif self.current_state == Q2:
            self.current_state = Q3
        elif self.current_state == Q3:
            self.current_state = Q4
        elif self.current_state == Q4:
            self.current_state = QH
        elif self.current_state == QH:
            self.current_state = QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def get_transition_seq(self):
        seq = []
        entry_template = '{}\n{}\n{}\n{}\n'
        while self.current_state != QH:
            input_state = self.get_state()
            input_cmd = self.get_cmd()
            input_call_state = self.get_call_state('input')
            input_call_cmd = self.get_call_cmd('input')

            self.one_step()

            output_state = self.get_state()
            output_cmd = self.get_cmd()
            output_call_state = self.get_call_state('output')
            output_call_cmd = self.get_call_cmd('output')

            input = entry_template.format(input_state, input_cmd, input_call_state, input_call_cmd).strip() + '\n'
            output = entry_template.format(output_state, output_cmd, output_call_state, output_call_cmd).strip()
            seq.append((input, output))
        return seq
    
class SubtractionTMChecker:
    def __init__(self, input):
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'SUB, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            h1_token = '[HEAD1]'
            h2_token = '[HEAD2]'
            output_token = '[OUTPUT]'
            separator = '|'
            s = state.replace(state_match[0], '').replace(h1_token, '').replace(h2_token, '').replace(output_token, '').replace(separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = SubtractionTM(op1, op2)
        except:
            raise ValueError('Invalid input format.')
        self.tm = SubtractionTM(op1, op2)
        self.step = 0
        self.transition_seq = self.tm.get_transition_seq()

    def one_step(self):
        if self.step > len(self.transition_seq):
            return
        self.step += 1

    def check(self, model_output):
        model_output = model_output.strip()
        if self.step >= len(self.transition_seq):
            return False
        ground_truth = self.transition_seq[self.step][1].strip()
        return model_output == ground_truth