from MLFQ import MLFQ
from EDF import EDF
from WRR import WRR
import copy

class EASH:
    def __init__(self, input_dim, output_dim):
        self.mlfq = MLFQ(3)
        self.edf = EDF()
        self.wrr = WRR()
        self.tasks = []
        self.time = 0
        self.scheduler_index = 0
        self.schedulers = [self.mlfq, self.edf, self.wrr]

        # Metrics
        self.total_waiting_time = 0
        self.total_turnaround_time = 0
        self.total_response_time = 0
        self.total_context_switches = 0
        self.total_completed_tasks = 0
        self.total_missed_tasks = 0
        self.cpu_busy_time = 0
        self.max_turnaround_time = 0
        self.worst_case_execution_time = 0

        self.current_task = None

    def add_task(self, task):
        self.tasks.append(copy.deepcopy(task))
        self.mlfq.add_task(copy.deepcopy(task))
        self.edf.add_task(copy.deepcopy(task))
        self.wrr.add_task(copy.deepcopy(task))

    def schedule(self):
        task = None
        for _ in range(len(self.schedulers)):
            task = self.schedulers[self.scheduler_index].get_next_task()
            if task:
                break
            self.scheduler_index = (self.scheduler_index + 1) % len(self.schedulers)

        if task:
            if self.current_task is not task:
                self.total_context_switches += 1
                self.current_task = task

            if task.start_time is None:
                task.set_start_time(self.time)
                self.total_response_time += task.response_time()
                self.total_waiting_time += task.waiting_time()

            task.remaining_time -= 1
            self.cpu_busy_time += 1
            if task.remaining_time <= 0:
                task.set_finish_time(self.time + 1)  # +1 because the task finished in this cycle
                turnaround_time = task.turnaround_time()
                self.total_turnaround_time += turnaround_time
                self.max_turnaround_time = max(self.max_turnaround_time, turnaround_time)
                self.worst_case_execution_time = max(self.worst_case_execution_time, task.computation_time)
                self.total_completed_tasks += 1
                if task in self.tasks:  # Ensure task is in the list before removing
                    self.tasks.remove(task)
                self.current_task = None
                # Check if task missed its deadline
                if self.time + 1 > task.deadline:
                    self.total_missed_tasks += 1

        self.scheduler_index = (self.scheduler_index + 1) % len(self.schedulers)

    def run(self, steps):
        for _ in range(steps):
            self.schedule()
            self.time += 1
            self.mlfq.run(1)  # Run MLFQ for one time unit
            self.edf.run(1)   # Run EDF for one time unit
            self.wrr.run(1)   # Run WRR for one time unit

    def print_statistics(self):
        throughput = self.total_completed_tasks / self.time
        cpu_utilization = (self.cpu_busy_time / self.time) * 100 if self.time > 0 else 0
        task_completion_percentage = (self.total_completed_tasks / (self.total_completed_tasks + self.total_missed_tasks)) * 100 if (self.total_completed_tasks + self.total_missed_tasks) > 0 else 100

        print(f"Total Context Switches: {self.total_context_switches}")
        print(f"Total Waiting Time: {self.total_waiting_time} µs")
        print(f"Total Turnaround Time: {self.total_turnaround_time} µs")
        print(f"Total Response Time: {self.total_response_time} µs")
        print(f"Maximum Turnaround Time: {self.max_turnaround_time} µs")
        print(f"Worst Case Execution Time: {self.worst_case_execution_time} µs")
        print(f"Throughput: {throughput:.2f} tasks/unit time")
        print(f"CPU Utilization: {cpu_utilization:.2f}%")
        print(f"Task Completion Percentage: {task_completion_percentage:.2f}%")
        print(f"Total Missed Tasks: {self.total_missed_tasks}")

        print("\nCPU Load Over Time:")
        print(f"Time CPU was busy: {self.cpu_busy_time} µs")
        print(f"Total simulation time: {self.time} µs")

        print("\nMLFQ Statistics:")
        self.mlfq.print_statistics()
        print("\nEDF Statistics:")
        self.edf.print_statistics()
        print("\nWRR Statistics:")
        self.wrr.print_statistics()
