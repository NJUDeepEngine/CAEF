import json
import random
import re
import os

from data.generator import SubSeqGenerator
from data.proportion import Proportioner
from turing_machine.alignment.aligner import TMAligner

train_target_file_template = 'datasets/train/{prefix}sub{suffix}.json'
test_target_file_template = 'datasets/test/{prefix}sub_{min}_{max}{suffix}.jsonl'
raw_train_target_file = 'datasets/raw/subtraction/train.jsonl'
raw_test_target_file_template = 'datasets/raw/subtraction/test_{min}_{max}.jsonl'

SUBTRACTION_PROMPT = """The following is a input to be executed of a Turing Machine that performs subtraction.

To solve a substraction problem by the machine, the machine is required to provide the initial state and command for other basic machines, including addition, reflection and left mask. 

For example, for 47819 - 12345 = 35474, the machine will perform the following steps:
- step 1: call reflection, 99999 - 12345 = 87654
- step 2: call addtion, 47819 + 87654 = 135473
- step 3: call addtion, 135473 + 1 = 135474
- step 4: call left mask, left_mask(135474) = 35474

The input may includes four lines or the original subtraction problem. 
When it is original problem, generate the initial subtraction state, command and prepare the initial state and the first command of the first called machine. 
When it includes four lines, it means the previous state, command and the result of the called machine. In detail:
- The first line is the current state of the machine.
- The second line is the command to be executed.
- The third line and the fourth line are halt state of another machine which is called by the subtraction machine at previous step.

For the current state (the first line): 
- There are five states in the machine: q0, q1, q2, q3 and qH. The machine starts in state q0 and halts when it reaches state qH.
- The head positions are represented by [HEAD1] and [HEAD2], which followed by two operands. 

The command (the second line) includes a series of actions to be executed by the machine and they are separated by commas.
- [CALL] <operation>: Call another machine to perform the operation.
- <state>: Move the machine to the state.

When the commands include [CALL], another extra two lines are needed to specify the initial state and the first command of the machine to be called.
As for initial state, it should include the operation, q0 state, operands and the head positions.
As for the first command:
- [OUTPUT] <number>: Write the number to the output position.
- [OUTPUT] <direction>: Move the output head to the direction.
- [HEAD1] <direction>: Move the head on the first operand to the direction.
- [HEAD2] <direction>: Move the head on the second operand to the direction.
- <state>: Move the machine to the state.

The machine performs subtraction by reading the digits from the two operands and calling other machines to complete the subtraction operation. 

Based on the current input, predict the output which includes next state, next command and the initial state and the first command of the machine to be called.

"""

ALIGNMENT_PROMPT = """The following is an input to a Turing Machine or an output of a Turing Machine. 

The task is doing an alignment:
- If it is an input, adapt the original input to the format that the Turing Machine can understand.
- If it is an output, adapt the original output to the format that represents the final result.

Input example:
```
- input: 
4531-1504=
- output:
SUB, q0, [HEAD1]|1|3|5|4 [HEAD2]|4|0|5|1 
CMD q1
```

Output example:
```
- input:
SUB, qH, [HEAD1]|1|3|5|4 [HEAD2]|4|0|5|1 |7|2|0|3
No command to execute. Halt state.
- output:
4531-1504=3027
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
- [OUTPUT] <number>: Write the number to the output position.
- <state>: Move the machine to the state.

Note that the number is represented in reverse order in machine, which is beneficial to the machine to perform the subtraction operation.

Based on the input, determine it is an input or an output, and adapt it to the format correspondingly.

"""

def seq_2_samples(seq, args):
    samples = []
    for i in range(len(seq)):
        input = '' if args.no_prompt else SUBTRACTION_PROMPT
        input += seq[i][0]
        output = seq[i][1]
        samples.append((input, output))
        if args.init: # only the first state needed
            break
    return samples

def write_json_samples(samples, target_file, append=False):
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

def write_jsonl_samples(samples, target_file, append=False):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    random.shuffle(samples)
    target = open(target_file, 'a') if append else open(target_file, 'w')
    for sample in samples:
        prompt, response = sample
        target.write(json.dumps({"prompt": prompt, "response": response}) + '\n')
    target.close()

def generate_sample(generator, aligner, a_n_digits, b_n_digits, args):
    if args.setting == 'execute':
        seq = generator.generate(a_n_digits, b_n_digits)
        return seq_2_samples(seq, args)
    elif args.setting == 'alignment':
        op1, op2 = generator.generate_ops(a_n_digits, b_n_digits)
        raw_input = f'{op1}-{op2}='
        raw_output = raw_input + str(op1 - op2)
        input = aligner.input_to_tm(raw_input)
        seq = generator.generate_with_op(op1, op2)
        output = seq[-1][1]
        if not args.no_prompt:
            raw_input = ALIGNMENT_PROMPT + raw_input
            output = ALIGNMENT_PROMPT + output
        return [(raw_input, input), (output, raw_output)]
    elif args.setting == 'raw':
        input, output = generator.generate_raw(a_n_digits, b_n_digits)
        return [(input, output)]
    else:
        raise NotImplementedError

def generate_train(args):
    generator = SubSeqGenerator()
    samples = []
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='sub',
        option='balance'
    )
    aligner = TMAligner()
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, a_n_digits + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for _ in range(num):
                sample = generate_sample(generator, aligner, a_n_digits, b_n_digits, args)
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
        train_target_file = raw_train_target_file
        write_jsonl_samples(samples, train_target_file)
    else:
        train_target_file = train_target_file_template.format(prefix=prefix, suffix=suffix)
        write_json_samples(samples, train_target_file)

def raw_to_tm():
    n_digits = [5]
    pattern = r'(\d+)\-(\d+)='
    aligner = TMAligner()
    generator = SubSeqGenerator()
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
                    raw_output = raw_input + str(op1 - op2)
                    seq = generator.generate_with_op(op1, op2)
                    tm_output = seq[-1][1]
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
    
    generator = SubSeqGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='sub',
        option='balance'
    )
    samples = []
    aligner = TMAligner()
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, a_n_digits + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for _ in range(num):
                sample = generate_sample(generator, aligner, a_n_digits, b_n_digits, args)
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
  