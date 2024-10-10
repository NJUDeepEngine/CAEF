import json
import random
import re
import os

from data.generator import DivSeqGenerator
from data.proportion import Proportioner
from turing_machine.alignment.aligner import TMAligner

train_target_file_template = 'datasets/train/{prefix}div{suffix}.json'
test_target_file_template = 'datasets/test/{prefix}div_{min}_{max}{suffix}.jsonl'
raw_train_target_file = 'datasets/raw/division/train.jsonl'
raw_test_target_file_template = 'datasets/raw/division/test_{min}_{max}.jsonl'

DIVISION_PROMPT = """The following is a input to be executed of a Turing Machine that performs division.

To solve a division problem by the machine, the machine is required to provide the initial state and command for other basic machines, including addition and greater_than machines. 

For example, for 4513 // 1504 = 3, the machine will perform the following algorithm:
- step 1: output = 0, cnt = 1504(oprand2)
- step 2: call greater_than, determine whether cnt > 4513(oprand1), if yes, go to step 5, otherwise, go to step 3
- step 3: call addition, output = output + 1
- step 4: call addition, cnt = cnt + 1504, go to step 2
- step 5: current machine halts, output is the result

The input includes at least two lines and may have two more lines.
- The first line is the current state of the machine.
- The second line is the command to be executed.
When there are two more lines:
- The third line and the fourth line are halt state of another machine which is called by the division machine at previous step.

For the current state (the first line): 
- There are five states in the machine: q0, q1, q2, q3 and qH. The machine starts in state q0 and halts when it reaches state qH. q1, q2 and q3 are used to perform the loop structure.
- The head positions are represented by [HEAD1] and [HEAD2], which followed by two operands. 

The command (the second line) includes a series of actions to be executed by the machine and they are separated by commas.
- [OUTPUT] <number>: Write the number to the output position.
- [COUNT] <number>: Write the number to the count register.
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

The machine performs division by reading the digits from the two operands and calling other machines to complete the division operation. 

Based on the current input, predict the output which includes next state, next command and the initial state and the first command of the machine to be called.

"""

ALIGNMENT_PROMPT = """The following is an input to a Turing Machine or an output of a Turing Machine. 

The task is doing an alignment:
- If it is an input, adapt the original input to the format that the Turing Machine can understand.
- If it is an output, adapt the original output to the format that represents the final result.

Input example:
```
- input: 
4531//1504=
- output:
DIV, q0, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT] [OUTPUT]
CMD [COUNT]|4|0|5|1, [OUTPUT] 0, q1
```

Output example:
```
- input:
DIV, qH, [HEAD1]|3|1|5|4 [HEAD2]|4|0|5|1 [COUNT]|6|1|0|6 |3
No command to execute. Halt state.
- output:
4531//1504=3
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
- [COUNT] <number>: Write the number to the count register.
- <state>: Move the machine to the state.

Based on the input, determine it is an input or an output, and adapt it to the format correspondingly.

"""

def seq_2_samples(seq, args):
    samples = []
    for i in range(len(seq)):
        input = '' if args.no_prompt else DIVISION_PROMPT
        input += seq[i][0]
        output = seq[i][1]
        samples.append((input, output))
    if args.init:
        input = samples[0][0]
        output = samples[-1][1]
        return [(input, output)]
    if len(samples) <= 10:
        return samples
    else:
        trancated_samples = [samples[0], samples[-1]]
        for i in range(1, 4):
            trancated_samples.append(samples[random.randint(1, len(samples) - 2)])
        return trancated_samples

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

def generate_sample_train(generator, aligner, a_n_digits, b_n_digits, args):
    if args.setting == 'execute':
        seq = generator.generate(a_n_digits, b_n_digits)
        return seq_2_samples(seq, args)
    elif args.setting == 'alignment':
        op1, op2 = generator.generate_ops(a_n_digits, b_n_digits)
        raw_input = f'{op1}//{op2}='
        raw_output = raw_input + str(op1 // op2)
        input = aligner.input_to_tm(raw_input)
        seq = generator.generate_with_op(op1, op2, only_input_output=True)
        output = seq[-1]
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
    generator = DivSeqGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='div',
        option='balance'
    )
    samples = []
    aligner = TMAligner()
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min,  args.max + 1):
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for _ in range(num):
                sample = generate_sample_train(generator, aligner, a_n_digits, b_n_digits, args)
                if sample:
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

