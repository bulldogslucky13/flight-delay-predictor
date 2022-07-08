# Author: DEREK STAHL

from pandas import *
import numpy as np
import time


class Node:
    def __init__(self, value=None, parent=None, children=None, action=None, next=[]):
        self.value = value  # attribute
        self.parent = parent    # parent node
        self.children = children    # possible actions to take
        self.action = action    # action taken to get to this attribute
        self.next = next    # next nodes

    # puts all node attributes into a string
    def __str__(self):
        x = ""
        for i in self.next:
            if type(i) != int:
                x = x + " " + str(i.value)
            else:
                x = x + " " + "DONE"

        return "NODE: " + str(self.value) + "\n" + "CHILDREN: " + str(self.children) + "\n" \
            + "ACTION: " + str(self.action) + "\n" + "NEXT: " + x + "\n\n"


# function used to calculate entropy of variables
def entropy_calc(series):
    value, counts = np.unique(series, return_counts=True)
    counts = counts / counts.sum()
    return (-counts * np.log2(counts)).sum(), value


# returns smallest child entropy along with its values
def child_entropy(dataset, used_vars):
    entropy_dict = {}
    values_dict = {}
    for (columnName, columnData) in dataset.iteritems():
        if columnName not in used_vars:
            entropy_value, values = entropy_calc(dataset[columnName])
            if entropy_value != 0:
                entropy_dict[columnName] = entropy_value
                values_dict[columnName] = values
    if entropy_dict:
        minimum_key = min(entropy_dict, key=entropy_dict.get)
        return minimum_key, values_dict[minimum_key]
    else:
        return 0, 0


# function used to create decision tree, recursive
def create_tree(dataset, used_vars, curr_node, path, tree):
    new_used_vars = used_vars
    new_path = path
    new_tree = tree

    # check to see if we are on the root node
    if curr_node is None:
        next_node, next_values = child_entropy(dataset=dataset, used_vars=used_vars)
        # Add next node to used variables
        # new_used_vars.append(next_node)
        new_node = Node(value=next_node, parent=None, children=next_values, action=None)
        new_tree.append(new_node)
        # go on to children nodes
        create_tree(dataset=dataset, used_vars=new_used_vars, curr_node=new_node, path=new_path, tree=new_tree)

    # the amount of variables we have
    elif len(used_vars) != 24:
        new_datasets = []
        # check to see if children are list type
        if type(curr_node.children) == int:
            print("Do Nothing")
        else:
            child_value = []
            # specify next data sets only to children values
            for child in curr_node.children:
                new_datasets.append(dataset[dataset[curr_node.value] == child])
            count = 0
            for data in new_datasets:
                # check to see if all values in delayed column are equal
                if (data['DELAYED'].to_numpy() == (data['DELAYED'].to_numpy())[0]).all():
                    fetch_node = curr_node
                    curr_node.next.append(-1)
                    new_list = []
                    while(fetch_node.parent != None):
                        temp = (fetch_node.parent.value, fetch_node.action)
                        new_list.append(temp)

                        fetch_node = fetch_node.parent
                    new_path.append(new_list)
                    count = count + 1
                    continue
                else:
                    next_node, next_values = child_entropy(dataset=data, used_vars=used_vars)
                    # fixing for overfitting
                    if len(next_values) < 5:
                        fetch_node = curr_node
                        curr_node.next.append(-1)
                        new_list = []
                        while(fetch_node.parent != None):
                            temp = (fetch_node.parent.value, fetch_node.action)
                            new_list.append(temp)

                            fetch_node = fetch_node.parent
                        new_path.append(new_list)
                        count = count + 1
                        continue

                    new_node = Node(value=next_node, parent=curr_node, children=next_values,
                                    action=curr_node.children[count], next=[])
                    new_tree.append(new_node)
                    curr_node.next.append(new_node)
                    # go on to children nodes
                    # new_used_vars.append(next_node)
                    create_tree(dataset=data, used_vars=new_used_vars, curr_node=new_node, path=new_path, tree=new_tree)
                count = count + 1
    return new_tree


