import json
import random
import os

from data.generator import LeftMaskSeqGenerator

train_target_file_template = 'datasets/train/left_mask{suffix}.json'
test_target_file_template = 'datasets/test/left_mask_{min}_{max}{suffix}.jsonl'

LEFT_MASK_PROMPT = """The following is a state paired with a command to be executed of a Turing Machine that performs left mask.

Left mask is a operation that removes the highest digit of the operand and writes the remaining digits to the output tape. Note that after removing the highest digit, if there are leading zeros, they should be removed as well.

The state includes the current operator, the current state of the machine, the current tape contents, and the current head positions.
- There are four states in the machine: q0, q1, q2, and qH. The machine starts in state q0 and halts when it reaches state qH. q1 is the state where the machine does copying or masking operation according to the current head position. q2 is the state where the machine removes the leading zeros. 
- The head position is represented by [HEAD], which indicate the position of the head on the operand. 
- The output position is represented by [OUTPUT].

The command includes a series of actions to be executed by the machine and they are separated by commas.
- [OUTPUT] <number>: Write the number to the output position.
- [OUTPUT] <direction>: Move the output head to the direction.
- [HEAD] <direction>: Move the head on the second operand to the direction.
- <state>: Move the machine to the state.

The machine performs left mask operation by copying the digits to the output tape and masking the last digit.

Based the current state and the command, predict the next state of the machine and next command to be executed.

"""

def seq_2_samples(seq, args):
    samples = []
    for i in range(len(seq) - 1):
        input = '' if args.no_prompt else LEFT_MASK_PROMPT
        input += seq[i][0] + '\n' + seq[i][1] + '\n'
        output = seq[i + 1][0] + '\n' + seq[i + 1][1] + '\n'
        samples.append((input, output))
    if len(samples) <= 5:
        return samples
    else:
        trancated_samples = [samples[0], samples[-1]]
        for i in range(1, 4):
            trancated_samples.append(samples[random.randint(1, len(samples) - 2)])
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

def generate_train(args):
    generator = LeftMaskSeqGenerator()
    samples = []
    for n_digits in range(args.min, args.max + 1):
        for _ in range(args.num // 2):
            seq = generator.generate(n_digits)
            samples.extend(seq_2_samples(seq, args))
            seq = generator.generate(n_digits, leading_zero=True)
            samples.extend(seq_2_samples(seq, args))

    train_target_file = train_target_file_template.format(suffix='_no_prompt' if args.no_prompt else '')
    write_json_samples(samples, train_target_file)

def generate_test(args):
    generator = LeftMaskSeqGenerator()
    samples = []
    for n_digits in range(args.min, args.max + 1):
        for _ in range(args.num // 2):
            seq = generator.generate(n_digits)
            samples.extend(seq_2_samples(seq, args))
            seq = generator.generate(n_digits, leading_zero=True)
            samples.extend(seq_2_samples(seq, args))

    test_target_file = test_target_file_template.format(
        min=args.min, max=args.max, suffix='_no_prompt' if args.no_prompt else '')
    write_jsonl_samples(samples, test_target_file)

def generate(args):
    if args.split == 'train':
        random.seed(42)
        generate_train(args)
    elif args.split == 'test':
        random.seed(43)
        generate_test(args)
