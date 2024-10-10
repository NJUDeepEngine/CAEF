import argparse

from synthetic.add_generate import generate as add_gen
from synthetic.reflection_generate import generate as ref_gen
from synthetic.left_mask_generate import generate as lm_gen
from synthetic.sub_generate import generate as sub_gen
from synthetic.equal_generate import generate as eq_gen
from synthetic.greater_than_generate import generate as gt_gen
from synthetic.less_than_generate import generate as lt_gen
from synthetic.mul_generate import generate as mul_gen
from synthetic.div_generate import generate as div_gen
from synthetic.aligner_generate import generate as alignment_gen


legal_tasks = ['add', 'reflection', 'left_mask', 'sub', 'equal', 'greater_than', 'less_than', 'mul', 'div', 'alignment']

task_gen_mapping = dict(
    add=add_gen,
    reflection=ref_gen,
    left_mask=lm_gen,
    sub=sub_gen,
    equal=eq_gen,
    greater_than=gt_gen,
    less_than=lt_gen,
    mul=mul_gen,
    div=div_gen,
    alginment=alignment_gen,
)

def generate(args):
    task = args.task
    gen_func = task_gen_mapping[task]
    gen_func(args)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--min', default=1, type=int, required=False)
    argparser.add_argument('--max', default=10, type=int, required=False)
    argparser.add_argument('--num', default=20, type=int, required=False)
    argparser.add_argument('--split', type=str, required=False, choices=['train', 'test'])
    argparser.add_argument('--task', type=str, required=False, choices=legal_tasks)
    argparser.add_argument('--no_prompt', action='store_true', required=False)
    argparser.add_argument('--init', action='store_true', required=False)
    argparser.add_argument('--append', action='store_true', required=False)
    argparser.add_argument('--setting', type=str, required=False, choices=['execute', 'raw', 'alignment', 'separate'])
    args = argparser.parse_args()

    generate(args)