# algorithm to search tree
def search_tree(tree, airline, dataset):

    path = []

    # get root node
    next_node = tree[0]

    path.append(next_node)
    new_dataset = dataset

    while next_node != -1:
        # get value to search
        search_value = airline[next_node.value]
        # check to see if value exists in list
        if search_value in new_dataset[next_node.value].tolist():
            # filter only to events with this node value
            new_dataset = (new_dataset[new_dataset[next_node.value] == search_value])
            # get index of where the value we are searching for is
            if search_value in next_node.children.tolist():
                value_index = (next_node.children.tolist()).index(search_value)
                next_node = next_node.next[value_index]
                path.append(next_node)
            else:
                break
        else:
            break

    if path[-1] == -1:
        path.remove(-1)

    print("PATH: ")
    for x in path:
        print(x)

    last_node = path[-1]
    set = []
    for outcome in last_node.children.tolist():
        set.append(new_dataset[new_dataset[last_node.value] == outcome])
    # block of code to calculate the average delay between remaining dataframes
    delay_sum = 0
    count = 0
    for dataframe in set:
        delay_sum = delay_sum + dataframe['DELAYED'].sum()
        count = count + len(dataframe['DELAYED'])
    delay_average = delay_sum/count
    print("DELAY AVERAGE: ", delay_average)
    if delay_average >= 0.5:
        print("DELAYED")
        return 1
    else:
        print("ON TIME")
        return 0


def search_one_point(airlines, tree):
    test_group = airlines.sample(n=1, random_state=25)
    # used as the airline entry into the algorithm
    for ind in test_group.index:
        # used as the airline entry into the algorithm
        demo_dict = {"MONTH": test_group['MONTH'][ind], "DAY": test_group['DAY'][ind],
                     "DAY_OF_WEEK": test_group['DAY_OF_WEEK'][ind], "AIRLINE": test_group['AIRLINE'][ind],
                     "FLIGHT_NUMBER": test_group['FLIGHT_NUMBER'][ind], "TAIL_NUMBER": test_group['TAIL_NUMBER'][ind],
                     "ORIGIN_AIRPORT": test_group['ORIGIN_AIRPORT'][ind],
                     "DESTINATION_AIRPORT": test_group['DESTINATION_AIRPORT'][ind],
                     "SCHEDULED_DEPARTURE": test_group['SCHEDULED_DEPARTURE'][ind],
                     "AIR_SYSTEM_DELAY": test_group['AIR_SYSTEM_DELAY'][ind],
                     "SECURITY_DELAY": test_group['SECURITY_DELAY'][ind],
                     "AIRLINE_DELAY": test_group['AIRLINE_DELAY'][ind],
                     "LATE_AIRCRAFT_DELAY": test_group['LATE_AIRCRAFT_DELAY'][ind],
                     "WEATHER_DELAY": test_group['WEATHER_DELAY'][ind],
                     "DEPARTURE_TIME": test_group['DEPARTURE_TIME'][ind],
                     "TAXI_OUT": test_group['TAXI_OUT'][ind], "WHEELS_OFF": test_group['WHEELS_OFF'][ind],
                     "SCHEDULED_TIME": test_group['SCHEDULED_TIME'][ind],
                     "ELAPSED_TIME": test_group['ELAPSED_TIME'][ind], "AIR_TIME": test_group['AIR_TIME'][ind],
                     "DISTANCE": test_group['DISTANCE'][ind], "WHEELS_ON": test_group['WHEELS_ON'][ind],
                     "TAXI_IN": test_group['TAXI_IN'][ind], "SCHEDULED_ARRIVAL": test_group['SCHEDULED_ARRIVAL'][ind],
                     "ARRIVAL_TIME": test_group['ARRIVAL_TIME'][ind], "DELAYED": test_group['DELAYED'][ind]}
    prediction = search_tree(tree, demo_dict, airlines)
    if prediction == 1:
        print("PREDICTION: DELAYED")
    else:
        print("PREDICTION: ON TIME")
    if prediction == demo_dict['DELAYED']:
        print("CORRECT")
    else:
        print("INCORRECT")


