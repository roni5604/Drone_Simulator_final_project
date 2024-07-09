import time
import threading
from typing import List, Callable


class CPU:
    all_cpus: List['CPU'] = []

    def __init__(self, hz: int, name: str):
        """
             Initialize the CPU object with the given frequency (hz) and name.
             """
        self.hz = hz
        self.functions_list: List[Callable[[int], None]] = []
        self.is_play = False # Flag to indicate if the CPU is running
        self.is_played_before_stop = False # Flag to indicate if the CPU was running before it was stopped
        self.elapsed_milli = 0

        # Create and start a new thread for this CPU
        self.thread = threading.Thread(target=self.thread_run, name=f"Eventor_{name}")
        self.thread.daemon = True # Daemon thread will shut down with the main program
        self.thread.start()

        # Add this CPU to the list of all CPUs
        CPU.all_cpus.append(self)

    @staticmethod
    def stop_all_cpus():
        """
        Stop all CPUs by setting their is_play attribute to False.
        """
        for cpu in CPU.all_cpus:
            cpu.is_play = False

    @staticmethod
    def resume_all_cpus():
        """
        Resume all CPUs that were playing before they were stopped.
        """
        for cpu in CPU.all_cpus:
            cpu.resume()

    def resume(self):
        """
          Resume the CPU if it was playing before it was stopped.
          """
        if self.is_played_before_stop:
            self.is_play = True

    def add_function(self, func: Callable[[int], None]):
        """
        Add a function to the CPU's function list.
        """
        self.functions_list.append(func)

    def play(self):
        """
            Start or resume the CPU's operations.
            """
        self.is_play = True
        self.is_played_before_stop = True
        self.resume()

    def stop(self):
        """
        Stop the CPU's operations.
        """
        self.is_play = False
        self.is_played_before_stop = False

    def get_elapsed_milli(self) -> int:
        """
        Get the elapsed time in milliseconds since the CPU started.
        """
        return self.elapsed_milli

    def reset_clock(self):
        self.elapsed_milli = 0

    def thread_run(self):
        """
          The main method run by the CPU's thread. Executes functions in the function list at the specified frequency.
          """
        functions_size = 0
        last_sample_times = [] # List to keep track of the last execution times of functions
        i = 0

        # Time to sleep between function executions to maintain the frequency
        time_to_sleep = max(2, 1000 // self.hz)

        while True:
            # Update the size of the functions list and the last sample times if the size has changed
            if functions_size != len(self.functions_list):
                functions_size = len(self.functions_list)
                last_sample_times = [0] * functions_size
                i = 0
            # If there are no functions to run, continue to the next iteration
            if functions_size == 0:
                # If there are no functions to execute, continue the loop
                continue
            # If the CPU is not running, update the last sample time
            last_sample = time.time() * 1000

            try:
                # Sleep for the calculated interval
                time.sleep(time_to_sleep / 1000.0)
                # Wait while the CPU is stopped
                while not self.is_play:
                    last_sample = time.time() * 1000
            except InterruptedError:
                pass

            diff = int(time.time() * 1000 - last_sample)
            before_index = self.get_cyclic(i - 1, functions_size)
            actual_diff = last_sample_times[before_index] + diff - last_sample_times[i]
            last_sample_times[i] = last_sample_times[before_index] + diff

            # Execute the current function with the actual time difference
            curr_func = self.functions_list[i]
            curr_func(actual_diff)
            self.elapsed_milli += actual_diff

            # Move to the next function in the list
            i = (i + 1) % functions_size

    @staticmethod
    def get_cyclic(i: int, size: int) -> int:
        # Get the cyclic index for the functions list
        i %= size
        if i < 0:
            return size + i
        return i
