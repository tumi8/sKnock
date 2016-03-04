import logging
from benchmarks import *

# TODO: class for handling all benchmarks


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    ap_firewall.benchmark()