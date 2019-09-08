import random
from datetime import datetime
import os
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME, OUTPUT_FILENAME, DLM = 'test_input.txt', 'output.txt', ':'


def gen_variants(input_string):
    cleaned, result = input_string.strip(), []
    if cleaned.count(DLM) > 0:
        login, password = cleaned.split(DLM, 1)
        if bool(login) and bool(password):
            result.append(cleaned)
            if not password[0].isdigit():
                result.append(DLM.join([login, password[0].swapcase()+password[1:]]))
            if not password[-1].isdigit():
                result.append(DLM.join([login, password[:-1]+password[-1].swapcase()]))
            for end_by in ['1', '!', '*']:
                result.append(DLM.join([login, password + end_by]))
    return result


def make_abs_path(filename):
    return os.path.join(CURRENT_PATH, filename)


def print_time(header='TIMING'):
    print(str(header)+' : ' + str(f"{datetime.now():%Y-%m-%d_%H-%M-%S}"))


def file_to_list(filename):
    try:
        with open(make_abs_path(filename)) as file:
            result = file.readlines()
    except UnicodeDecodeError:
        with open(make_abs_path(filename), encoding="ISO-8859-1") as file:
            result = file.readlines()
    return result


if __name__ == "__main__":
    print(CURRENT_PATH)
    start_time, out_items = datetime.now(), []
    print_time('START')

    input_items = file_to_list(INPUT_FILENAME)
    print_time('FILE READ DONE')

    while len(input_items) > 0:
        string = input_items.pop()
        variants = gen_variants(string)
        out_items += variants
    print_time('VARIANTS LIST DONE')

    random.shuffle(out_items)
    print_time('RANDOM DONE')

    with open(make_abs_path(OUTPUT_FILENAME), 'w') as target:
        target.write('\n'.join(out_items)) 
    print_time('WRITE FILE DONE')

    print('EXEC TIME: ' + str(datetime.now() - start_time))
