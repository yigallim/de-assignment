import time

class ProgressTracker:
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.last_percentage = 0
        self.start_time = time.time()
        print()

    def update(self):
        self.current_step += 1
        percentage = int((self.current_step / self.total_steps) * 100)
        elapsed_time = time.time() - self.start_time
        estimated_total_time = elapsed_time / self.current_step * self.total_steps
        estimated_remaining_time = estimated_total_time - elapsed_time

        if percentage > self.last_percentage:
            self.last_percentage = percentage
            self.print_progress(percentage, elapsed_time, estimated_remaining_time)

    @staticmethod
    def format_time(seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}m {secs}s"

    def print_progress(self, percentage, elapsed_time, remaining_time):
        bar_length = 50
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        elapsed_time_str = self.format_time(elapsed_time)
        remaining_time_str = self.format_time(remaining_time)
        print(
            f"\r|{bar}| {percentage}% Elapsed: {elapsed_time_str} ETA: {remaining_time_str}",
            end='', flush=True
        )

    def complete(self):
        self.print_progress(100, time.time() - self.start_time, 0)
        print("\n")