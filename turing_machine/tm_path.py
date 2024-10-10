import os

base_model_3_path = ''
base_model_31_path = ''

add = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

reflection = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

left_mask = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

sub = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

equal = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

greater_than = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

less_than = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

mul = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

div = dict(
    lora_path = '',
    lora_path_no_prompt = '',
    aligner_path = '',
    task_path = '',
    task_path_no_prompt = '',
    task_path_executor = '',
    task_path_raw = '',
    aligner_input_path = '',
    aligner_output_path = '',
)

class PathArtifact:
    def __init__(self, path_dict, model_version):
        self.lora_3_dir = ''
        self.lora_31_dir = ''
        self.task_dir = 'datasets'
        self.raw_dir = ''
        self.lora_dir = self.lora_3_dir if model_version == '3' else self.lora_31_dir

        self.lora_path = os.path.join(self.lora_dir, path_dict['lora_path'])
        self.lora_path_no_prompt = os.path.join(self.lora_dir, path_dict['lora_path_no_prompt'])
        self.aligner_path = os.path.join(self.lora_dir, path_dict['aligner_path'])
        self.task_path = os.path.join(self.task_dir, path_dict['task_path'])
        self.task_path_no_prompt = os.path.join(self.task_dir, path_dict['task_path_no_prompt'])
        self.task_path_executor = os.path.join(self.task_dir, path_dict['task_path_executor'])
        self.task_path_raw = os.path.join(self.raw_dir, path_dict['task_path_raw'])
        self.aligner_input_path = os.path.join(self.task_dir, path_dict['aligner_input_path'])
        self.aligner_output_path = os.path.join(self.task_dir, path_dict['aligner_output_path'])

class PathProvider:
    def __init__(self, model_version):
        self.path_dict = dict(
            add=PathArtifact(add, model_version),
            reflection=PathArtifact(reflection, model_version),
            left_mask=PathArtifact(left_mask, model_version),
            sub=PathArtifact(sub, model_version),
            equal=PathArtifact(equal, model_version),
            greater_than=PathArtifact(greater_than, model_version),
            less_than=PathArtifact(less_than, model_version),
            mul=PathArtifact(mul, model_version),
            div=PathArtifact(div, model_version),
        )
        self.base_model_path = base_model_3_path if model_version == '3' else base_model_31_path

    def get_legal_task(self):
        return list(self.path_dict.keys())

    def get_path(self, task) -> PathArtifact:
        if task not in self.path_dict:
            raise ValueError(f'Invalid task: {task}')
        return self.path_dict[task]
    
    def get_base_model_path(self):
        return self.base_model_path