def calc_prec_recall(airlines, tree):
    test_group = airlines.sample(n=500, random_state=25)

    true_positives = 0
    false_negatives = 0
    false_positives = 0
    for ind in test_group.index:
        # used as the airline entry into the algorithm
        demo_dict = {"MONTH": test_group['MONTH'][ind], "DAY": test_group['DAY'][ind],
                     "DAY_OF_WEEK": test_group['DAY_OF_WEEK'][ind], "AIRLINE": test_group['AIRLINE'][ind],
                     "FLIGHT_NUMBER": test_group['FLIGHT_NUMBER'][ind], "TAIL_NUMBER": test_group['TAIL_NUMBER'][ind],
                     "ORIGIN_AIRPORT": test_group['ORIGIN_AIRPORT'][ind],
                     "DESTINATION_AIRPORT": test_group['DESTINATION_AIRPORT'][ind],
                     "SCHEDULED_DEPARTURE": test_group['SCHEDULED_DEPARTURE'][ind],
                     "AIR_SYSTEM_DELAY": test_group['AIR_SYSTEM_DELAY'][ind],
                     "SECURITY_DELAY": test_group['SECURITY_DELAY'][ind],
                     "AIRLINE_DELAY": test_group['AIRLINE_DELAY'][ind],
                     "LATE_AIRCRAFT_DELAY": test_group['LATE_AIRCRAFT_DELAY'][ind],
                     "WEATHER_DELAY": test_group['WEATHER_DELAY'][ind],
                     "DEPARTURE_TIME": test_group['DEPARTURE_TIME'][ind],
                     "TAXI_OUT": test_group['TAXI_OUT'][ind], "WHEELS_OFF": test_group['WHEELS_OFF'][ind],
                     "SCHEDULED_TIME": test_group['SCHEDULED_TIME'][ind],
                     "ELAPSED_TIME": test_group['ELAPSED_TIME'][ind], "AIR_TIME": test_group['AIR_TIME'][ind],
                     "DISTANCE": test_group['DISTANCE'][ind], "WHEELS_ON": test_group['WHEELS_ON'][ind],
                     "TAXI_IN": test_group['TAXI_IN'][ind], "SCHEDULED_ARRIVAL": test_group['SCHEDULED_ARRIVAL'][ind],
                     "ARRIVAL_TIME": test_group['ARRIVAL_TIME'][ind], "DELAYED": test_group['DELAYED'][ind]}
        prediction = search_tree(tree, demo_dict, airlines)
        if prediction == 1 and demo_dict['DELAYED'] == prediction:
            true_positives = true_positives + 1
        elif prediction == 0 and demo_dict['DELAYED'] == 1:
            false_negatives = false_negatives + 1
        elif prediction == 1 and demo_dict['DELAYED'] == 0:
            false_positives = false_positives + 1
    recall = true_positives/(true_positives + false_negatives)
    precision = true_positives / (true_positives + false_positives)
    f1 = (2 * recall * precision)/(recall + precision)
    print("\n\n\nRECALL: ", recall)
    print("PRECISION: ", precision)
    print("F1 Score", f1)


def main_function():
    airlines = read_csv("ENDOFPREPROC.csv")
    airlines_test = read_csv("training_set.csv")
    # drop old indices
    airlines.drop(airlines.columns[[0]], inplace=True, axis=1)
    airlines_test.drop(airlines_test.columns[[0]], inplace=True, axis=1)

    used_vars = ['DELAYED']
    tree = (create_tree(dataset=airlines, used_vars=used_vars, curr_node=None, path=[], tree=[]))

    # RECALL AND PRECISION TEST
    calc_prec_recall(airlines, tree)
    # search_one_point(airlines_test, tree)


start = time.time()
main_function()
end = time.time()
print("\nELAPSED TIME: ", end-start)
