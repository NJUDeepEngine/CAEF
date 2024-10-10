import json
import random
import re
import os

from data.generator import LessThanSeqGenerator
from data.proportion import Proportioner
from turing_machine.alignment.aligner import TMAligner

train_target_file_template = 'datasets/train/{prefix}less_than{suffix}.json'
test_target_file_template = 'datasets/test/{prefix}less_than_{min}_{max}{suffix}.jsonl'
raw_train_target_file = 'datasets/raw/less_than/train.jsonl'
raw_test_target_file_template = 'datasets/raw/less_than/test_{min}_{max}.jsonl'

LESS_THAN_PROMPT = """The following is a state paired with a command to be executed of a Turing Machine that determines whether the first operand is less than the second operand.

The state includes the current operator, the current state of the machine, the current tape contents, and the current head positions.
- There are three states in the machine: q0, q1, and qH. The machine starts in state q0 and halts when it reaches state qH. q1 is the state where the machine does the comparison.
- The head positions are represented by [HEAD1] and [HEAD2], which indicate the positions of the heads on the two operands. 
- The output position is represented by [OUTPUT].

The command includes a series of actions to be executed by the machine and they are separated by commas.
- [OUTPUT] <number>: Write the number to the output position.
- [OUTPUT] <direction>: Move the output head to the direction.
- [HEAD1] <direction>: Move the head on the first operand to the direction.
- [HEAD2] <direction>: Move the head on the second operand to the direction.
- <state>: Move the machine to the state.

The machine performs comparison by reading the digits from the two operands and writing the result to the output tape. 

Based on the current state and the command, predict the next state of the machine and next command to be executed.

"""

ALIGNMENT_PROMPT = """The following is an input to a Turing Machine or an output of a Turing Machine. 

The task is doing an alignment:
- If it is an input, adapt the original input to the format that the Turing Machine can understand.
- If it is an output, adapt the original output to the format that represents the final result.

Input example:
```
- input: 
47182<83911=
- output:
LESS_THAN, q0, [HEAD1] |2|8|1|7|4[HEAD2] |1|1|9|3|8 [OUTPUT]
CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] False, q1
```

Output example:
```
- input:
LESS_THAN, qH,  |2|8|1|7|4[HEAD1] |1|1|9|3|8[HEAD2] True
No command to execute. Halt state.
- output:
47182<83911=True
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
- [OUTPUT] <result>: Write the result to the output position.
- <state>: Move the machine to the state.

Based on the input, determine it is an input or an output, and adapt it to the format correspondingly.

"""

def seq_2_samples(seq, args):
    samples = []
    if args.init: # only the first state needed
        input = seq[0][0] + '\n' + seq[0][1] + '\n'
        output = seq[-1][0] + '\n' + seq[-1][1] + '\n'
        samples.append((input, output))
        return samples
    for i in range(len(seq) - 1):
        input = '' if args.no_prompt else LESS_THAN_PROMPT
        input += seq[i][0] + '\n' + seq[i][1] + '\n'
        output = seq[i + 1][0] + '\n' + seq[i + 1][1] + '\n'
        samples.append((input, output))
    if len(samples) <= 5:
        return samples
    else:
        trancated_samples = [samples[0], samples[-1], samples[-2]]
        for i in range(1, 5):
            trancated_samples.append(samples[random.randint(1, len(samples) - 3)])
        return trancated_samples

def write_json_samples(samples, target_file):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    random.shuffle(samples)
    target = open(target_file, 'w')
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

def write_jsonl_samples(samples, target_file):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    random.shuffle(samples)
    target = open(target_file, 'w')
    for sample in samples:
        prompt, response = sample
        target.write(json.dumps({"prompt": prompt, "response": response}) + '\n')
    target.close()

def generate_sample(generator, aligner, a_n_digits, b_n_digits, option, args):
    if args.setting == 'execute':
        seq = generator.generate(a_n_digits, b_n_digits, option)
        return seq_2_samples(seq, args)
    elif args.setting == 'alignment':
        op1, op2 = generator.generate_ops(a_n_digits, b_n_digits, option)
        raw_input = f'{op1}<{op2}='
        raw_output = raw_input + str(op1 < op2)
        input = aligner.input_to_tm(raw_input)
        seq = generator.generate_with_op(op1, op2)
        output = seq[-1][0] + '\n' + seq[-1][1] + '\n'
        if not args.no_prompt:
            raw_input = ALIGNMENT_PROMPT + raw_input
            output = ALIGNMENT_PROMPT + output
        return [(raw_input, input), (output, raw_output)]
    elif args.setting == 'raw':
        input, output = generator.generate_raw(a_n_digits, b_n_digits, option)
        return [(input, output)]
    else:
        raise NotImplementedError

