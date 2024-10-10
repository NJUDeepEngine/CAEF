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

class TMCommandGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.q2_token = 'q2'
        self.qH_token = 'qH'

        self.h_token = '[HEAD]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'

        self.q0_cmd_template = '{cmd_token} {h_token} {right_token}, {q1_token}'
        self.q1_2_q1_cmd_template = '{cmd_token} {h_token} {right_token}, {output_token} {output}, {output_token} {right_token}, {q1_token}'
        self.q1_2_q2_cmd_template = '{cmd_token} {output_token} {left_token}, {output_token} 0, {q2_token}'
        self.q2_2_q2_cmd_template = '{cmd_token} {output_token} {left_token}, {q2_token}'
        self.q2_2_qH_cmd_template = '{cmd_token} {qH_token}'


    def get_q0_cmd(self):
        return self.q0_cmd_template.format(cmd_token=self.cmd_token,
                                           h_token=self.h_token,
                                           right_token=self.right_token,
                                           q1_token=self.q1_token)
    
    def get_q1_cmd(self, output, next_state):
        if next_state == 'q1':
            return self.q1_2_q1_cmd_template.format(cmd_token=self.cmd_token,
                                                    h_token=self.h_token,
                                                    right_token=self.right_token,
                                                    output_token=self.output_token,
                                                    output=output,
                                                    q1_token=self.q1_token)
        elif next_state == 'q2':
            return self.q1_2_q2_cmd_template.format(cmd_token=self.cmd_token,
                                                    h_token=self.h_token,
                                                    left_token=self.left_token,
                                                    output_token=self.output_token,
                                                    q2_token=self.q2_token)
        
    def get_q2_cmd(self, next_state):
        if next_state == 'q2':
            return self.q2_2_q2_cmd_template.format(cmd_token=self.cmd_token,
                                                    output_token=self.output_token,
                                                    left_token=self.left_token,
                                                    q2_token=self.q2_token)
        elif next_state == 'qH':
            return self.q2_2_qH_cmd_template.format(cmd_token=self.cmd_token,
                                                    qH_token=self.qH_token)
        
if __name__ == '__main__':
    cmd_gen = TMCommandGenerator()
    # q0 test
    q0_str = 'CMD [HEAD] RIGHT, q1'
    qo_str_gen = cmd_gen.get_q0_cmd()
    assert q0_str == qo_str_gen, f"Expected: {q0_str}, Got: {qo_str_gen}"

    # q1 to q1 test
    q1_str = 'CMD [HEAD] RIGHT, [OUTPUT] 4, [OUTPUT] RIGHT, q1'
    q1_str_gen = cmd_gen.get_q1_cmd(4, 'q1')
    assert q1_str == q1_str_gen, f"Expected: {q1_str}, Got: {q1_str_gen}"

    # q1 to qH test
    qH_str = 'CMD [OUTPUT] LEFT, [OUTPUT] 0, qH'
    qH_str_gen = cmd_gen.get_q1_cmd(0, 'qH')
    assert qH_str == qH_str_gen, f"Expected: {qH_str}, Got: {qH_str_gen}"