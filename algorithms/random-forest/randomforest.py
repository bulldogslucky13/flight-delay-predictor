from random import seed, sample
from random import randrange
from math import sqrt
import numpy as np
import pandas as pd
import time
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score


# Split a dataset into k folds
def split_k_folds(dataset, k_folds):
	dataset_split = list()
	dataset_copy = list(dataset)
	fold_size = int(len(dataset) / k_folds)
	for i in range(k_folds):
		fold = [dataset_copy.pop(randrange(len(dataset_copy))) for _ in range(fold_size)]
		dataset_split.append(fold)
	return dataset_split



# Evaluate an algorithm using a cross validation
def run_predictions(dataset, algorithm, n_folds, *args):
	folds = split_k_folds(dataset, n_folds)
	prediction_values = list()
	for fold in folds:
		train_set = list(folds)
		train_set.remove(fold)
		train_set = sum(train_set, [])
		test_set = list()
		for row in fold:
			row_copy = list(row)
			test_set.append(row_copy)
			row_copy[-1] = None
		predicted = algorithm(train_set, test_set, *args)
		actual_value = [row[-1] for row in fold]
		prediction_values.append((actual_value, predicted))
	return prediction_values

# Split a dataset based on an attribute and an attribute value
def test_split(index, value, dataset):
	left, right = list(), list()
	for row in dataset:
		if row[index] < value:
			left.append(row)
		else:
			right.append(row)
	return left, right

# Calculate the Gini index for a split dataset
def gini_index(groups, classes):
	n_instances = float(sum([len(group) for group in groups]))
	# sum weighted Gini index for each group
	gini = 0.0
	for group in groups:
		size = float(len(group))
		if size == 0:
			continue
		score = 0.0
		for class_val in classes:
			p = [row[-1] for row in group].count(class_val) / size
			score += p * p
		gini += (1.0 - score) * (size / n_instances)
	return gini

# Select the best split for a dataset
def get_split(dataset, n_features):
	class_values = list(set(row[-1] for row in dataset))
	b_index, b_value, b_score, b_groups = 999, 999, 999, None

	features = sample(range(len(dataset[0])-1), n_features)
 
	for index in features:
		for row in dataset:
			groups = test_split(index, row[index], dataset)
			gini = gini_index(groups, class_values)
			if gini < b_score:
				b_index, b_value, b_score, b_groups = index, row[index], gini, groups
	return {'index':b_index, 'value':b_value, 'groups':b_groups}

# Create a leaf
def to_leaf_node(group):
	outcomes = [row[-1] for row in group]
	return max(set(outcomes), key=outcomes.count)

# Create child splits for a node or make leaf
def split(node, max_depth, min_size, n_features, depth):
	left, right = node['groups']
	del(node['groups'])
	# check for a no split
	if not left or not right:
		node['left'] = node['right'] = to_leaf_node(left + right)
		return
	# check for max depth
	if depth >= max_depth:
		node['left'], node['right'] = to_leaf_node(left), to_leaf_node(right)
		return
	# left child
	if len(left) <= min_size:
		node['left'] = to_leaf_node(left)
	else:
		node['left'] = get_split(left, n_features)
		split(node['left'], max_depth, min_size, n_features, depth+1)
	# right child
	if len(right) <= min_size:
		node['right'] = to_leaf_node(right)
	else:
		node['right'] = get_split(right, n_features)
		split(node['right'], max_depth, min_size, n_features, depth+1)

def build_tree(train, max_depth, min_size, n_features):
	root = get_split(train, n_features)
	split(root, max_depth, min_size, n_features, 1)
	return root

# Predict if a row with the tree node.
def predict(node, row):
	if row[node['index']] < node['value']:
		if isinstance(node['left'], dict):
			return predict(node['left'], row)
		else:
			return node['left']
	else:
		if isinstance(node['right'], dict):
			return predict(node['right'], row)
		else:
			return node['right']

# Create subset of dateset by ratio
def subsample(dataset, ratio):
	sample = list()
	n_sample = round(len(dataset) * ratio)
	while len(sample) < n_sample:
		index = randrange(len(dataset))
		sample.append(dataset[index])
	return sample

# Make a prediction with a list of bagged trees
def bagging_predict(trees, row):
	predictions = [predict(tree, row) for tree in trees]
	return max(set(predictions), key=predictions.count)

# Random Forest Algorithm
def random_forest(train, test, max_depth, min_size, sample_size, n_trees, n_features):
	trees = list()
	for i in range(n_trees):
		sample = subsample(train, sample_size)
		tree = build_tree(sample, max_depth, min_size, n_features)
		trees.append(tree)
	predictions = [bagging_predict(trees, row) for row in test]
	return(predictions)

start = time.time()
# Test the random forest algorithm
seed(5)
filename = 'processed_data.csv'
dataset = pd.read_csv(filename).to_numpy().tolist()

#run the random forest
n_folds = 3
max_depth = 6
min_size = 5
sample_size = 0.5
n_features = int(sqrt(len(dataset[0])-1))
for n_trees in [1, 3, 5]:
    
	#get pairs of 
	predictions = run_predictions(dataset, random_forest, n_folds, max_depth, min_size, sample_size, n_trees, n_features)

	precision_scores = [precision_score(actual, predicted, average='binary') for (actual, predicted) in predictions]

	recall_scores = [recall_score(actual, predicted, average='binary') for (actual, predicted) in predictions]

	f1_scores = [f1_score(actual, predicted, average='binary') for (actual, predicted) in predictions]
 
	print('Trees: %d-----------------------' % n_trees)
	print('Precision score: %s' % precision_scores)
	print('Mean precision: %.3f' % (sum(precision_scores)/float(len(precision_scores))))
 
	print('Recall scores: %s' % recall_scores)
	print('Mean recall: %.3f' % (sum(recall_scores)/float(len(recall_scores))))
 
	print('f1 scores: %s' % f1_scores)
	print('Mean f1: %.3f' % (sum(f1_scores)/float(len(f1_scores))))
end = time.time()
#calculate running time for random forest algorithm
print(f'total takes {end - start}')