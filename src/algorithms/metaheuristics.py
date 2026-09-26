"""Metaheuristics: no optimality guarantee, but scale to n = 10,000+ with adjustable time budget."""
import math
import random
import time

import numpy as np

from ..models import Solution


def randomized_approach(problem, iterations=1000, seed=None):
    """Multi-start randomized approach.

    At each iteration, shuffles item order and builds a greedy solution
    with that order; keeps the best solution found. Simple, good for
    quick exploration, but no quality guarantee.
    """
    start_time = time.time()

    if seed is not None:
        random.seed(seed)

    best_value = 0
    best_weight = 0
    best_items = []

    for _ in range(iterations):
        indices = list(range(problem.n))
        random.shuffle(indices)

        selected = []
        total_weight = 0
        total_value = 0

        for idx in indices:
            item = problem.items[idx]
            if total_weight + item.weight <= problem.capacity:
                selected.append(idx)
                total_weight += item.weight
                total_value += item.value

        if total_value > best_value:
            best_value = total_value
            best_weight = total_weight
            best_items = selected

    time_taken = time.time() - start_time
    sol = Solution(best_items, best_value, best_weight, time_taken)
    sol.usage_percent = (best_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def genetic_algorithm(problem, population_size=100, generations=50,
                       crossover_rate=0.8, mutation_rate=0.02,
                       elitism_count=5, seed=None):
    """Genetic Algorithm for the 0-1 Knapsack problem.

    Maintains a population of solutions that evolve through tournament
    selection, two-point crossover, bit-flip mutation and elitism over
    multiple generations.
    """
    start_time = time.time()

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    n = problem.n
    capacity = problem.capacity
    items = problem.items

    def fitness(chromosome):
        """Quality of a chromosome (solution), penalized if overweight."""
        total_weight = sum(chromosome[i] * items[i].weight for i in range(n))
        total_value = sum(chromosome[i] * items[i].value for i in range(n))

        if total_weight > capacity:
            penalty = (total_weight - capacity) * 10
            return max(0, total_value - penalty)
        return total_value

    def create_initial_population():
        """Creates initial population with different strategies."""
        population = []

        # 50% random solutions
        for _ in range(population_size // 2):
            chromosome = [random.randint(0, 1) for _ in range(n)]
            population.append(chromosome)

        # 25% greedy solutions (ratio)
        sorted_indices = sorted(range(n), key=lambda i: items[i].ratio(), reverse=True)
        for _ in range(population_size // 4):
            chromosome = [0] * n
            weight = 0
            for idx in sorted_indices:
                if weight + items[idx].weight <= capacity and random.random() > 0.3:
                    chromosome[idx] = 1
                    weight += items[idx].weight
            population.append(chromosome)

        # 25% solutions with variable density
        for _ in range(population_size - len(population)):
            chromosome = [0] * n
            density = random.uniform(0.2, 0.8)
            weight = 0
            for i in range(n):
                if random.random() < density and weight + items[i].weight <= capacity:
                    chromosome[i] = 1
                    weight += items[i].weight
            population.append(chromosome)

        return population

    def tournament_selection(population, fitnesses, tournament_size=3):
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
        winner_idx = tournament_indices[tournament_fitnesses.index(max(tournament_fitnesses))]
        return population[winner_idx]

    def crossover(parent1, parent2):
        """Two-point crossover."""
        if random.random() > crossover_rate:
            return parent1[:], parent2[:]

        point1 = random.randint(1, n - 2)
        point2 = random.randint(point1 + 1, n - 1)

        child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
        child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]

        return child1, child2

    def mutate(chromosome):
        """Bit-flip mutation."""
        mutated = chromosome[:]
        for i in range(n):
            if random.random() < mutation_rate:
                mutated[i] = 1 - mutated[i]
        return mutated

    population = create_initial_population()
    best_chromosome = None
    best_fitness = -1

    for gen in range(generations):
        fitnesses = [fitness(chromo) for chromo in population]

        gen_best_idx = fitnesses.index(max(fitnesses))
        gen_best_fitness = fitnesses[gen_best_idx]

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_chromosome = population[gen_best_idx][:]

        sorted_indices = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)

        new_population = []

        # Elitism: keep the best
        for i in range(elitism_count):
            new_population.append(population[sorted_indices[i]][:])

        while len(new_population) < population_size:
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)

            child1, child2 = crossover(parent1, parent2)

            child1 = mutate(child1)
            child2 = mutate(child2)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    selected_items = [i for i in range(n) if best_chromosome[i] == 1]
    total_value = sum(items[i].value for i in selected_items)
    total_weight = sum(items[i].weight for i in selected_items)

    time_taken = time.time() - start_time

    sol = Solution(selected_items, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / capacity * 100) if capacity > 0 else 0

    return sol


