import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
from tqdm import tqdm
import argparse
import json
import torch

from eval.evaluation import extract_answer, do_eval_one_step, do_eval_iter
from arithmetic.llm_arithmetic_batch import llm_execute_batch
from turing_machine.tm_path import PathProvider
from utils import get_model_and_tokenizer, get_task_path, load_datasets

torch.manual_seed(42)
torch.cuda.random.manual_seed(42)

legal_tasks = ['add', 'reflection', 'left_mask', 'sub', 'equal', 'greater_than', 'less_than', 'mul', 'div']

def eval_one_step(model, tokenizer, batch_size, task_path, task, aligner):
    prompts = []
    model_responses = []
    ground_truths = []
    cnt = 0
    batch = []

    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )

    if aligner:
        model.set_adapter(f'{task}_aligner')

    lines = load_datasets([task_path])
    pbar = tqdm(lines, total=len(lines))

    for line in pbar:
        sample = json.loads(line)
        prompt = sample['prompt']
        batch.append(prompt)
        prompts.append(prompt)
        ground_truths.append(sample['response']) 
        cnt += 1

        if cnt % batch_size == 0:
            with torch.no_grad():
                inputs = tokenizer(batch, return_tensors="pt", padding=True).to("cuda")
                outputs = model.generate(
                    **inputs,
                    **gen_kwargs,
                )
            for i, output in enumerate(outputs):
                model_response = extract_answer(batch[i],
                                                    tokenizer.decode(output, skip_special_tokens=True))
                model_responses.append(model_response)
            # reset batch
            batch = []

            interval = 100
            prev = (cnt - batch_size) // interval
            cur = cnt // interval
            if cur > prev:
                num = interval * cur
                cur_model_responses = model_responses[:num]
                cur_ground_truths = ground_truths[:num]
                cur_prompts = prompts[:num]
                print(f'{num} samples result:')
                do_eval_one_step(cur_model_responses, cur_ground_truths, cur_prompts, task, aligner)
                print('\n')
        
    # last batch
    if len(batch) > 0:
        with torch.no_grad():
            inputs = tokenizer(batch, return_tensors="pt", padding=True).to("cuda")
            outputs = model.generate(
                **inputs,
                **gen_kwargs,
            )
        for i, output in enumerate(outputs):
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))                 
            model_responses.append(model_response)

    result = {}
    print('Final result:')
    result['eval_result'] = do_eval_one_step(model_responses, ground_truths, prompts, task, aligner)
    result['num_samples'] = len(model_responses)

    with open('log/one_step_result.log', 'w') as f:
        f.write(f'task path: {task_path}\n')
        f.write(f'samples num: {result["num_samples"]}\n')
        f.write(f'accuarcy: {result["eval_result"]}\n')

    return result

def eval_iter(model, tokenizer, batch_size, task_path, task, alignment):
    prompts = []
    model_responses = []
    ground_truths = []
    cnt = 0
    batch = []

    lines = load_datasets([task_path])
    pbar = tqdm(lines, total=len(lines))

    for line in pbar:
        sample = json.loads(line)
        prompt = sample['prompt']
        batch.append(prompt)
        prompts.append(prompt)
        ground_truths.append(sample['response']) 
        cnt += 1

        if cnt % batch_size == 0:
            batch_model_responses, _ = llm_execute_batch(model, tokenizer, batch, task, alignment)
            model_responses.extend(batch_model_responses)

            batch = []

            interval = 100
            prev = (cnt - batch_size) // interval
            cur = cnt // interval
            if cur > prev:
                num = interval * cur
                cur_model_responses = model_responses[:num]
                cur_ground_truths = ground_truths[:num]
                cur_prompts = prompts[:num]
                print(f'{num} samples result:')
                do_eval_iter(cur_model_responses, cur_ground_truths, cur_prompts, task, alignment)
                print('\n')
    
    # last batch
    if len(batch) > 0:
        batch_model_responses, _ = llm_execute_batch(model, tokenizer, batch, task, alignment)
        model_responses.extend(batch_model_responses)

    result = {}
    print('Final result:')
    result['eval_result'] = do_eval_iter(model_responses, ground_truths, prompts, task, alignment)
    result['num_samples'] = len(model_responses)

    with open('log/iter_result.log', 'w') as f:
        f.write(f'task path: {task_path}\n')
        f.write(f'samples num: {result["num_samples"]}\n')
        f.write(f'accuarcy: {result["eval_result"]}\n')

    return result


def eval_model(args, model, tokenizer, path_provider):
    task_path = get_task_path(args, path_provider)
    if args.execute:
        return eval_iter(model, tokenizer, args.batch_size, task_path, args.task, args.alignment)
    else:
        aligner = args.aligner_input or args.aligner_output
        return eval_one_step(model, tokenizer, args.batch_size, task_path, args.task, aligner)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--model', type=str, required=True, choices=['3', '3.1'])
    argparser.add_argument('--batch_size', default=32, type=int, required=False)
    argparser.add_argument('--task', type=str, choices=legal_tasks, required=True)
    argparser.add_argument('--no_prompt', action='store_true', required=False)
    argparser.add_argument('--execute', action='store_true', required=False)
    argparser.add_argument('--alignment', action='store_true', required=False)
    argparser.add_argument('--aligner_input', action='store_true', required=False)
    argparser.add_argument('--aligner_output', action='store_true', required=False)
    args = argparser.parse_args()

    path_provider = PathProvider(args.model)
    model, tokenizer = get_model_and_tokenizer(args.task, path_provider, args.no_prompt)
    model.generation_config.temperature=None
    model.generation_config.top_p=None

    result = eval_model(args, model, tokenizer, path_provider)