def generate_train(args):
    generator = LessThanSeqGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='less_than',
        option='balance'
    )
    samples = []
    aligner = TMAligner()
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, args.max + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for i in range(num):
                option = None
                if a_n_digits == b_n_digits and i % 2 == 0:
                    option = 'equal'
                sample = generate_sample(generator, aligner, a_n_digits, b_n_digits, option, args)
                samples.extend(sample)
    if args.setting == 'execute':
        prefix = 'execute_'
        suffix = '_no_prompt' if args.no_prompt else ''
        suffix += '_special'
    elif args.setting == 'alignment':
        prefix = ''
        suffix = '_alignment'
        suffix += '_no_prompt' if args.no_prompt else ''
    elif args.setting == 'raw':
        prefix = suffix = ''
    else:
        raise NotImplementedError
    
    if args.setting == 'raw':
        train_target_file = raw_train_target_file
        write_jsonl_samples(samples, train_target_file)
    else:
        train_target_file = train_target_file_template.format(prefix=prefix, suffix=suffix)
        write_json_samples(samples, train_target_file)

def raw_to_tm():
    n_digits = [5, 10, 50 ,100]
    pattern = r'(\d+)<(\d+)='
    aligner = TMAligner()
    generator = LessThanSeqGenerator()
    for n_digit in n_digits:
        raw_f = raw_test_target_file_template.format(min=n_digit, max=n_digit)
        executor_samples = []
        aligner_input_samples = []
        aligner_output_samples = []
        with open(raw_f, 'r') as f:
            for line in f:
                sample = json.loads(line)
                raw_input = sample['prompt']
                match = re.search(pattern, raw_input)
                if match:
                    op1, op2 = match.groups()
                    op1, op2 = int(op1), int(op2)
                    tm_input = aligner.input_to_tm(raw_input)
                    raw_output = raw_input + str(op1 < op2)
                    seq = generator.generate_with_op(op1, op2)
                    tm_output = seq[-1][0] + '\n' + seq[-1][1] + '\n'
                    executor_samples.append((tm_input, tm_output))
                    aligner_input_samples.append((raw_input, tm_input))
                    aligner_output_samples.append((tm_output, raw_output))
                else:
                    raise ValueError(f'Invalid input: {raw_input}')
        write_jsonl_samples(executor_samples, test_target_file_template.format(min=n_digit, max=n_digit, prefix='execute_', suffix='_executor'))
        write_jsonl_samples(aligner_input_samples, test_target_file_template.format(min=n_digit, max=n_digit, prefix='execute_', suffix='_aligner_input'))
        write_jsonl_samples(aligner_output_samples, test_target_file_template.format(min=n_digit, max=n_digit, prefix='execute_', suffix='_aligner_output'))

def generate_test(args):
    if args.setting == 'separate':
        raw_to_tm()
        return
    
    generator = LessThanSeqGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='less_than',
        option='balance'
    )
    samples = []
    aligner = TMAligner()
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, args.max + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for i in range(num):
                option = None
                if a_n_digits == b_n_digits and i % 2 == 0:
                    option = 'equal'
                sample = generate_sample(generator, aligner, a_n_digits, b_n_digits, option, args)
                samples.extend(sample)

    if args.setting == 'execute':
        prefix = 'execute_'
        suffix = '_no_prompt' if args.no_prompt else ''
    elif args.setting == 'alignment':
        prefix = ''
        suffix = '_alignment'
        suffix += '_no_prompt' if args.no_prompt else ''
    elif args.setting == 'raw':
        prefix = suffix = ''
    else:
        raise NotImplementedError
    
    if args.setting == 'raw':
        test_target_file = raw_test_target_file_template.format(min=args.min, max=args.max)
    else:
        test_target_file = test_target_file_template.format(
            min=args.min, max=args.max, prefix=prefix, suffix=suffix)
    write_jsonl_samples(samples, test_target_file)

def generate(args):
    if args.split == 'train':
        random.seed(42)
        generate_train(args)
    elif args.split == 'test':
        random.seed(43)
        generate_test(args)
