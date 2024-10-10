# Executing Arithmetic: Fine-Tuning Large Language Models as Turing Machines

This repository contains the implementation for the paper *"Executing Arithmetic: Fine-Tuning Large Language Models as Turing Machines"*.

## Directory Structure

- `arithmetic`: Execution structure for each arithmetic operator.
- `data`: Generates individual samples for each operator.
- `eval`: Evaluation logic.
- `synthetic`: Scripts to generate datasets for training and testing.
- `turing_machine`: Turing machine prototype implementation for each operator.

## Usage

### Preparation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Download the LoRA adapters and evaluation datasets from our [HuggingFace page](https://huggingface.co/NJUDeepEngine/CAEF_llama3.1_8b):
```bash
python download.py
```

3. Update the paths in the following files to match your local setup:
   - `turing_machine/tm_path.py`
   - `utils.py`

Example:
```python
base_model_3_path = "/model/meta-llama/Meta-Llama-3-8B/"
base_model_31_path = "/model/meta-llama/Meta-Llama-3.1-8B/"

add = dict(
    lora_path = '',                                  # optional, for testing first-stage executor
    lora_path_no_prompt = 'ckpt/executors/addition',  # LoRA path of the executor
    aligner_path = 'ckpt/aligners/addition',          # LoRA path of the aligner
    task_path = '',                                  # optional, for testing first-stage executor
    task_path_no_prompt = '',                        # optional, executor for one-step transition
    task_path_executor = '',                         # optional, executor for full process
    task_path_raw = 'datasets/raw/addition/test_5_5.jsonl',  # for testing whole process
    aligner_input_path = '',                         # optional, for testing aligner input
    aligner_output_path = '',                        # optional, for testing aligner output
)
```

4. (Optional) Generate separate test sets for executors and aligners:
```bash
python generate.py --task add --split test --setting separate
```
Then, configure `task_path_executor`, `aligner_input_path`, and `aligner_output_path` in `turing_machine/tm_path.py`.

### Evaluation

#### Full Process (Addition Example)

To evaluate the complete process:
```bash
python eval_tm.py --model 3.1 --task add --batch_size 64 --no_prompt --execute --alignment
```

#### Executor-Only Evaluation

To evaluate only the executors:
```bash
python eval_tm.py --model 3.1 --task add --batch_size 64 --no_prompt --execute
```

#### Aligner-Only Evaluation

To evaluate only the aligners (input or output):
```bash
# input evaluation
python eval_tm.py --model 3.1 --task add --batch_size 64 --no_prompt --aligner_input

# output evaluation
python eval_tm.py --model 3.1 --task add --batch_size 64 --no_prompt --aligner_output
```

You can modify the `task` and `batch_size` parameters as needed.

### Training

If you want to train executors or aligners on your own, follow the instructions below to generate the necessary training data. Both JSON and JSONL formats are supported. Check the files in the `synthetic` directory for examples.

#### For Executors:

1. First stage:
```bash
python generate.py --task add --min 1 --max 100 --num 20 --split train --setting execute
```

2. Second stage:
```bash
python generate.py --task add --min 1 --max 100 --num 20 --split train --no_prompt --setting execute
```

#### For Aligners:

1. First stage:
```bash
python generate.py --task add --min 1 --max 100 --num 20 --split train --setting alignment
```

2. Second stage:
```bash
python generate.py --task add --min 1 --max 100 --num 20 --split train --no_prompt --setting alignment
```

The expressions are divided into equivalence classes based on the pair `(len(a), len(b))`. The `min` and `max` parameters refer to the minimum and maximum length of the operands, respectively. The `num` parameter defines how many expressions will be generated per class, though the actual number may vary based on sampling and balancing strategies.