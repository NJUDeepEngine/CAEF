import re
from eval.evaluation import extract_answer
from turing_machine.addition.addition_tm import AdditionTMChecker
from turing_machine.reflection.reflection_tm import ReflectionTMChecker
from turing_machine.left_mask.left_mask_tm import LeftMaskTMChecker
from turing_machine.subtraction.sub_tm import SubtractionTMChecker
from turing_machine.equal.equal_tm import EqualTMChecker
from turing_machine.greater_than.greater_than_tm import GreaterThanTMChecker
from turing_machine.less_than.less_than_tm import LessThanTMChecker
from turing_machine.multiplication.mul_tm import MultiplicationTMChecker
from turing_machine.division.div_tm import DivisionTMChecker
from turing_machine.alignment.aligner import TMAligner

HALT_OUTPUT = """No command to execute. Halt state."""
CALL_PATTERN = r'\bCMD\s\[CALL\]\s(.+),\s(.+)\b'
SUB_FINISH_PATTERN = r'SUB, qH,'
MUL_FINISH_PATTERN = r'MUL, qH,'
DIV_FINISH_PATTERN = r'DIV, qH,'

def _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished):
    assert len(batch) == len(corrects) == len(finished)
    # skip error or finished
    skips = [not correct or finish for correct, finish in zip(corrects, finished)]
    # filter out correct answers
    skip_indices = [i for i, skip in enumerate(skips) if skip]
    reserve_indices = [i for i, skip in enumerate(skips) if not skip]
    filtered_batch = [batch[i] for i in reserve_indices]
    assert len(filtered_batch) != 0
    # generate
    inputs = tokenizer(filtered_batch, return_tensors="pt", padding=True).to("cuda")
    outputs = model.generate(
        **inputs,
        **gen_kwargs,
    )
    # restore batch
    results = [None] * len(batch)
    for i, idx in enumerate(reserve_indices):
        results[idx] = outputs[i]
    for idx in skip_indices:
        results[idx] = batch[idx] # copy original input
    return results

def _check_finished(batch, corrects, finished):
    # any correct answer is halt state, set True in `finished`
    for i in range(len(batch)): 
        if corrects[i] and batch[i].find(HALT_OUTPUT) != -1:
            finished[i] = True
    return finished

def _check_stop(batch, corrects, finished):
    # if no correct answer exists, stop
    if not any(corrects): 
        return True
    # if all samples finished, stop
    if all(finished):
        return True
    return False

def _pre_align_batch(model, tokenizer, task, batch, corrects=None):
    model.set_adapter(f'{task}_aligner')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    results = [''] * len(batch)
    if not corrects:
        corrects = [True] * len(batch)
    finished = [not correct for correct in corrects]
    outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)
    adapter = TMAligner()
    for i, output in enumerate(outputs):
        if not corrects[i] or finished[i]:
            continue
        model_response = extract_answer(batch[i],
                                            tokenizer.decode(output, skip_special_tokens=True))
        ground_truth = adapter.input_to_tm(batch[i])
        if model_response.strip() != ground_truth.strip():
            corrects[i] = False
            results[i] = batch[i] + '\n\n' + model_response
        else:
            results[i] = model_response

    return results, corrects

def _post_align_batch(model, tokenizer, task, batch, corrects=None, finished=None):
    model.set_adapter(f'{task}_aligner')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    results = [''] * len(batch)
    if not corrects:
        corrects = [True] * len(batch)
    finished = [not correct for correct in corrects]
    outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)
    for i, output in enumerate(outputs):
        if not corrects[i] or finished[i]:
            continue
        model_response = extract_answer(batch[i],
                                            tokenizer.decode(output, skip_special_tokens=True))
        results[i] = model_response
            
    return results, corrects

def llm_add_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('add')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    new_finished = [not correct for correct in corrects]
    if finished:
        for i in range(len(finished)):
            if finished[i]:
                new_finished[i] = True
    finished = new_finished
    checkers = [AdditionTMChecker(input) if (corrects[i] and not finished[i]) else None for i, input in enumerate(batch)]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects


def llm_reflection_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('reflection')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [ReflectionTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects


def llm_left_mask_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('left_mask')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [LeftMaskTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects

def llm_equal_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('equal')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [EqualTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects

def llm_greater_than_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('greater_than')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    new_finished = [not correct for correct in corrects]
    if finished:
        for i in range(len(finished)):
            if finished[i]:
                new_finished[i] = True
    finished = new_finished
    checkers = [GreaterThanTMChecker(input) if (corrects[i] and not finished[i]) else None for i, input in enumerate(batch)]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects

def llm_less_than_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('less_than')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    # checkers = [LessThanTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    # finished = [not correct for correct in corrects]
    new_finished = [not correct for correct in corrects]
    if finished:
        for i in range(len(finished)):
            if finished[i]:
                new_finished[i] = True
    finished = new_finished
    checkers = [LessThanTMChecker(input) if (corrects[i] and not finished[i]) else None for i, input in enumerate(batch)]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += model_response
            results[i] = model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
            else:
                checker.one_step()
            batch[i] = model_response

        finished = _check_finished(batch, corrects, finished)

    return results, corrects

op_2_func = {
    'add': llm_add_batch,
    'reflection': llm_reflection_batch,
    'left_mask': llm_left_mask_batch,
    'less_than': llm_less_than_batch,
    'greater_than': llm_greater_than_batch,
}

def _check_finished_sub(batch, corrects, finished):
    # any correct answer is halt state, set True in `finished`
    for i in range(len(batch)): 
        if corrects[i] and re.findall(SUB_FINISH_PATTERN, batch[i]):
            finished[i] = True
    return finished

def llm_sub_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('sub')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [SubtractionTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        # process model outputs
        inits = [''] * len(batch)
        func = None
        call_flag = False
        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            # call_flag = False
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += '\n' + model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
                continue
            else:
                checker.one_step()
            # check function call
            matches = re.findall(CALL_PATTERN, model_response)
            if matches:
                # prepare call
                call_op, _ = matches[0]
                call_op = call_op.lower()
                splits = model_response.split('\n')
                inits[i] = splits[2] + '\n' + splits[3] + '\n'
                func = op_2_func[call_op]
                call_flag = True
                batch[i] = splits[0] + '\n' + splits[1] + '\n'
            else:
                batch[i] = model_response

        finished = _check_finished_sub(batch, corrects, finished)

        if call_flag:
            call_responses, corrects = func(model, tokenizer, inits, corrects)
            model.set_adapter('sub')
            for i in range(len(batch)):
                batch[i] += call_responses[i]
                if not corrects[i]:
                    finished[i] = True
                    if len(call_responses[i]) > 0:
                        results[i] = call_responses[i]  

    for i, accumulate_output in enumerate(accumulate_outputs):
        if corrects[i]:
            results[i] = accumulate_output.split('\n')[-2]

    return results, corrects

def _check_finished_mul(batch, corrects, finished):
    # any correct answer is halt state, set True in `finished`
    for i in range(len(batch)): 
        if corrects[i] and re.findall(MUL_FINISH_PATTERN, batch[i]):
            finished[i] = True
    return finished

def llm_mul_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('mul')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [MultiplicationTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        # prepare for function call
        inits = [''] * len(batch)
        func = None
        call_flag = False
        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            # call_flag = False
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += '\n' + model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
                continue
            else:
                checker.one_step()
            # check function call
            matches = re.findall(CALL_PATTERN, model_response)
            if matches:
                # prepare call
                call_op, _ = matches[0]
                call_op = call_op.lower()
                splits = model_response.split('\n')
                inits[i] = splits[2] + '\n' + splits[3] + '\n'
                func = op_2_func[call_op]
                call_flag = True
                batch[i] = splits[0] + '\n' + splits[1] + '\n'
            else:
                batch[i] = model_response

        finished = _check_finished_mul(batch, corrects, finished)

        if call_flag:
            call_responses, corrects = func(model, tokenizer, inits, corrects, finished)
            model.set_adapter('mul')
            for i in range(len(batch)):
                batch[i] += call_responses[i]
                if not corrects[i]:
                    finished[i] = True
                    if len(call_responses[i]) > 0:
                        results[i] = call_responses[i]

    for i, accumulate_output in enumerate(accumulate_outputs):
        if corrects[i]:
            results[i] = accumulate_output.split('\n')[-2]

    return results, corrects

def _check_finished_div(batch, corrects, finished):
    # any correct answer is halt state, set True in `finished`
    for i in range(len(batch)): 
        if corrects[i] and re.findall(DIV_FINISH_PATTERN, batch[i]):
            finished[i] = True
    return finished

def llm_div_batch(model, tokenizer, batch, corrects=None, finished=None):
    model.set_adapter('div')
    gen_kwargs = dict(
        max_length=4096,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    accumulate_outputs = [''] * len(batch)
    results = [''] * len(batch) # status where the machine halts or error occurs
    corrects = [True] * len(batch) if corrects is None else corrects
    checkers = [DivisionTMChecker(input) if corrects[i] else None for i, input in enumerate(batch)]
    finished = [not correct for correct in corrects]
    step = 0

    while not _check_stop(batch, corrects, finished):
        step += 1
        outputs = _wrapper_generate(model, tokenizer, gen_kwargs, batch, corrects, finished)

        # prepare for function call
        inits = [''] * len(batch)
        func = None
        call_flag = False
        for i, output in enumerate(outputs):
            # skip if error has occurred or finished
            if not corrects[i] or finished[i]:
                continue
            # call_flag = False
            model_response = extract_answer(batch[i],
                                                tokenizer.decode(output, skip_special_tokens=True))
            accumulate_outputs[i] += '\n' + model_response
            # remove from batch if error occurs
            checker = checkers[i]
            if not checker.check(model_response):
                results[i] = batch[i] + '\n' + model_response
                corrects[i] = False
                finished[i] = True
                continue
            else:
                checker.one_step()
            # check function call
            matches = re.findall(CALL_PATTERN, model_response)
            if matches:
                # prepare call
                call_op, _ = matches[0]
                call_op = call_op.lower()
                splits = model_response.split('\n')
                inits[i] = splits[2] + '\n' + splits[3] + '\n'
                func = op_2_func[call_op]
                call_flag = True
                batch[i] = splits[0] + '\n' + splits[1] + '\n'
            else:
                batch[i] = model_response

        finished = _check_finished_div(batch, corrects, finished)

        if call_flag:
            call_responses, corrects = func(model, tokenizer, inits, corrects, finished)
            model.set_adapter('div')
            for i in range(len(batch)):
                batch[i] += call_responses[i]
                if not corrects[i]:
                    finished[i] = True
                    if len(call_responses[i]) > 0:
                        results[i] = call_responses[i]      

    for i, accumulate_output in enumerate(accumulate_outputs):
        if corrects[i]:
            results[i] = accumulate_output.split('\n')[-2]

    return results, corrects

def llm_execute_batch(model, tokenizer, batch, task, alignment):
    task_func_mapping = dict(
        add=llm_add_batch,
        reflection=llm_reflection_batch,
        left_mask=llm_left_mask_batch,
        sub=llm_sub_batch,
        equal=llm_equal_batch,
        greater_than=llm_greater_than_batch,
        less_than=llm_less_than_batch,
        mul=llm_mul_batch,
        div=llm_div_batch,
    )
    try:
        if alignment:
            pre_align_batch, corrects = _pre_align_batch(model, tokenizer, task, batch)
            func = task_func_mapping[task]
            executor_responses, corrects = func(model, tokenizer, pre_align_batch, corrects)
            # append halt output
            for i in range(len(executor_responses)):
                if corrects[i] and HALT_OUTPUT not in executor_responses[i]:
                    executor_responses[i] += '\n' + HALT_OUTPUT
            post_align_batch, corrects = _post_align_batch(model, tokenizer, task, executor_responses, corrects)
            # record error
            for i in range(len(batch)):
                post_align_batch[i] = executor_responses[i] if not post_align_batch[i] else post_align_batch[i]
                post_align_batch[i] = pre_align_batch[i] if not post_align_batch[i] else post_align_batch[i]
            return post_align_batch, corrects
        else:
            func = task_func_mapping[task]
            executor_responses, corrects = func(model, tokenizer, batch)
            return executor_responses, corrects
    except KeyError:
        raise ValueError(f'Invalid task: {task}')

