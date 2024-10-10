from transformers import AutoTokenizer, LlamaForCausalLM
from peft import PeftModel
import torch

base_model_3_path = ''
base_model_31_path = ''

task_requirements = {
    'add': None,
    'reflection': None,
    'left_mask': None,
    'sub': ['add', 'reflection', 'left_mask'],
    'equal': None,
    'greater_than': None,
    'less_than': None,
    'mul': ['add', 'less_than'],
    'div': ['add', 'greater_than'],
}

def load_adapters(model, tasks, path_provider, no_prompt, loaded):
    for task in tasks:
        if task in loaded:
            continue
        # load executor
        path = path_provider.get_path(task)
        operator_path = path.lora_path_no_prompt if no_prompt else path.lora_path
        if isinstance(model, PeftModel):
            model.load_adapter(
                model_id=operator_path,
                adapter_name=task,
                is_trainable=False,
            )
        else:
            model = PeftModel.from_pretrained(
                model,
                model_id=operator_path,
                adapter_name=task,
                torch_dtype=torch.bfloat16,
                is_trainable=False,
                attn_implementation="flash_attention_2",
            )
        # load aligner
        try:
            aligner_path = path.aligner_path
            if aligner_path:
                model.load_adapter(
                    model_id=aligner_path,
                    adapter_name=task + '_aligner',
                    is_trainable=False,
                )
        except:
            pass
        print(f'Loaded adapter {task}: {operator_path}')
        loaded.add(task)
        # load requirements
        requirements = task_requirements[task]
        if requirements:
            model = load_adapters(model, requirements, path_provider, no_prompt, loaded)

    return model
    

def get_model_and_tokenizer(task, path_provider, no_prompt):
    base_model_path = path_provider.get_base_model_path()

    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = LlamaForCausalLM.from_pretrained(base_model_path,
                                                device_map="auto",
                                                torch_dtype=torch.bfloat16,
                                                attn_implementation="flash_attention_2")
    
    model = load_adapters(model, [task], path_provider, no_prompt, set())
    model.set_adapter(task)

    return model, tokenizer

def get_task_path(args, path_provider):
    path_set = path_provider.get_path(args.task)
    if args.alignment:
        return path_set.task_path_raw
    if args.execute:
        return path_set.task_path_executor
    if args.aligner_input:
        return path_set.aligner_input_path
    if args.aligner_output:
        return path_set.aligner_output_path
    if args.no_prompt:
        task_path = path_set.task_path_no_prompt
    else:
        task_path = path_set.task_path
    return task_path

def load_datasets(task_paths, max_sample=1000000):
    lines = []
    for task_path in task_paths:
        print(f'Task path = {task_path}')
        with open(task_path, 'r') as f:
            lines.extend(f.readlines())
    return lines[:max_sample]
