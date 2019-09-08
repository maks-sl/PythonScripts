import os
import numpy as np
import math

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILENAME = os.path.join(CURRENT_PATH, 'out.txt')

WRITE_TO_FILE_EVERY = 1000000

D_START = 0.00000000000000001
D_END =   0.00000000099999999
D_STEP =  0.00000000000000001
FILE_SIZE_RATIO = 0.21 / 10000000


class NpRange:

    class _NpRangeIterator:
        def __init__(self, range_instance):
            self.range = range_instance
            self.next_value = range_instance.start

        def __iter__(self):
            return self

        def __next__(self):
            if np.greater(self.next_value, np.add(self.range.end, self.range.step)):
                raise StopIteration

            result = self.next_value
            self.next_value = np.add(self.next_value, self.range.step)

            return result

    def __init__(self, start, end, step):
        self.start, self.end, self.step = np.float64(start), np.float64(end), np.float64(step)
        self.length = math.ceil(np.ceil(np.true_divide(np.subtract(self.end, self.start), self.step)).item()) + 1

    def __iter__(self):
        return self._NpRangeIterator(self)


def format_line(np_value):
    return f'{np_value:.17f}'

if __name__ == "__main__":

    np_range = NpRange(D_START, D_END, D_STEP)
    file_size = np_range.length * FILE_SIZE_RATIO
    print('File length ' + str(np_range.length) + ' lines, ', end=' ')
    print(f'{file_size:.2f}' + ' GB will be used!')

    iterator = iter(np_range)
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
