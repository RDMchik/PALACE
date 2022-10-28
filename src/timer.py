import time


class Timer:

    def __init__(self, lenght: any) -> None:

        self.length = lenght
        self.start = time.time()

    @property
    def done(self) -> bool:
        if self.length + self.start <= time.time():
            return True
        return False