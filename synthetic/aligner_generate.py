import json
import random
import os

from data.generator import AlignerPairGenerator
from data.proportion import Proportioner

train_target_file_template = 'datasets/train/alignment{suffix}.json'
test_target_file_template = 'datasets/test/alignment_{min}_{max}{suffix}.jsonl'

ALIGNMENT_PROMPT = """The following is an input to a Turing Machine or an output of a Turing Machine. 

The task is doing an alignment:
- If it is an input, adapt the original input to the format that the Turing Machine can understand.
- If it is an output, adapt the original output to the format that represents the final result.

Input example:
```
- input: 
1504+2379=
- output:
ADD, q0, [HEAD1] |4|0|5|1[HEAD2] |9|7|3|2 [C] [OUTPUT]
CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1
```

Output example:
```
- input:
MUL, qH, [HEAD1]|4|1|8|4|4 [HEAD2]|5 [COUNT]|5 |0|7|0|4|2|2
No command to execute. Halt state.
- output:
44814*5=224070

```

There are two lines that represent the Turing Machine:
- The first line is the current state of the machine.
- The second line is the command to be executed.
And this format is fit to both input and output as the examples shown above.

For the current state (the first line): 
- There are at least 2 states in the machine: q0 and qH. The machine starts in state q0 and halts when it reaches state qH.
- The head positions are represented by [HEAD1] and [HEAD2], which followed by two operands. 

The command (the second line) includes a series of actions to be executed by the machine and they are separated by commas.
- [HEAD] <direction>: Move the head to the direction.
- [OUTPUT] <direction>: Move the output head to the direction.
- [OUTPUT] <number>: Write the number to the output position.
- [C] <number>: Write the number to the carry out register.
- [COUNT] <number>: Write the number to the count register.
- [CALL] <operation>: Call another machine to perform the operation.
- <state>: Move the machine to the state.

Based on the input, determine it is an input or an output, and adapt it to the format correspondingly.

"""

def align_pair(pair, args):
    if args.no_prompt:
        return pair
    input, output = pair
    return (ALIGNMENT_PROMPT + input, output)

def get_extra_pairs(a_n_digits, b_n_digits, num, generator, args):
    pairs = []
    operators = [
        ('*', 'mul'),
        ('//', 'div'),
    ]
    if a_n_digits > 5 or b_n_digits > 5:
        return pairs

    for i in range(num * 10):
        for op, task in operators:
            if i % 2 == 0:
                pair = generator.generate_input_pair(a_n_digits, b_n_digits, op)
            else:
                pair = generator.generate_output_pair(a_n_digits, b_n_digits, task)
            if pair:
                pairs.append(align_pair(pair, args))

    return pairs

def write_json_samples(samples, target_file, append):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    random.shuffle(samples)
    target = open(target_file, 'a') if append else open(target_file, 'w')
    target.write('[\n')
    cnt = 0
    for sample in samples:
        if cnt != 0:
            target.write(",\n")
        cnt += 1
        prompt, response = sample
        json.dump({"instruction": prompt, "input": "", "output": response}, target, ensure_ascii=False, indent=4)


    target.write('\n]\n')
    target.close()

def write_jsonl_samples(samples, target_file, append):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    random.shuffle(samples)
    target = open(target_file, 'a') if append else open(target_file, 'w')
    for sample in samples:
        prompt, response = sample
        target.write(json.dumps({"prompt": prompt, "response": response}) + '\n')
    target.close()

def generate_train(args):
    generator = AlignerPairGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='align',
        option='balance'
    )
    samples = []
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min,  args.max + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for i in range(num):
                if i % 2 == 0:
                    pair = generator.generate_input_pair(a_n_digits, b_n_digits)
                else:
                    pair = generator.generate_output_pair(a_n_digits, b_n_digits)
                if pair:
                    samples.append(align_pair(pair, args))
            pairs = get_extra_pairs(a_n_digits, b_n_digits, num, generator, args)
            samples.extend(pairs)
    train_target_file = train_target_file_template.format(suffix='_no_prompt' if args.no_prompt else '')
    write_json_samples(samples, train_target_file, args.append)

def generate_test(args):
    generator = AlignerPairGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='align',
        option='balance'
    )
    samples = []

    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, args.max + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for i in range(num):
                if i % 2 == 0:
                    pair = generator.generate_input_pair(a_n_digits, b_n_digits)
                else:
                    pair = generator.generate_output_pair(a_n_digits, b_n_digits)
                if pair:
                    samples.append(align_pair(pair, args))
            pairs = get_extra_pairs(a_n_digits, b_n_digits, num, generator, args)
            samples.extend(pairs)

    suffix = ''
    if args.no_prompt:
        suffix += '_no_prompt'
    test_target_file = test_target_file_template.format(
        min=args.min, max=args.max, suffix=suffix)
    write_jsonl_samples(samples, test_target_file, args.append)

def generate(args):
    if args.split == 'train':
        random.seed(42)
        generate_train(args)
    elif args.split == 'test':
        random.seed(43)
        generate_test(args)