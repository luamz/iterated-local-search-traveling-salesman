# Iterated Local Search (ILS) for Traveling Salesman Problem
This project solves the Traveling Salesman Problem with metaheuristic Iterated Local Search (ILS) and compares the results with sequential and parallel executions. 


## Generating results
To run the project set up desired config (Parallel or Sequential, number of threads, number of max iterations) in ``driver.py`` then run it.
The results will be save in the folder ``\results``.

### Instances
Instances were found at http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/

### Initial Solution
For initial solution it was used the Nearest Neighbour method.

### Local Search
For local search  it was used the 2-opt method.

### Pertubation
Sequential pertubation switches a random city and its right neighbour.


Parallel pertubation switches two random cities.

## Results
Some of the results found on instances ``berlin52`` and ``st70``.
![Results](https://user-images.githubusercontent.com/50959073/203293859-f5006608-0b54-4e4d-a5e9-a6f6644dcf50.png)