def generate_sample_test(generator, aligner, a_n_digits, b_n_digits, args):
    if args.setting == 'execute':
        seq = generator.generate(a_n_digits, b_n_digits)
        return seq_2_samples(seq, args)
    elif args.setting == 'alignment':
        op1, op2 = generator.generate_ops(a_n_digits, b_n_digits)
        raw_input = f'{op1}//{op2}='
        raw_output = raw_input + str(op1 // op2)
        input = aligner.input_to_tm(raw_input)
        seq = generator.generate_with_op(op1, op2)
        output = seq[-1][1]
        if not args.no_prompt:
            raw_input = ALIGNMENT_PROMPT + raw_input
            output = ALIGNMENT_PROMPT + output
        return [(raw_input, input), (output, raw_output)]
    elif args.setting == 'raw':
        input, output = generator.generate_raw_with_fixed_result(b_n_digits)
        return [(input, output)]
    else:
        raise NotImplementedError

def raw_to_tm():
    executor_samples = []
    aligner_input_samples = []
    aligner_output_samples = []
    pattern = r'(\d+)\/\/(\d+)='
    aligner = TMAligner()
    generator = DivSeqGenerator()
    min_n_digit = 1
    max_n_digit = 10
    raw_f = raw_test_target_file_template.format(min=min_n_digit, max=max_n_digit)
    with open(raw_f, 'r') as f:
        for line in f:
            sample = json.loads(line)
            raw_input = sample['prompt']
            match = re.search(pattern, raw_input)
            if match:
                op1, op2 = match.groups()
                op1, op2 = int(op1), int(op2)
                tm_input = aligner.input_to_tm(raw_input)
                raw_output = raw_input + str(op1 // op2)
                seq = generator.generate_with_op(op1, op2, only_input_output=True)
                tm_output  = seq[-1]
                executor_samples.append((tm_input, tm_output))
                aligner_input_samples.append((raw_input, tm_input))
                aligner_output_samples.append((tm_output, raw_output))
            else:
                raise ValueError(f'Invalid input: {raw_input}')
    write_jsonl_samples(executor_samples, test_target_file_template.format(min=min_n_digit, max=max_n_digit, prefix='execute_', suffix='_executor'))
    write_jsonl_samples(aligner_input_samples, test_target_file_template.format(min=min_n_digit, max=max_n_digit, prefix='execute_', suffix='_aligner_input'))
    write_jsonl_samples(aligner_output_samples, test_target_file_template.format(min=min_n_digit, max=max_n_digit, prefix='execute_', suffix='_aligner_output'))

def generate_test(args):
    if args.setting == 'separate':
        raw_to_tm()
        return
    
    generator = DivSeqGenerator()
    porportioner = Proportioner(
        minimal=args.min,
        maximal=args.max,
        num=args.num,
        task='div',
        option='balance'
    )
    samples = []
    aligner = TMAligner()

    if args.setting == 'raw':
        for b_n_digits in range(args.min, args.max + 1):
            a_n_digits = b_n_digits
            num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
            for _ in range(num):
                sample = generate_sample_test(generator, aligner, a_n_digits, b_n_digits, args)
                if sample:
                    samples.extend(sample)
    else:
        for a_n_digits in range(args.min, args.max + 1):
            for b_n_digits in range(args.min, args.max + 1):
                num = porportioner.get_num(a_n_digits=a_n_digits, b_n_digits=b_n_digits)
                for _ in range(num):
                    sample = generate_sample_test(generator, aligner, a_n_digits, b_n_digits, args)
                    if sample:
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