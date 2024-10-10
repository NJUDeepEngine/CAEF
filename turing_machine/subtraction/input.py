class TMInputGenerator:
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
        self.separator = '|'

        self.add_token = 'ADD'
        self.sub_token = 'SUB'
        self.reflection_token = 'REFLECTION'
        self.left_mask_token = 'LEFT_MASK'

        self.refelction_halt_template = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {output}'
        self.add_halt_tempalte = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {c_token}{carry_out} {output}'
        self.left_mask_halt_template = '{operator}, {qH_token},  {op}{h_token} {output}'
    
    def get_q1_input(self, op1, op2, output):
        op1 = str(op1)
        op2 = str(op2)
        output = str(output)

        sep = self.separator
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)
            output = sep + sep.join(output)

        return self.refelction_halt_template.format(operator=self.reflection_token,
                                            qH_token=self.qH_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            output=output,
                                            op1=op1,
                                            op2=op2)
    
    def get_q2_input(self, op1, op2, carry_out, output):
        op1 = str(op1)
        op2 = str(op2)
        output = str(output)

        sep = self.separator
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)
            output = sep + sep.join(output)

        return self.add_halt_tempalte.format(operator=self.add_token,
                                            qH_token=self.qH_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            carry_out=carry_out,
                                            output=output,
                                            op1=op1,
                                            op2=op2)
    
    def get_q3_input(self, op1, op2, carry_out, output):
        op1 = str(op1)
        op2 = str(op2)
        output = str(output)

        sep = self.separator
        if len(sep) > 0:
            op1 = sep + sep.join(op1)
            op2 = sep + sep.join(op2)
            output = sep + sep.join(output)

        return self.add_halt_tempalte.format(operator=self.add_token,
                                            qH_token=self.qH_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            carry_out=carry_out,
                                            output=output,
                                            op1=op1,
                                            op2=op2)
    
    def get_q4_input(self, op, output):
        op = str(op)
        output = str(output)

        sep = self.separator
        if len(sep) > 0:
            op = sep + sep.join(op)
            output = sep + sep.join(output)

        return self.left_mask_halt_template.format(operator=self.left_mask_token,
                                                    qH_token=self.qH_token,
                                                    h_token=self.h_token,
                                                    output=output,
                                                    op=op)