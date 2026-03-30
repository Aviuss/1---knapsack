import argparse
import random
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from matplotlib.lines import Line2D
import numpy as np

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
    if ev_ctx["TOURNAMENT_SELECTION"] == None:
        return roulette_wheel_select(pop, fits, ev_ctx)
    return tournament_select(pop, fits, ev_ctx, ev_ctx["TOURNAMENT_SELECTION"])

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

def add_element_full(off, off_total_weight, ev_ctx):
    for i in range(len(off)):
        ind = off[i]
        ind_len = len(ind)
        if ind_len == ev_ctx["n"]:
            continue

        taken = [False for _ in range(ev_ctx["n"])]
        taken_id_zip = list(zip(taken, list(range(ev_ctx["n"]))))
        taken_id_zip = list(map(lambda x:list(x), taken_id_zip))
        elements_to_add_size = ev_ctx["n"]
        for idx in ind:
            taken_id_zip[idx][0] = True
            elements_to_add_size -= 1

        if elements_to_add_size == 0:
            continue

        
        nothing_added = False

        while (off_total_weight[i] < ev_ctx["W"] and not nothing_added):
            nothing_added = True

            random.shuffle(taken_id_zip)

            for j in range(ev_ctx["n"]):
                if taken_id_zip[j][0]:
                    continue
                taken_id_zip[j][0] = True
                idx = taken_id_zip[j][1]

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


        del_elem_prob = ev_ctx["MUT_DEL_ELEMENT_PROB"](ind_len, ev_ctx)
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
    off = add_element_full(off, off_total_weight, ev_ctx)

    return off

def evolution(ev_ctx):
    max_log = []
    flat_log = []
    pop = create_random_population(ev_ctx)
    for gen in range(ev_ctx["MAX_GEN"]):
        fits = [fitness(ind, ev_ctx) for ind in pop]
        max_log.append(max(fits))
        
        ev_ctx['current_variable_is_function_flat'] = False
        if len(max_log) >= ev_ctx["IS_FLAT_WINDOW"]:
            if max_log[len(max_log)-1] == max_log[len(max_log) - ev_ctx["IS_FLAT_WINDOW"] - 1]:
                ev_ctx['current_variable_is_function_flat'] = True
        flat_log.append(ev_ctx['current_variable_is_function_flat'])

        off = deep_copy_population(pop)
        off = select(off, fits, ev_ctx)
        off = crossover(off, ev_ctx)
        off = mutation(off, ev_ctx)
        
        pop.sort(key=lambda x: fitness(x, ev_ctx), reverse=True)
        pop = pop[0:int(ev_ctx["POP_SIZE"]*ev_ctx["PERCT_OF_PARENTS_INTO_NEXT_POPULATION"])]
        
        pop.extend(off)
        pop.sort(key=lambda x: fitness(x, ev_ctx), reverse=True)
        pop = pop[0:ev_ctx["POP_SIZE"]]

    return pop, max_log, flat_log

def evolutionary_algorithm(W, list_price_weight):
    
    def mut_del_elem_prob_func(ind_size, ev_ctx):
        if ev_ctx['current_variable_is_function_flat']:
            return 7/ind_size
        return 1/ind_size

    ev_ctx = { # evolutionary context
        "MAX_GEN": 50,
        "POP_SIZE": 20,
        "CX_PROB": 0.50,
        "MUT_DEL_PROB": 0.50,
        "MUT_DEL_ELEMENT_PROB": mut_del_elem_prob_func,
        "PERCT_OF_PARENTS_INTO_NEXT_POPULATION": 0.1,
        "W": W,
        "list_price_weight": list_price_weight,
        "n": len(list_price_weight),
        "IS_FLAT_WINDOW": 10,
        "current_variable_is_function_flat": False,
        "TOURNAMENT_SELECTION": 3 # If set to None -> roulete selection
    }


    pop, max_log, flat_log = evolution(ev_ctx)
    print(max(pop, key=lambda x: fitness(x, ev_ctx)))
    print(max_log)

    fig, ax = plt.subplots()

    x = np.arange(len(max_log))
    y = np.array(max_log)
    flags = np.array(flat_log, dtype=bool)

    for i in range(len(x) - 1):
        color = 'red' if flags[i] else 'steelblue'
        ax.plot(x[i:i+2], y[i:i+2], color=color, linewidth=1.5)

    legend_elements = [
        Line2D([0], [0], color='steelblue', label='evolving'),
        Line2D([0], [0], color='red',       label='flat (stagnant)'),
    ]
    ax.legend(handles=legend_elements)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Max fitness')
    plt.tight_layout()
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