from typing import Literal
import math

class Proportioner:
    def __init__(self, minimal, maximal, num, task, option: Literal['default', 'balance']):
        self.minimal = minimal
        self.maximal = maximal
        self.num = num
        self.task = task
        self.option = option

    def get_num(self, **kwargs):

        task_func_mapping = dict(
            add=self._get_num_add,
            reflection=self._get_num_reflection,
            left_mask=self._get_num_left_mask,
            sub=self._get_num_sub,
            equal=self._get_num_equal,
            greater_than=self._get_num_greater_than,
            less_than=self._get_num_less_than,
            mul=self._get_num_mul,
            div=self._get_num_div,
            align=self._get_num_align,
        )

        return task_func_mapping[self.task](**kwargs)

        
    def _get_num_add(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits > 10 and b_n_digits > 10 and (a_n_digits / b_n_digits > 1.5 or b_n_digits / a_n_digits > 1.5):
                num = num // 2
            if a_n_digits <= 10 and b_n_digits <= 10:
                num *= 10
            return num

    def _get_num_reflection(self, **kwargs):
        pass

    def _get_num_left_mask(self, **kwargs):
        pass

    def _get_num_sub(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits > 10 and b_n_digits > 10 and (a_n_digits / b_n_digits > 1.5 or b_n_digits / a_n_digits > 1.5):
                num = num // 2
            if a_n_digits <= 10 and b_n_digits < 10:
                num *= 5
            return num
        
    def _get_num_equal(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            equal_scale_factor = 10
            if a_n_digits == b_n_digits:
                num *= equal_scale_factor
                if a_n_digits <= 10:
                    num *= 10
                return num
            choice = self.maximal - self.minimal + 1
            class_num = choice * choice
            equal_class_num = choice
            unequal_scale_factor = equal_class_num * equal_scale_factor / class_num
            return math.ceil(num * unequal_scale_factor)
        
    def _get_num_greater_than(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits <= 5 and b_n_digits <= 5:
                num *= 10
            return num
        
    def _get_num_less_than(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits <= 5 and b_n_digits <= 5:
                num *= 10
            return num

    def _get_num_mul(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits <= 10 or b_n_digits <= 10:
                num *= 2
            return num
        
    def _get_num_div(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            if a_n_digits < b_n_digits:
                return 5
            if a_n_digits - b_n_digits > 5:
                return 0
            num = self.num
            if a_n_digits - b_n_digits <= 2:
                num *= 2
            elif a_n_digits - b_n_digits > 3:
                num = num // 2
            return num
        
    def _get_num_align(self, **kwargs):
        a_n_digits = kwargs['a_n_digits']
        b_n_digits = kwargs['b_n_digits']
        if self.option == 'default':
            return self.num
        if self.option == 'balance':
            num = self.num
            if a_n_digits <= 10 or b_n_digits <= 10:
                num *= 2
            return num