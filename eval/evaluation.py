import re
import json

def extract_answer(input, output):
    output = output.replace(input, '')
    return output

def do_eval_one_step(outputs, ground_truths, prompts, task, aligner):
    assert len(outputs) == len(ground_truths)
    correct = 0
    for i, output in enumerate(outputs):
        output = output.strip()
        ground_truths[i] = ground_truths[i].strip()
        if output == ground_truths[i]:
            correct += 1
        else:
            pass
    acc = correct / len(outputs)
    print('accuracy = ', acc)
    return acc

def do_eval_iter(outputs, ground_truths, prompts, task, alignment):
    if alignment:
        for i in range(len(ground_truths)):
            ground_truths[i] = prompts[i] + ground_truths[i]
    assert len(outputs) == len(ground_truths)
    correct = 0
    for i, output in enumerate(outputs):
        output = output.strip()
        ground_truths[i] = ground_truths[i].strip()
        if output == ground_truths[i]:
            correct += 1
        else:
            pass
    acc = correct / len(outputs)
    print('Accuracy = ', acc)
    return acc