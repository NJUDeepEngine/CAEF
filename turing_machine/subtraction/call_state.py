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
        self.reflection_token = 'REFLECTION'
        self.left_mask_token = 'LEFT_MASK'

        # init state templates
        self.sub_template = '{op1}-{op2}='
        self.reflection_init_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}'
        self.add_init_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {c_token} {output_token}'
        self.left_mask_init_template = '{operator}, {q0_token}, {h_token} {op} {output_token}'

        # halt state templates
        self.refelction_halt_template = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {output}'
        self.add_halt_tempalte = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {c_token}{carry_out} {output}'
        self.left_mask_halt_template = '{operator}, {qH_token},  {op}{h_token} {output}'

    def get_q1_output(self, op1, op2):
        op1 = str(op1)
        op2 = str(op2)
        separator = self.separator
        if len(separator) > 0:
            op1 = separator + separator.join(op1)
            op2 = separator + separator.join(op2)
        return self.reflection_init_template.format(operator=self.reflection_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            output_token=self.output_token,
                                            op1=op1,
                                            op2=op2,
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
    
    def get_q3_output(self, op):
        op1 = str(op)
        op2 = '1'
        separator = self.separator
        if len(separator) > 0:
            op1 = separator + separator.join(op1)
            op2 = separator + separator.join(op2)
        return self.add_init_template.format(operator=self.add_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            output_token=self.output_token,
                                            op1=op1,
                                            op2=op2,
                                            q0_token=self.q0_token)
    
    def get_q4_output(self, op):
        op = str(op)
        separator = self.separator
        if len(separator) > 0:
            op = separator + separator.join(op)

        return self.left_mask_init_template.format(operator=self.left_mask_token,
                                            h_token=self.h_token,
                                            output_token=self.output_token,
                                            op=op,
                                            q0_token=self.q0_token)   