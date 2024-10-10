import re

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - EQUAL, q0, [HEAD1] 1234[HEAD2] 1234 [OUTPUT]
    - EQUAL, q1,  [HEAD1]1234 [HEAD2]1234 [OUTPUT]True
    - EQUAL, q1,  1[HEAD1]234 1[HEAD2]234 [OUTPUT]True
    - EQUAL, q1,  1234[HEAD1] 1234[HEAD2] [OUTPUT]True
    - EQUAL, qH,  1234[HEAD1] 1234[HEAD2] True
    - EQUAL, q1,  1[HEAD1]234 1[HEAD2]934 [OUTPUT]True
    - EQUAL, qH,  123[HEAD1] 123[HEAD2]4 [OUTPUT]True
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] True, q1
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [OUTPUT], qH
    - No command to execute. Halt state.
    - CMD [OUTPUT] False, [OUTPUT], qH
    - CMD [OUTPUT] False, [OUTPUT], qH
"""

class EqualTMCommandGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'
        self.true_token = 'True'
        self.false_token = 'False'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'
        
        # Machine will halt when it reaches qH, so there is no qH_cmd_template.
        self.q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {true_token}, {q1_token}'
        self.q1_2_q1_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}'
        self.q1_2_qH_true_cmd_template = '{cmd_token} {output_token}, {qH_token}'
        self.q1_2_qH_false_cmd_template = '{cmd_token} {output_token} {false_token}, {output_token}, {qH_token}'

    def get_q0_cmd(self):
        return self.q0_cmd_template.format(cmd_token=self.cmd_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            right_token=self.right_token,
                                            output_token=self.output_token,
                                            true_token=self.true_token,
                                            q1_token=self.q1_token)

    def get_q1_cmd(self, output, next_state):
        if next_state == 'q1':
            return self.q1_2_q1_cmd_template.format(cmd_token=self.cmd_token,
                                                    h1_token=self.h1_token,
                                                    h2_token=self.h2_token,
                                                    right_token=self.right_token,
                                                    q1_token=self.q1_token)
        elif next_state == 'qH':
            output = str(output)
            if output == 'True':
                return self.q1_2_qH_true_cmd_template.format(cmd_token=self.cmd_token,
                                                            output_token=self.output_token,
                                                            qH_token=self.qH_token)
            else:
                return self.q1_2_qH_false_cmd_template.format(cmd_token=self.cmd_token,
                                                            output_token=self.output_token,
                                                            false_token=self.false_token,
                                                            qH_token=self.qH_token)
        else:
            raise ValueError(f'Invalid next state: {next_state}')
        
if __name__ == '__main__':
    generator = EqualTMCommandGenerator()
    # q0 test
    q0_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] True, q1'
    q0_gen = generator.get_q0_cmd()
    assert q0_str == q0_gen, f'Expect {q0_str}, Got {q0_gen}'

    # q1 to q1 test
    q1_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, q1'
    q1_gen = generator.get_q1_cmd('True', 'q1')
    assert q1_str == q1_gen, f'Expect {q1_str}, Got {q1_gen}'

    # q1 to qH true test
    qH_true_str = 'CMD [OUTPUT], qH'
    qH_true_gen = generator.get_q1_cmd('True', 'qH')
    assert qH_true_str == qH_true_gen, f'Expect {qH_true_str}, Got {qH_true_gen}'

    # q1 to qH false test
    qH_false_str = 'CMD [OUTPUT] False, [OUTPUT], qH'
    qH_false_gen = generator.get_q1_cmd('False', 'qH')
    assert qH_false_str == qH_false_gen, f'Expect {qH_false_str}, Got {qH_false_gen}'