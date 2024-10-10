class TMCallStateGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h_token = '[HEAD]'
        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.c_token = '[C]'
        self.output_token = '[OUTPUT]'
        self.separator = '|'

        self.add_token = 'ADD'
        self.sub_token = 'SUB'
        self.less_than_token = 'LESS_THAN'

        self.less_than_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}'
        self.add_init_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {c_token} {output_token}'


    def get_q1_output(self, op1, op2):
        operand1 = str(op1)
        operand2 = str(op2)
        separator = self.separator
        if len(separator) > 0:
            operand1 = separator + separator.join(operand1)
            operand2 = separator + separator.join(operand2)
        return self.less_than_template.format(operator=self.less_than_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            output_token=self.output_token,
                                            op1=operand1,
                                            op2=operand2,
                                            q0_token=self.q0_token)
    
    def get_q2_output(self, op1, op2):
        operand1 = str(op1)
        operand2 = str(op2)
        separator = self.separator
        if len(separator) > 0:
            operand1 = separator + separator.join(operand1)
            operand2 = separator + separator.join(operand2)
        return self.add_init_template.format(operator=self.add_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            output_token=self.output_token,
                                            op1=operand1,
                                            op2=operand2,
                                            q0_token=self.q0_token)
    
    def get_q3_output(self, op1, op2):
        operand1 = str(op1)
        operand2 = str(op2)
        separator = self.separator
        if len(separator) > 0:
            operand1 = separator + separator.join(operand1)
            operand2 = separator + separator.join(operand2)
        return self.add_init_template.format(operator=self.add_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            output_token=self.output_token,
                                            op1=operand1,
                                            op2=operand2,
                                            q0_token=self.q0_token)