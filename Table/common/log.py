from inspect import currentframe, getframeinfo


def debug_log(info: str):
    frame = getframeinfo(currentframe().f_back)
    print(f'{info} - {frame.filename}:{frame.lineno}')


def info_log(info: str):
    print(info)
