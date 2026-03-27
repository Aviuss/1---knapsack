import argparse
import random

def read_data_from_file(filepath):
    file = open(filepath, 'r')
    data = file.readlines()
    file.close()
    data = list(map(lambda x:x.split(' '), data))
    data = list(map(lambda x:[int(x[0]), int(x[1])], data))

    n = data[0][0]
    W = data[0][1]
    list_price_weight = data[1:]

    if n != len(list_price_weight):
        raise Exception("Number of items doesn't correnspond to 'n'")
    
    return {
        "W": W,
        "list_price_weight": list_price_weight
    }

def fitness(ind, ev_ctx):
    total_weight = 0
    total_cost = 0
    for idx in ind:
        element = ev_ctx["list_price_weight"][idx]
        total_weight += element[1]
        total_cost += element[0]

        if total_weight > ev_ctx["W"]:
            return 0
    
    return total_cost

def create_random_population(ev_ctx):
    pop = []

    idx_list = list(range(ev_ctx["n"]))
    for _ in range(ev_ctx["POP_SIZE"]):
        random.shuffle(idx_list)
        ind = []
        ind_total_weight = 0
        
        for idx in idx_list:
            weight_plus = ev_ctx["list_price_weight"][idx][1] + ind_total_weight
            if weight_plus <= ev_ctx["W"]:
                ind.append(idx)
                ind_total_weight = weight_plus
            else:
                break

        pop.append(ind)
    return pop

def select(pop, fits, ev_ctx):
    return random.choices(pop, weights=fits, k=ev_ctx["POP_SIZE"])

def crossover(pop):
    return pop

    off = []
    for p1, p2 in zip(pop[::2], pop[1::2]):
        if random.random() < 0.8:
            point = random.randrange(0, IND_LEN)
            o1 = p1[:point] + p2[point:]
            o2 = p2[:point] + p1[point:]
            off.append(o1)
            off.append(o2)
        else:
            off.append(p1[:])
            off.append(p2[:])
    return off

def mutation(pop):
    return pop

    off = []
    for p in pop:
        if random.random() < MUT_PROB:
            o = [1-i if random.random() < MUT_FLIP_PROB else i for i in p]
            off.append(o)
        else:
            off.append(p[:])
    return off

def evolution(ev_ctx):
    log = []
    pop = create_random_population(ev_ctx)
    for gen in range(ev_ctx["MAX_GEN"]):
        fits = [fitness(ind, ev_ctx) for ind in pop]
        log.append(max(fits))
        mating_pool = select(pop, fits, ev_ctx)
        off = crossover(mating_pool)
        off = mutation(off)
        off[0] = max(pop, key=lambda x: fitness(x, ev_ctx))
        pop = off[:]
    
    return pop, log

def evolutionary_algorithm(W, list_price_weight):
    ev_ctx = { # evoulionary context
        "MAX_GEN": 1000,
        "POP_SIZE": 50,
        "IND_LEN": 50,
        "CX_PROB": 0.8,
        "MUT_PROB": 0.6,
        "W": W,
        "list_price_weight": list_price_weight,
        "n": len(list_price_weight),
    }

    pop, log = evolution(ev_ctx)
    print(max(pop, key=lambda x: fitness(x, ev_ctx)))
    print(log)

    import matplotlib.pyplot as plt
    plt.plot(log)
    plt.show()


def main(args):
    knapsack_data = read_data_from_file(args.file)
    solution = evolutionary_algorithm(
        knapsack_data["W"],
        knapsack_data["list_price_weight"]
    )
    print(solution)


if __name__ == "__main__":
    random.seed(2137)
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="test_data/debug_10.txt", type=str, help="Test data to load.")

    main(parser.parse_args())