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
                if random.random() < ev_ctx["RANDOM_CREATION_STOP_ITERATION_PROB"]:
                    break
            else:
                break

        pop.append(ind)
    return pop

def select(pop, fits, ev_ctx):
    return random.choices(pop, weights=fits, k=ev_ctx["POP_SIZE"])


def deep_copy_population(pop):
    off = []
    for p in pop:
        off.append(p.copy())
    return off

def merge_two_ind(ind1, ind2, ev_ctx):
    ind_new = []
    taken = [False for _ in range(ev_ctx["n"])]

    for idx in ind1:
        ind_new.append(idx)
        taken[idx] = True
    
    for idx in ind2:
        if not taken[idx]:
            ind_new.append(idx)
    return ind_new

def crossover(pop, ev_ctx):

    off = []
    for p1, p2 in zip(pop[::2], pop[1::2]):
        if random.random() < ev_ctx["CX_PROB"]:
            #point = random.randrange(0, IND_LEN)
            point_1 = len(p1)//2
            point_2 = len(p2)//2



            o1 = merge_two_ind(p1[:point_1], p2[point_2:], ev_ctx)
            o2 = merge_two_ind(p2[:point_2], p1[point_1:], ev_ctx)
            off.append(o1)
            off.append(o2)
        else:
            off.append(p1.copy())
            off.append(p2.copy())
    return off



def mutation_add_element(off, ev_ctx):
    for i in range(len(off)):
        if random.random() >= ev_ctx["MUT_ADD_PROB"]:
            break
    
        ind = off[i]
        ind_len = len(ind)

        taken = [False for _ in range(ev_ctx["n"])]
        elements_to_add_size = ev_ctx["n"]
        for idx in ind:
            taken[idx] = True
            elements_to_add_size -= 1

        if elements_to_add_size == 0:
            continue

        total_ind_weight = 0
        for idx in ind:
            total_ind_weight += ev_ctx["list_price_weight"][idx][1]
        
        add_elem_prob = ev_ctx["MUT_ADD_ELEMENT_PROB"](elements_to_add_size)
        for idx in range(ev_ctx["n"]):
            if taken[idx]:
                continue

            if random.random() >= add_elem_prob:
                weight_plus = ev_ctx["list_price_weight"][idx][1] + total_ind_weight
                if weight_plus <= ev_ctx["W"]:
                    ind.append(idx)
                    total_ind_weight = weight_plus
    
    return off

def mutation_del_element(off, ev_ctx):
    for i in range(len(off)):
        if random.random() >= ev_ctx["MUT_DEL_PROB"]:
            break
    
        ind = off[i]
        ind_len = len(ind)
        if ind_len == 0:
            continue

        new_ind = []
        del_elem_prob = ev_ctx["MUT_DEL_ELEMENT_PROB"](ind_len)
        for idx in ind:
            if random.random() >= del_elem_prob:
                new_ind.append(idx)
            
        off[i] = new_ind
    
    return off
    

def mutation(off, ev_ctx):

    off = mutation_del_element(off, ev_ctx)
    off = mutation_add_element(off, ev_ctx)

    return off

def evolution(ev_ctx):
    log = []
    pop = create_random_population(ev_ctx)
    for gen in range(ev_ctx["MAX_GEN"]):
        fits = [fitness(ind, ev_ctx) for ind in pop]
        log.append(max(fits))

        off = deep_copy_population(pop)
        off = select(off, fits, ev_ctx)
        off = crossover(off, ev_ctx)
        off = mutation(off, ev_ctx)
        
        off[0] = max(pop, key=lambda x: fitness(x, ev_ctx))
        pop = off[:]
    
    return pop, log

def evolutionary_algorithm(W, list_price_weight):
    ev_ctx = { # evolutionary context
        "MAX_GEN": 100,
        "POP_SIZE": 10,
        "CX_PROB": 0.8,
        "MUT_DEL_PROB": 0.8,
        "MUT_DEL_ELEMENT_PROB": lambda ind_size: 1/ind_size,
        "MUT_ADD_PROB": 0.8,
        "MUT_ADD_ELEMENT_PROB": lambda elements_to_add_size: 1/elements_to_add_size,
        "RANDOM_CREATION_STOP_ITERATION_PROB": 0.0,
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
    parser.add_argument("--file", default="test_data/input_1000.txt", type=str, help="Test data to load.")

    main(parser.parse_args())