def genetic_algorithm_adaptive(problem):
    """Adjusts population size, generations and mutation rate to problem
    size for a good quality/time tradeoff (finer exploration for small
    instances, faster convergence for large ones)."""
    n = problem.n

    if n <= 50:
        return genetic_algorithm(problem, population_size=50, generations=30, mutation_rate=0.03)
    elif n <= 100:
        return genetic_algorithm(problem, population_size=80, generations=40, mutation_rate=0.02)
    elif n <= 500:
        return genetic_algorithm(problem, population_size=100, generations=50, mutation_rate=0.02)
    elif n <= 1000:
        return genetic_algorithm(problem, population_size=120, generations=40, mutation_rate=0.01)
    else:
        return genetic_algorithm(problem, population_size=150, generations=30, mutation_rate=0.01)


def simulated_annealing(problem, initial_temp=1000, cooling_rate=0.995,
                         min_temp=1, max_iterations=10000, seed=None):
    """Simulated Annealing for the 0-1 Knapsack problem.

    Starts from a greedy solution, explores neighbors by flipping a bit,
    always accepts improvements and accepts degradations with
    probability exp(-delta/T), while T cools down progressively.
    """
    start_time = time.time()

    if seed is not None:
        random.seed(seed)

    n = problem.n
    capacity = problem.capacity
    items = problem.items

    def evaluate(solution):
        total_value = sum(solution[i] * items[i].value for i in range(n))
        total_weight = sum(solution[i] * items[i].weight for i in range(n))
        return total_value, total_weight

    def fitness(solution):
        value, weight = evaluate(solution)
        if weight > capacity:
            return value - (weight - capacity) * 10
        return value

    # Initial solution: greedy by ratio
    current_solution = [0] * n
    sorted_indices = sorted(range(n), key=lambda i: items[i].ratio(), reverse=True)
    current_weight = 0
    for idx in sorted_indices:
        if current_weight + items[idx].weight <= capacity:
            current_solution[idx] = 1
            current_weight += items[idx].weight

    current_fitness = fitness(current_solution)
    best_solution = current_solution[:]
    best_fitness = current_fitness

    temperature = initial_temp
    iteration = 0

    while temperature > min_temp and iteration < max_iterations:
        neighbor = current_solution[:]
        flip_idx = random.randint(0, n - 1)
        neighbor[flip_idx] = 1 - neighbor[flip_idx]

        neighbor_fitness = fitness(neighbor)
        delta = neighbor_fitness - current_fitness

        if delta > 0:
            current_solution = neighbor
            current_fitness = neighbor_fitness
        else:
            acceptance_prob = math.exp(delta / temperature)
            if random.random() < acceptance_prob:
                current_solution = neighbor
                current_fitness = neighbor_fitness

        if current_fitness > best_fitness:
            _, weight = evaluate(current_solution)
            if weight <= capacity:
                best_solution = current_solution[:]
                best_fitness = current_fitness

        temperature *= cooling_rate
        iteration += 1

    selected_items = [i for i in range(n) if best_solution[i] == 1]
    total_value = sum(items[i].value for i in selected_items)
    total_weight = sum(items[i].weight for i in selected_items)

    # Repair if necessary (remove lowest-ratio items until back under capacity)
    if total_weight > capacity:
        selected_sorted = sorted(selected_items, key=lambda i: items[i].ratio())
        while total_weight > capacity and selected_sorted:
            remove_idx = selected_sorted.pop(0)
            total_weight -= items[remove_idx].weight
            total_value -= items[remove_idx].value
            selected_items.remove(remove_idx)

    time_taken = time.time() - start_time

    sol = Solution(selected_items, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / capacity * 100) if capacity > 0 else 0
    sol.iterations = iteration
    sol.final_temperature = temperature

    return sol


def simulated_annealing_adaptive(problem):
    """Adjusts initial temperature, cooling rate and iteration budget to
    problem size (fast cooling for small instances, slow cooling and more
    iterations for large ones)."""
    n = problem.n

    if n <= 50:
        return simulated_annealing(problem, initial_temp=500, cooling_rate=0.99, max_iterations=5000)
    elif n <= 200:
        return simulated_annealing(problem, initial_temp=1000, cooling_rate=0.995, max_iterations=10000)
    elif n <= 1000:
        return simulated_annealing(problem, initial_temp=2000, cooling_rate=0.997, max_iterations=15000)
    else:
        return simulated_annealing(problem, initial_temp=5000, cooling_rate=0.999, max_iterations=20000)
