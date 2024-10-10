import re

from .call_state import TMCallStateGenerator
from .call_command import TMCallCommandGenerator
from .input import TMInputGenerator

Q0 = 'q0'
Q1 = 'q1'
Q2 = 'q2'
Q3 = 'q3'
QH = 'qH'

r""" Turing Machine(TM) utils for LLM division.

For 'a // b = c', algorithm:
c = 0, cnt = b
while not cnt > a:
    c += 1
    cnt += b
output: c
    
States:
- q0: Initial state.
- q1: 'while' loop: compare cnt and a, decide next state.
- q2: 'while' loop: step1, c += 1.
- q3: 'while' loop: step2, cnt += b.
- q5: Halt state.

Example:
4513 // 1504 = 3
---
iteration 1:
- input
DIV, q0, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT] [OUTPUT]              # state
CMD [COUNT]|4|0|5|1, [OUTPUT] 0, q1                                    # command
- output
DIV, q1, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT], [OUTPUT]|0   # state
CMD [CALL] GREATER_THAN, q2                                            # command
GREATER_THAN, q0, [HEAD1] |4|0|5|1[HEAD2] |3|1|5|4 [OUTPUT]            # state for call                
CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] False, q1                   # command for call

---
iteration 2:
- input
DIV, q1, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|4|0|5|1, [OUTPUT]|0   # copied from last output
CMD [CALL] GREATER_THAN, q2                                            # copied from last output
GREATER_THAN, qH,  |4|0|5|1[HEAD1] |3|1|5|4[HEAD2] False               # final state after call
No command to execute. Halt state.                                     # message after call                            
- output
DIV, q2, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|4|0|5|1, [OUTPUT]|0   # state
CMD [CALL] ADD, q3                                                     # command
ADD, q0, [HEAD1] |0[HEAD2] |1 [C] [OUTPUT]                             # state for call
CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1                           # command for call

---
iteration 3:
- input
DIV, q2, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|4|0|5|1, [OUTPUT]|0   # copied from last output
CMD [CALL] ADD, q3                                                     # copied from last output
ADD, qH,  |0[HEAD1] |1[HEAD2] [C]0 |1                                  # final state after call
No command to execute. Halt state.                                     # message after call
- output
DIV, q3, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|4|0|5|1, [OUTPUT]|1   # state
CMD [CALL] ADD, q1                                                     # command
ADD, q0, [HEAD1] |4|0|5|1[HEAD2] |4|0|5|1 [C] [OUTPUT]                 # state for call
CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1                           # command for call

---
iteration 4:
- input
DIV, q3, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|4|0|5|1, [OUTPUT]|1   # copied from last output
CMD [CALL] ADD, q1                                                     # copied from last output
ADD, qH,  |4|0|5|1[HEAD1] |4|0|5|1[HEAD2] [C]0 |8|0|0|3                # final state after call
No command to execute. Halt state.                                     # message after call
- output
DIV, q1, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|8|0|0|3, [OUTPUT]|1   # state
CMD [CALL] GREATER_THAN, q2                                            # command
LESS_THAN, q0, [HEAD1] |8|0|0|3[HEAD2] |3|1|5|4 [OUTPUT]               # state for call                
CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] False, q1                   # command for call

...
---
iteration 11:
- input
DIV, q1, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|6|1|0|6, [OUTPUT]|3  # state
CMD [CALL] GREATER_THAN, q2                                           # command
GREATER_THAN, qH,  |6|1|0|6[HEAD1] |3|1|5|4[HEAD2] True               # final state after call
No command to execute. Halt state.                                    # message after call 
- output
DIV, q4, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|6|1|0|6 [OUTPUT]|3   # state
CALL [OUTPUT], qH                                                     # command, change state to qH

---
iteration 12:
- input
DIV, q4, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|6|1|0|6 [OUTPUT]|3   # state
CMD [OUTPUT], qH                                                      # command
- output
MUL, qH, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|6|1|0|6 |3           # final state
No command to execute. Halt state.                                    # end message
"""

