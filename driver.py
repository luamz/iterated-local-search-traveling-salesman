from subprocess import call
import pathlib

INSTANCES = ['berlin52', 'st70', 'rat99', 'kroA', 'lin105']
CURRENT_INSTANCE = INSTANCES[0]
N_THREADS = 5
MAX_ITERATIONS = 500
MAX_THREAD_ITERATIONS = MAX_ITERATIONS//N_THREADS

N_EXECUTIONS = 1
PARALLEL = True
SEQUENTIAL = True


def main():
    if SEQUENTIAL:
        for i in range(N_EXECUTIONS):
            print(f"Execution {i+1} - Sequential")
            call(["python3", f"{pathlib.Path(__file__).parent.resolve()}/main_sequential.py",
                  f"{CURRENT_INSTANCE}", f"{str(MAX_ITERATIONS)}"])

    if PARALLEL:
        for i in range(N_EXECUTIONS):
            print(f"Execution {i+1} - Parallel")
            call(["python3", f"{pathlib.Path(__file__).parent.resolve()}/main_parallel.py",
                  f"{CURRENT_INSTANCE}", f"{str(N_THREADS)}", f"{str(MAX_THREAD_ITERATIONS)}"])


if __name__ == "__main__":
    main()
