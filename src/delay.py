
import time


def wait_for(seconds: int) -> None:
    if seconds == 0:
        return

    print_progress_bar(0, seconds,
                       prefix="Delay for Internet Archive:",
                       suffix="",
                       length=50)

    for i in range(seconds+1):
        time.sleep(1.0)
        print_progress_bar(i, seconds,
                           prefix="Delay for Internet Archive:",
                           suffix="",
                           length=50)


def print_progress_bar(iteration: int, total: int,
                       prefix: str = '', suffix: str = '',
                       decimals: int = 1, length: int = 100, fill: str = '█',
                       printEnd: str = "\r") -> None:
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
