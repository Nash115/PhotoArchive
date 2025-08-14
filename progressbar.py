class ProgressBar:
    def __init__(self, max=100, start_value=0, bar_length=40) -> None:
        self.max = max
        self.value = start_value
        self.bar_length = bar_length

    def __repr__(self) -> str:
        if self.max <= 0:
            return "Progress bar not initialized properly."
        val = min(max(self.value, 0), self.max)
        filled_length = int(self.bar_length * val // self.max)
        bar = '#' * filled_length + '-' * (self.bar_length - filled_length)
        percent = round((val / self.max) * 100, 2)
        return f"\r[{bar}] {val}/{self.max} ({percent}%)"

    def afficher(self) -> None:
        print(self, end="", flush=True)
        if self.value >= self.max:
            self.end()

    def update(self, value) -> None:
        self.value = value
        self.afficher()

    def end(self) -> None:
        print(" done !")