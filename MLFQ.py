from collections import deque

class MLFQ:
    def __init__(self, levels):
        self.levels = levels
        self.queues = [deque() for _ in range(levels)]
        self.time = 0
        self.total_waiting_time = 0
        self.total_turnaround_time = 0
        self.total_response_time = 0
        self.max_turnaround_time = 0
        self.worst_case_execution_time = 0

    def add_task(self, task):
        self.queues[0].append(task)

    def get_next_task(self):
        for i in range(self.levels):
            if self.queues[i]:
                task = self.queues[i].popleft()
                return task
        return None

    def run(self, steps):
        for _ in range(steps):
            task = self.get_next_task()
            if task:
                if task.start_time is None:
                    task.set_start_time(self.time)
                    self.total_response_time += task.response_time()
                    self.total_waiting_time += task.waiting_time()
                task.remaining_time -= 1
                self.time += 1
                if task.remaining_time <= 0:
                    task.set_finish_time(self.time)
                    self.total_turnaround_time += task.turnaround_time()
                    self.max_turnaround_time = max(self.max_turnaround_time, task.turnaround_time())
                    self.worst_case_execution_time = max(self.worst_case_execution_time, task.computation_time)
                else:
                    self.queues[0].append(task)

    def print_statistics(self):
        print(f"MLFQ Statistics:")
        print(f"Total Waiting Time: {self.total_waiting_time} µs")
        print(f"Total Turnaround Time: {self.total_turnaround_time} µs")
        print(f"Total Response Time: {self.total_response_time} µs")
        print(f"Maximum Turnaround Time: {self.max_turnaround_time} µs")
        print(f"Worst Case Execution Time: {self.worst_case_execution_time} µs")
