from torch import cuda
import os

def get_device():
    return f'cuda:{cuda.current_device()}' if os.environ['CURRENT_DEVICE']=='GPU' else 'cpu'