import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILENAME = os.path.join(CURRENT_PATH, 'out-fast.txt')

WRITE_TO_FILE_EVERY = 1000000

D_START = 1
D_END = 100000000
D_STEP = 1
FILE_SIZE_RATIO = 0.21 / 10000000


def format_line(value):
    return '0.'+str(value).zfill(17)

if __name__ == "__main__":

    fast_range = range(D_START, D_END, D_STEP)
    cnt_lines = (D_END - D_START) / D_STEP + 1

    file_size = cnt_lines * FILE_SIZE_RATIO
    print('File length ' + str(len(fast_range)) + ' lines, ', end=' ')
    print(f'{file_size:.2f}' + ' GB will be used!')

    iterator = iter(fast_range)
    counter = 0
    out = []
    with open(OUTPUT_FILENAME, 'w') as w:

        while True:
            try:
                if counter >= WRITE_TO_FILE_EVERY:
                    w.write('\n'.join(out) + '\n')
                    out = []
                    counter = 0
                    print(format_line(current))

                current = next(iterator)
                counter += 1
                out.append(format_line(current))

            except StopIteration:
                if len(out):
                    w.write('\n'.join(out) + '\n')
                    out = []
                break
