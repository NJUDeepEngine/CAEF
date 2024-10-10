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

        self.greater_than_token = 'GREATER_THAN'
        self.add_token = 'ADD'

        self.greater_than_halt_template = '{operator}, {qH_token},  {l_op1}{h1_token}{r_op1} {l_op2}{h2_token}{r_op2} {output}'
        self.add_halt_tempalte = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {c_token}{carry_out} {output}'

    def get_q1_input(self, op1, op2, output):
        op1 = str(op1)
        op2 = str(op2)

        idx = min(len(op1), len(op2))
        l_op1 = op1[:idx]
        r_op1 = op1[idx:]
        l_op2 = op2[:idx]
        r_op2 = op2[idx:]
        
        sep = self.separator
        if len(sep) > 0:
            l_op1 = sep + sep.join(l_op1) if len(l_op1) > 0 else ''
            r_op1 = sep + sep.join(r_op1) if len(r_op1) > 0 else ''
            l_op2 = sep + sep.join(l_op2) if len(l_op2) > 0 else ''
            r_op2 = sep + sep.join(r_op2) if len(r_op2) > 0 else ''
        
        return self.greater_than_halt_template.format(operator=self.greater_than_token,
                                                    qH_token=self.qH_token,
                                                    h1_token=self.h1_token,
                                                    h2_token=self.h2_token,
                                                    l_op1=l_op1,
                                                    r_op1=r_op1,
                                                    l_op2=l_op2,
                                                    r_op2=r_op2,
                                                    output_token=self.output_token,
                                                    output=output)

        
    
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