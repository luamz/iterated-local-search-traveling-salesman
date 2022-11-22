import tsplib95
import random
import time
import threading
import pathlib
import sys

class ParallelExecution:

    def __init__(self, instance, n_threads, max):
        self.instance = instance
        self.n_threads = n_threads
        self.iteration_max = max

        self.problem = tsplib95.load(f'{pathlib.Path(__file__).parent.resolve()}/instances/{instance}.tsp')
        self.problem.get_graph()
        self.problem_description = self.problem.as_keyword_dict()

        self.cities = [i - 1 for i in list(self.problem.get_nodes())]
        self.n_cities = len(self.cities)
        self.coord_x = []
        self.coord_y = []
        self.load_coordinates()

        self.global_best_solution = []
        self.global_best_cost = []
        self.sem = threading.Semaphore()


    def load_coordinates(self):
        if self.problem_description['EDGE_WEIGHT_TYPE'] == 'EUC_2D':
            for i in range(1, self.n_cities + 1):
                x, y = self.problem_description['NODE_COORD_SECTION'][i]
                self.coord_x.append(x); self.coord_y.append(y)


    def distance_cities(self, city_A, city_B):
        coord = city_A + 1, city_B + 1
        return self.problem.get_weight(*coord)


    def route_cost(self, cities):
        cost = 0
        i = 0
        while i < self.n_cities - 1:
            cost += self.distance_cities(cities[i], cities[i + 1])
            i += 1
        cost += self.distance_cities(cities[-1], cities[0])
        return cost


    def nearest_neighbour(self, initial_city):
        solution_cities = [initial_city]
        current_city = initial_city

        visited = [False] * self.n_cities
        visited[current_city] = True

        while len(solution_cities) < self.n_cities:
            min_distance = 9999999
            next_city = None

            for candidate_city in range(self.n_cities):
                if not visited[candidate_city] and candidate_city != current_city:
                    cost = self.distance_cities(current_city, candidate_city)
                    if cost < min_distance:
                        min_distance = cost
                        next_city = candidate_city

            solution_cities.append(next_city)
            visited[next_city] = True
            current_city = next_city

        return solution_cities


    def two_opt_local_search(self, cities):
        best_route = cities[:]
        best_cost = self.route_cost(best_route)
        improved = False
        for i in range(1, self.n_cities - 2):
            for j in range(i + 1, self.n_cities):
                if j - i == 1: continue
                current_route = cities[:]
                current_route[i:j] = current_route[j - 1:i - 1:-1]
                new_cost = self.route_cost(current_route)

                if new_cost < best_cost:
                    best_cost = new_cost
                    best_route = current_route
                    improved = True

        if improved:
            return best_route[:]
        else:
            return cities


    def perturbation(self, cities):
        i = random.randint(0, self.n_cities - 1)
        j = random.randint(0, self.n_cities - 1)
        if i != self.n_cities - 1 and i!=j:
            j = i + 1

        temp = cities[i]
        cities[i] = cities[j]
        cities[j] = temp
        return cities


    def iterations(self, thread, solution, best_solution, best_cost):
        local = threading.local()
        local.solution = solution[:]
        local.best_solution = best_solution[:]
        local.best_cost = best_cost

        count_no_improvement = 0
        for iteration in range(self.iteration_max):

            print(f"Thread:{thread+1} - Iteration:{iteration+1} - Best Cost:{local.best_cost} - No Improvemente: {count_no_improvement}")
            inital_cost = local.best_cost


            # Perturbations
            local.solution = self.perturbation(local.solution)
            pertubation_cost = self.route_cost(local.solution)

            if pertubation_cost < local.best_cost:
                count_no_improvement = 0
                local.best_cost = pertubation_cost
                local.best_solution = local.solution[:]


            # Local Search
            local.solution = self.two_opt_local_search(local.solution)
            local_search_cost = self.route_cost(local.solution)

            if local_search_cost < local.best_cost:
                count_no_improvement = 0
                local.best_cost = local_search_cost
                local.best_solution = local.solution[:]

            if local.best_cost == inital_cost:
                count_no_improvement = count_no_improvement + 1

            if abs(local.best_cost - local_search_cost) / local.best_cost > 0.01:
                local.solution = local.best_solution[:]

        # Global Critiria
        self.sem.acquire()
        if local.best_cost < self.global_best_cost[-1]:
            self.global_best_solution.append(local.best_solution[:])
            self.global_best_cost.append(local.best_cost)
        self.sem.release()


    def run_parallel_iterations(self, n_threads, initial_solution, initial_best_solution, initial_best_cost):
        threads = []
        for thread in range(n_threads):
            t = threading.Thread(target=self.iterations,
                                 args=(str(thread), initial_solution, initial_best_solution, initial_best_cost))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()


    def ils(self):
        start_time = time.time()

        # Initial Solution
        initial_city = random.randint(0, self.n_cities)
        #initial_city = 1

        initial_solution = self.nearest_neighbour(initial_city)
        cost = self.route_cost(initial_solution)

        # Local Search
        initial_solution = self.two_opt_local_search(initial_solution)
        cost = self.route_cost(initial_solution)

        initial_best_solution = initial_solution[:]
        initial_best_cost = cost
        self.global_best_cost.append(initial_best_solution)
        self.global_best_cost.append(cost)

        # Iterations
        self.run_parallel_iterations(self.n_threads, initial_solution, initial_best_solution, initial_best_cost)

        end_time = time.time()
        total_time = end_time - start_time

        print("---------------------------------------------")
        print("Route Cost  : %d" % self.global_best_cost[-1])
        print("Processing Time : %f" % total_time)
        print(f"Route Solution {self.global_best_solution[-1]}")
        f = open(f"{pathlib.Path(__file__).parent.resolve()}/results/results_modified_{self.instance}_{self.n_threads}.xlsx", "a")
        f.write(f"{initial_city},{self.global_best_cost[-1]},{total_time}\n")
        f.close()

    def run(self):
        self.ils()



def main():
    instance = sys.argv[1]
    threads = int(sys.argv[2])
    max_iterations = int(sys.argv[3])
    print("Graph {} - {} Threads  - {} Iterations\n".format(instance, threads, max_iterations))
    ex1 = ParallelExecution(instance,threads,max_iterations)
    ex1.run()


if __name__ == "__main__":
    main()