class DivisionTM:
    def __init__(self, op1, op2):
        self.call_state_generator = TMCallStateGenerator()
        self.call_cmd_generator = TMCallCommandGenerator()
        self.input_generator = TMInputGenerator()

        self.op1 = str(op1)[::-1]
        self.op2 = str(op2)[::-1]
        self.cnt = -1
        self.output = ''

        self.current_state = Q0
        self.operator = 'DIV'
        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.cmd_token = 'CMD'
        self.call_token = '[CALL]'
        self.output_token = '[OUTPUT]'
        self.count_token = '[COUNT]'
        self.add_token = 'ADD'
        self.greater_than_token = 'GREATER_THAN'
        self.separator = '|'

    def get_cuurent_state(self):
        return self.current_state
    
    def get_next_state(self):
        if self.current_state == Q0:
            return Q1
        elif self.current_state == Q1:
            if self.cnt > int(self.op1[::-1]):
                return QH
            return Q2
        elif self.current_state == Q2:
            return Q3
        elif self.current_state == Q3:
            return Q1
        elif self.current_state == QH:
            return QH
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def get_state(self):
        state_template = '{operator}, {state}, {h1_token}{op1} {h2_token}{op2} {count_token}{count} {output_token}{output}'
        op1 = self.op1
        op2 = self.op2
        count = str(self.cnt)[::-1] if self.cnt >= 0 else ''
        output = self.output

        sep = self.separator
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)
            count = sep + sep.join(count) if len(count) > 0 else ''
            output = sep + sep.join(output) if len(output) > 0 else ''

        output_token = self.output_token if self.current_state != QH else ''
        return state_template.format(
            operator=self.operator,
            state=self.current_state,
            h1_token=self.h1_token,
            h2_token=self.h2_token,
            count_token=self.count_token,
            output_token=output_token,
            op1=op1,
            op2=op2,
            count=count,
            output=output
        )
    
    def get_cmd(self):
        if self.current_state == Q0:
            return self._get_q0_cmd()
        elif self.current_state == Q1:
            return self._get_q1_cmd()
        elif self.current_state == Q2:
            return self._get_q2_cmd()
        elif self.current_state == Q3:
            return self._get_q3_cmd()
        elif self.current_state == QH:
            return 'No command to execute. Halt state.'
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
    
    def _get_q0_cmd(self):
        q0_cmd_template = '{cmd_token} {count_token}{count}, {output_token} 0, {next_state}'
        count = self.op2
        sep = self.separator
        if len(sep) > 0:
            count = sep + sep.join(count) if len(count) > 0 else ''
        return q0_cmd_template.format(
            cmd_token=self.cmd_token,
            count_token=self.count_token,
            count=count,
            output_token=self.output_token,
            next_state=Q1
        )

    def _get_q1_cmd(self):
        call_template = '{cmd_token} {call_token} {call_cmd}, {next_state}'        
        call_cmd = self.greater_than_token
        return call_template.format(
            cmd_token=self.cmd_token,
            call_token=self.call_token,
            call_cmd=call_cmd,
            next_state=Q2,
        )

    def _get_q2_cmd(self):
        call_template = '{cmd_token} {call_token} {call_cmd}, {next_state}'
        next_state = self.get_next_state()
        call_cmd = self.add_token
        return call_template.format(
            cmd_token=self.cmd_token,
            call_token=self.call_token,
            call_cmd=call_cmd,
            next_state=next_state
        )

    def _get_q3_cmd(self):
        call_template = '{cmd_token} {call_token} {call_cmd}, {next_state}'
        next_state = self.get_next_state()
        call_cmd = self.add_token
        return call_template.format(
            cmd_token=self.cmd_token,
            call_token=self.call_token,
            call_cmd=call_cmd,
            next_state=next_state
        )

     
    def get_call_state(self, choice):
        assert choice in ['input', 'output'], 'Invalid choice, should be either "input" or "output".'
        if choice == 'input':
            return self._get_call_state_input()
        elif choice == 'output':
            return self._get_call_state_output()
        
    def _get_call_state_input(self):
        if self.current_state == Q1:
            op1 = str(self.cnt)[::-1]
            op2 = self.op1
            output = self.cnt > int(self.op1[::-1])
            result = self.input_generator.get_q1_input(op1, op2, output)
        elif self.current_state == Q2:
            op1 = self.output
            op2 = 1
            output = str(int(self.output[::-1]) + 1)[::-1]
            carry_out = 1 if len(output) > len(op1) else 0
            result = self.input_generator.get_q2_input(op1, op2, carry_out, output)
        elif self.current_state == Q3:
            op1 = self.op2
            op2 = str(self.cnt)[::-1]
            output = str(int(op1[::-1]) + int(op2[::-1]))[::-1]
            carry_out = 1 if len(output) > len(op1) and len(output) > len(op2) else 0
            result = self.input_generator.get_q3_input(op1, op2, carry_out, output)
        else:
            return ''

        return result

    def _get_call_state_output(self):
        if self.current_state == Q0:
            return ''
        elif self.current_state == Q1:
            op1 = str(self.cnt)[::-1]
            return self.call_state_generator.get_q1_output(op1, self.op1)
        elif self.current_state == Q2:
            return self.call_state_generator.get_q2_output(self.output, 1)
        elif self.current_state == Q3:
            op2 = str(self.cnt)[::-1]
            return self.call_state_generator.get_q3_output(self.op2, op2)
        elif self.current_state == QH:
            return ''
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def get_call_cmd(self, choice):
        assert choice in ['input', 'output'], 'Invalid choice, should be either "input" or "output".'
        if self.current_state == Q0:
            return ''
        if choice == 'output':
            if self.current_state == Q1:
                return self.call_cmd_generator.get_q1_cmd()
            elif self.current_state == Q2:
                return self.call_cmd_generator.get_q2_cmd()
            elif self.current_state == Q3:
                return self.call_cmd_generator.get_q3_cmd()
            elif self.current_state == QH:
                return ''
            else:
                raise ValueError(f'Invalid state: {self.current_state}')
        else:
            return 'No command to execute. Halt state.'

    def one_step(self):
        if self.current_state == Q0:
            self._one_step_q0()
        elif self.current_state == Q1:
            self._one_step_q1()
        elif self.current_state == Q2:
            self._one_step_q2()
        elif self.current_state == Q3:
            self._one_step_q3()
        elif self.current_state == QH:
            self._one_step_qH()
        else:
            raise ValueError(f'Invalid state: {self.current_state}')
        
    def _one_step_q0(self):
        self.cnt = int(self.op2[::-1])
        self.output = '0'
        self.current_state = Q1

    def _one_step_q1(self):
        next_state = self.get_next_state()
        if next_state == Q2:
            # enter loop
            self.current_state = Q2
        else:
            # quit loop
            self.current_state = QH

    def _one_step_q2(self):
        # compute c += 1
        rev = lambda x: int(x[::-1])
        c = rev(self.output) + 1
        self.output = str(c)[::-1]
        self.current_state = Q3

    def _one_step_q3(self):
        # compute cnt += b
        self.cnt += int(self.op2[::-1])
        self.current_state = Q1

    def _one_step_qH(self):
        self.current_state = QH
        print('Halt')

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

    def get_input_output(self):  
        # Warning: this method is only for generating the input-output pair for the model.
        # DO NOT use this DivisionTM instance calling other methods after calling.
        assert self.current_state == Q0, 'Only support for initial state.'
        input_state = self.get_state()
        input_cmd = self.get_cmd()
        self.current_state = QH
        result = int(self.op1[::-1]) // int(self.op2[::-1])
        self.cnt = (result + 1) * int(self.op2[::-1])
        self.output = str(result)[::-1]
        output_state = self.get_state()
        output_cmd = self.get_cmd()
        return [input_state + '\n' + input_cmd + '\n', output_state + '\n' + output_cmd]

class DivisionTMChecker:
    def __init__(self, input):
        splits = input.strip().split('\n')
        state = splits[0]
        STATE_PATTERN = r'DIV, (.+),'
        state_match = re.search(STATE_PATTERN, state)
        if not state_match:
            raise ValueError('Invalid input format.')
        try:
            h1_token = '[HEAD1]'
            h2_token = '[HEAD2]'
            count_token = '[COUNT]'
            output_token = '[OUTPUT]'
            separator = '|'
            s = state.replace(state_match[0], '').replace(h1_token, '').replace(h2_token, '').replace(count_token, '').replace(output_token, '').replace(separator, '').strip()
            idx = s.find(' ')
            op1 = int((s[:idx].strip())[::-1])
            op2 = int((s[idx+1:].strip())[::-1])
            self.tm = DivisionTM(op1, op2)
        except:
            raise ValueError('Invalid input format.')
        self.tm = DivisionTM(op1, op2)
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
