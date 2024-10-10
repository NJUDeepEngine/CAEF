import json
import random
import os

from data.generator import ReflectionSeqGenerator


train_target_file_template = 'datasets/train/tm_reflection{suffix}.json'
test_target_file_template = 'datasets/test/tm_reflection_{min}_{max}{suffix}.jsonl'

REFLECTION_PROMPT = """The following is a state paired with a command to be executed of a Turing Machine that performs reflection.

The state includes the current operator, the current state of the machine, the current tape contents, and the current head positions.
- There are three states in the machine: q0, q1, q2 and qH. The machine starts in state q0 and halts when it reaches state qH. q1 is the state where the machine does the reflection operation. q2 is the state where the machine removes the leading zeros from the output tape.
- The head positions are represented by [HEAD1] and [HEAD2], which indicate the positions of the heads on the two operands. 
- The output position is represented by [OUTPUT].

The command includes a series of actions to be executed by the machine and they are separated by commas.
- [OUTPUT] <number>: Write the number to the output position.
- [OUTPUT] <direction>: Move the output head to the direction.
- [HEAD1] <direction>: Move the head on the first operand to the direction.
- [HEAD2] <direction>: Move the head on the second operand to the direction.
- <state>: Move the machine to the state.

The machine performs reflection by reading the digits from the two operands and writing the subtrction result to the output tape. 

Based on the current state and the command, predict the next state of the machine and next command to be executed.

"""

def seq_2_samples(seq, args):
    samples = []
    for i in range(len(seq) - 1):
        input = '' if args.no_prompt else REFLECTION_PROMPT
        input += seq[i][0] + '\n' + seq[i][1] + '\n'
        output = seq[i + 1][0] + '\n' + seq[i + 1][1] + '\n'
        samples.append((input, output))
    if len(samples) <= 10:
        return samples
    else:
        trancated_samples = [samples[0], samples[-1]]
        for i in range(len(samples)):
            if 'CMD q2' in samples[i][1]:
                idx = i
                break
        trancated_samples.append(samples[idx]) # q1 -> q2
        trancated_samples.append(samples[idx + 1]) # q2 -> q2/qH
        for i in range(1, 5):
            trancated_samples.append(samples[random.randint(1, idx - 1)])
        if idx + 2 != len(samples) - 1:
            for _ in range(1, 4):
                trancated_samples.append(samples[random.randint(idx + 2, len(samples) - 2)])
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
    generator = ReflectionSeqGenerator()
    samples = []
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, a_n_digits + 1):
            num = args.num * 2 if a_n_digits == b_n_digits else args.num
            for i in range(num):
                seq = generator.generate(a_n_digits, b_n_digits)
                samples.extend(seq_2_samples(seq, args))
                if a_n_digits == b_n_digits and i % 2 == 0:
                    seq = generator.generate_leading_zero(a_n_digits, b_n_digits)
                    samples.extend(seq_2_samples(seq, args))
    train_target_file = train_target_file_template.format(suffix='_no_prompt' if args.no_prompt else '')
    write_json_samples(samples, train_target_file)

def generate_test(args):
    generator = ReflectionSeqGenerator()
    samples = []
    for a_n_digits in range(args.min, args.max + 1):
        for b_n_digits in range(args.min, a_n_digits + 1):
            for _ in range(args.num):
                seq = generator.generate(a_n_digits, b_n_digits)
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