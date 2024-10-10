class TMCallCommandGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.q2_token = 'q2'
        self.q3_token = 'q3'
        self.qH_token = 'qH'

        self.h_token = '[HEAD]'
        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.c_token = '[C]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'

        self.false_token = 'False'

        self.greater_than_q0_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {false_token}, {q1_token}'
        self.add_q0_template = '{cmd_token}: {c_token} 0, {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}'

    def get_q1_cmd(self):
        return self.greater_than_q0_template.format(cmd_token=self.cmd_token,
                                             h1_token=self.h1_token,
                                             h2_token=self.h2_token,
                                             right_token=self.right_token,
                                             output_token=self.output_token,
                                             false_token=self.false_token,
                                             q1_token=self.q1_token)
    
    def get_q2_cmd(self):
        return self.add_q0_template.format(cmd_token=self.cmd_token,
                                            c_token=self.c_token,
                                            h1_token=self.h1_token,
                                            right_token=self.right_token,
                                            h2_token=self.h2_token,
                                            q1_token=self.q1_token)
    
    def get_q3_cmd(self):
        return self.add_q0_template.format(cmd_token=self.cmd_token,
                                            c_token=self.c_token,
                                            h1_token=self.h1_token,
                                            right_token=self.right_token,
                                            h2_token=self.h2_token,
                                            q1_token=self.q1_token)