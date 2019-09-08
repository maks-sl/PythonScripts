from datetime import datetime
import os
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME, OUTPUT_FILENAME, DLM = 'test_input.txt', 'output.txt', ' '


def make_abs_path(filename):
    return os.path.join(CURRENT_PATH, filename)


def print_time(header='TIMING'):
    print(str(header)+' : ' + str(f"{datetime.now():%Y-%m-%d %H:%M:%S}"))


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

    with open(make_abs_path(OUTPUT_FILENAME), 'w') as target:

        for row in input_items:
            parts = row.split()
            # p_code        old     new
            # S31236        29700   23760
            out_items += ["update store_products set "
                          "price_old = {1}, price_new = {2} "
                          "where p_code = '{0}';".format(*parts)]

        target.write('\n'.join(out_items))
    print_time('WRITE FILE DONE')

    print('EXEC TIME: ' + str(datetime.now() - start_time))
