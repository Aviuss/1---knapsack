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
        ind = set([])
        ind_total_weight = 0
        
        for idx in idx_list:
            weight_plus = ev_ctx["list_price_weight"][idx][1] + ind_total_weight
            if weight_plus <= ev_ctx["W"]:
                ind.add(idx)
                ind_total_weight = weight_plus
            else:
                break

        pop.append(ind)
    return pop

def tournament_select(pop, fits, ev_ctx, k=3):
    selected = []
    for _ in range(ev_ctx["POP_SIZE"]):
        contestants = random.sample(range(ev_ctx["POP_SIZE"]), k)
        winner = max(contestants, key=lambda i: fits[i])
        selected.append(pop[winner].copy())
    return selected

def roulette_wheel_select(pop, fits, ev_ctx):
    return random.choices(pop, weights=fits, k=ev_ctx["POP_SIZE"])

def select(pop, fits, ev_ctx):
    return tournament_select(pop, fits, ev_ctx)

def deep_copy_population(pop):
    off = []
    for p in pop:
        off.append(p.copy())
    return off

def merge_two_ind(ind1, ind2, ev_ctx):
    ind_new = set([])

    for idx in ind1:
        ind_new.add(idx)

    for idx in ind2:
        ind_new.add(idx)

    return ind_new

def crossover(pop, ev_ctx):
    off = []
    for p1, p2 in zip(pop[::2], pop[1::2]):
        if random.random() < ev_ctx["CX_PROB"]:
            point_1 = len(p1)//2
            point_2 = len(p2)//2
            
            p1_list = sorted(list(p1))
            p2_list = sorted(list(p2))
            #p1_set = set(p1)
            #p2_set = set(p2)
            #union_set = p1_set & p2_set
            #union_list = list(union_set)

            o1 = merge_two_ind(p1_list[:point_1], p2_list[point_2:], ev_ctx)
            o2 = merge_two_ind(p2_list[:point_2], p1_list[point_1:], ev_ctx)
            off.append(o1)
            off.append(o2)
        else:
            off.append(p1.copy())
            off.append(p2.copy())
    return off

def mutation_add_element(off, off_total_weight, ev_ctx):
    for i in range(len(off)):
        ind = off[i]
        ind_len = len(ind)
        if ind_len == ev_ctx["n"]:
            continue
        if random.random() >= ev_ctx["MUT_ADD_PROB"]:
            continue
    
        
        taken = [False for _ in range(ev_ctx["n"])]
        elements_to_add_size = ev_ctx["n"]
        for idx in ind:
            taken[idx] = True
            elements_to_add_size -= 1

        if elements_to_add_size == 0:
            continue

        
        add_elem_prob = ev_ctx["MUT_ADD_ELEMENT_PROB"](elements_to_add_size)
        at_lest_once = True
        nothing_added = True

        while at_lest_once or (off_total_weight[i] < ev_ctx["W"] and not nothing_added):
            at_lest_once = False
            nothing_added = True

            for idx in range(ev_ctx["n"]):
                if taken[idx]:
                    continue
                taken[idx] = True

                if random.random() < add_elem_prob:
                    continue
                weight_plus = ev_ctx["list_price_weight"][idx][1] + off_total_weight[i]
                if weight_plus <= ev_ctx["W"]:
                    ind.add(idx)
                    off_total_weight[i] = weight_plus
                    nothing_added = False
    
    return off

def mutation_del_element(off, off_total_weight, ev_ctx):
    for i in range(len(off)):
        if random.random() >= ev_ctx["MUT_DEL_PROB"]:
            continue
    
        ind = off[i]
        ind_len = len(ind)
        if ind_len == 0:
            continue

        
        del_elem_prob = ev_ctx["MUT_DEL_ELEMENT_PROB"](ind_len)
        at_lest_once = True

        while at_lest_once or off_total_weight[i] > ev_ctx["W"]:
            new_ind = set([])
            at_lest_once = False
            for idx in ind:
                if random.random() >= del_elem_prob:
                    new_ind.add(idx)
                else:
                    off_total_weight[i] -= ev_ctx["list_price_weight"][idx][1]
            ind = new_ind

        off[i] = new_ind
    
    return off
    

def mutation(off, ev_ctx):
    off_total_weight = []
    for ind in off:
        total_ind_weight = 0
        for idx in ind:
            total_ind_weight += ev_ctx["list_price_weight"][idx][1]
        off_total_weight.append(total_ind_weight)

    off = mutation_del_element(off, off_total_weight, ev_ctx)
    off = mutation_add_element(off, off_total_weight, ev_ctx)

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
        
        #off[0] = max(pop, key=lambda x: fitness(x, ev_ctx))
        #pop = off[:]
        pop.sort(key=lambda x: fitness(x, ev_ctx), reverse=True)
        pop = pop[0:int(ev_ctx["POP_SIZE"]*ev_ctx["PERCT_OF_PARENTS_INTO_NEXT_POPULATION"])]
        
        pop.extend(off)
        pop.sort(key=lambda x: fitness(x, ev_ctx), reverse=True)
        pop = pop[0:ev_ctx["POP_SIZE"]]

    return pop, log

def evolutionary_algorithm(W, list_price_weight):
    ev_ctx = { # evolutionary context
        "MAX_GEN": 100,
        "POP_SIZE": 100,
        "CX_PROB": 0.99,
        "MUT_DEL_PROB": 0.99,
        "MUT_DEL_ELEMENT_PROB": lambda ind_size: 1/ind_size,
        "MUT_ADD_PROB": 0.99,
        "MUT_ADD_ELEMENT_PROB": lambda elements_to_add_size: 1/elements_to_add_size,
        "PERCT_OF_PARENTS_INTO_NEXT_POPULATION": 0.05,
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
    #random.seed(2137)
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="test_data/input_1000.txt", type=str, help="Test data to load.")

    main(parser.parse_args())