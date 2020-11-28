#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is an implementation of the FP Growth Algorithm [10],
which attempts to make a compressed form of a transaction database
that can be held in memory and can by efficiently used for searching
for frequent itemsets.

There are a variety of constraints that can be applied in association
rule learning, including support, confidence, life, conviction, leverage,
collective strength, and all-confidence [4]. However, this implementation only
uses support which has the downward closure property.

This implementation uses a recursive rather than iterative approach to searching
the space of possible projected trees. One of the tradeoffs here is that the
recursive approach can take up a lot of memory compared to iteratively-
generating the trees. Python has a recursion depth limit, meaning that a
function can only occur on the current call stack a finite number of times.

GNU General Public License v3.0
Permissions of this strong copyleft license are conditioned on making available complete source
code of licensed works and modifications, which include larger works using a licensed work, under
the same license.
Copyright and license notices must be preserved.
Contributors provide an express grant of patent rights.


Reference Material:
[1]: https://en.wikipedia.org/wiki/Suffix_tree
[2]: https://en.wikipedia.org/wiki/Generalized_suffix_tree
[3]: https://www.geeksforgeeks.org/pattern-searching-using-suffix-tree/
[4]: https://en.wikipedia.org/wiki/Association_rule_learning#FP-growth_algorithm
[5]: https://en.wikipedia.org/wiki/Trie
[6]: https://en.wikipedia.org/wiki/Search_tree
[7]: https://en.wikipedia.org/wiki/Tree_(data_structure)
[8]: https://en.wikipedia.org/wiki/Node_(computer_science)
[9]: https://en.wikipedia.org/wiki/Recursion#In_computer_science
[10]: https://dl.acm.org/doi/10.1145/342009.335372
[11]: https://www.softwaretestinghelp.com/fp-growth-algorithm-data-mining/
[12]: https://en.wikibooks.org/wiki/Data_Mining_Algorithms_In_R/Frequent_Pattern_Mining/The_FP-Growth_Algorithm
[13]: https://www.youtube.com/watch?v=yCbankIouUU&ab_channel=StudyKorner
[14]: http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/
[15]: https://spark.apache.org/docs/latest/ml-frequent-pattern-mining.html
[16]: https://dl.acm.org/doi/10.1145/1454008.1454027
[17]: https://towardsdatascience.com/fp-growth-frequent-pattern-generation-in-data-mining-with-python-implementation-244e561ab1c3
[18]: https://github.com/chonyy/fpgrowth_py
[19]: https://medium.com/@saurav.agg19/implement-trie-prefix-tree-692560ea448a
'''

__author__ = 'Galen M. Seilis'
__copyright__ = 'Copyright 2020, Assignment 2, CPSC-673-A1'
__credits__ = ['Galen Seilis', 'Fan Jiang (Instructor)']
__license__ = 'GNU General Public License v3.0'
__version__ = '0.1.0'
__maintainer__ = 'Galen Seilis'
__email__ = 'seilis@unbc.ca'
__status__ = 'School Project'

# Standard Imports
import argparse
from collections import Counter
from time import ctime

def get_db_size(file_name):
    '''
    This function gets the number of transactions
    from the transaction database by reading and
    returning only the first line of the file.

    This function is intended to be run only once
    at the beginning of a frequent pattern mining
    algorithm.

    Make sure that the first line of the transaction
    database is suitable for this purpose.

    ARGUMENTS
        file_name (str): The name of the transaction database file.

    RETURNS
        (int): Number of transactions in transaction database.
    '''
    with open(file_name) as file_io:
        return int(file_io.readline().rstrip())

def clean_line(line):
    '''
    This helper function parses a line from the
    transaction database.

    ARGUMENTS
        line (str): A line from the transaction database.

    RETURNS
        t_id (int): The transaction identifier.
        t_n (int): The number of items in the transaction.
        t_set (frozenset[int]): The set of items as integers in the transaction.
    '''
    t_id, t_n, t_set = line.rstrip().split('\t')
    t_id = int(t_id)
    t_n = int(t_n)
    t_set = frozenset([int(i) for i in t_set.split(' ')])
    return t_id, t_n, t_set

def scan_db(file_name):
    '''
    This generator yields each transaction from the
    transaction database.

    ARGUMENTS
        file_name (str): The name of the transaction database file.

    RETURNS
        generator

    YIELDS
        (int, int, set[int]): Transaction from transaction database file.
    '''
    with open(file_name) as file_io:
        for i, line in enumerate(file_io):
            if i != 0:
                yield clean_line(line)
            else:
                continue

def first_scan(file_name, epsilon):
    '''
    This function perfoms the first database scan
    for the apriori frequent pattern mining algorithm.

    Compared to the function later_scan, first_scan will
    assume that all items are candidates while later_scan
    will assume that the candidates are provided.

    ARGUMENTS
        file_name (str): The name of the transaction database file.
        epsilon (float/int): Absolute minimum support threshold.

    RETURNS
        (dict): A support table of each item in the database.
    '''
    supporter = Counter()
    transactions = []
    for t_line in scan_db(file_name):
        t_set = t_line[-1]
        transactions.append(t_set)
        supporter += Counter(t_set)
    l_table = {k: v for k, v in sorted(supporter.items(),
                                       key=lambda item: item[1],
                                       reverse=True) if v >= epsilon}
    transactions = [frozenset([item for item in trans if item in l_table.keys()])\
                    for trans in transactions]
    return l_table, transactions


class FPNode:
    '''
    This class defines the nodes in FPTree classes
    used in the FP-Growth algorithm. While the data
    structure is nominally a tree, the nodes are
    linked both by parent-child edges but also by
    additional edges that I have termed "links". The
    the set of all links induces a graph of what I call
    the hyperlinks.
    '''
    def __init__(self, tree, item, support=1):
        '''
        ARGUMENTS
            tree (FPTree): The tree this node is being inserted into.
            item (int): The id for the item this node represents.
            support (int): Frequency of the item this node represents.

        RETURNS
            None
        '''
        self.tree = tree
        self.item = item
        self.support = support
        self.parent = None
        self.children = {}
        self._link = None

    def add(self, child):
        """
            This method assigns an FPNode to be this child of
            self.

            ARGUMENTS
                child (FPNode[object]): FPNode to be assigned as child of self.

            RETURNS
                None
        """

        if not child.item in self.children:
            self.children[child.item] = child
            child.parent = self

    def search(self, item):
        '''
        This function returns the children of a given
        node if the item exists in the children keys.

        ARGUMENTS
            item (int): Query item.

        RETURNS
            self.children[item]: Children associated with item.
        '''
        if item in self.children.keys():
            return self.children[item]
        return None

    def increment_node_support(self):
        '''
        This method increments the support of the item this node represents.

        ARGUMENTS
            None

        RETURNS
            None
        '''
        self.support += 1

    @property
    def root(self):
        '''
        This method indicates whether self is the root of
        an FPTree. The root node is identified by how it is
        operationally defined. It doesn't represent an item,
        so node.item should be None. And since the root doesn't
        represent an item, it doesn't have a support

        ARGUMENTS
            None

        RETURNS
            (bool): Whether the FPNode is the root of its FPTree.
        '''
        return self.item is None and self.support is None

    @property
    def link(self):
        '''
        This method gives the next node in the
        hyperlinked graph.

        ARGUMENTS
            None

        RETURNS
            _link (int): Next node in hyperlink graph.
        '''
        return self._link

    @link.setter
    def link(self, value):
        '''
        This method sets the next node in the hyperlinked
        graph.

        ARGUMENTS
            value (int): Node query.

        RETURNS
            None
        '''
        self._link = value

class FPTree:
    '''
    This class defines the frequent pattern trees used for the
    FP growth algorithm. This class is used for both the initial tree,
    as well as the subsequent projected trees.
    '''

    def __init__(self):
        '''
        This initialization sets the root of the tree to have None
        for item and None for count. It also initializes the hyperlink
        dictionary that keeps track of the links between nodes that are
        not formally parent:child relationships.
        '''
        self.root = FPNode(self, None, None)
        self.hyperlinks = {}

    def add_transaction(self, itemset):
        """
        This method adds a transaction to the prefix tree.

        ARGUEMNTS
            itemset (iterable[int]): transaction to be added to prefix tree.

        RETURNS
            None
        """
        point = self.root

        for item in itemset:
            next_point = point.search(item)
            if next_point:
                next_point.increment_node_support()
            else:
                next_point = FPNode(self, item)
                point.add(next_point)
                self.update_route(next_point)
            point = next_point

    def update_route(self, point):
        """
        This method extends the route to a given item, including all
        nodes that form a connected path to it.

        ARGUMENTS
            point (int): An item to extend to.

        RETURNS
            None
        """
        if point.item in self.hyperlinks.keys():
            route = self.hyperlinks[point.item]
            route[1].link = point
            self.hyperlinks[point.item] = route[0], point
        else:
            self.hyperlinks[point.item] = (point, point)

    def items(self):
        '''
        This method generates tuples of which items
        are paired with which nodes. Note that a
        given item may be associated with multiple nodes,
        but a given node is associated with only one
        item.

        ARGUMENTS
            None

        RETURNS
            (generator object)

        YIELDS
            (item, node)
                item (int): An item in the tree.
                node (int): A node in the tree.
        '''
        for item in self.hyperlinks:
            yield item, self.nodes(item)

    def nodes(self, item):
        '''
        ARGUMENTS
            item (int): Initial node in hyperlink graph.

        RETURNS
            (generator object)

        YIELDS
            node (FPNode): Next node in hyperlink path.
        '''
        if item in self.hyperlinks:
            node = self.hyperlinks[item][0]
        while node:
            yield node
            node = node.link

    def prefix_paths(self, item):
        '''
        This method gets the paths

        NOTE
            These are paths within the tree that follow
            the parent:child relations.

        ARGUMENTS
            item (int): An item in the FPTree.

        RETURNS
            All paths for that contain a nodes for a given item.
        '''
        paths = []
        for node in self.nodes(item):
            path = []
            while not node.root and node:
                path = [node] + path
                node = node.parent
            paths.append(path)
        return paths

def fp_search(tree, epsilon, suffix=None):
    '''
    This function performs a recursive search
    through the space of projected trees, and limits
    the scope of the search by checking for the support
    of the trees in the itemset it represents. It also
    yields the frequent itemsets while the search is
    being performed.

    WARNING: It is possible to go over Python's built-in
    recursion depth limit using this function. Whether this
    happens will depend upon the size of the dataset.

    ARGUMENTS
        tree (FPTree[object]): An FPTree (initial, or projected).
        epsilon (int): The minimum support threshold.
        suffix (iterable, mutable): A suffix corresponding to the input tree (default: None, i.e. "root")

    RETURNS
        (generator object)

    YIELDS
        freq_items (list): Frequent items discovered in search.
        tree_support (int): Support of items in current tree.
    '''
    suffix = [] if suffix is None else suffix
    for item, nodes in tree.items():
        tree_support = sum(n.support for n in nodes)
        if tree_support >= epsilon and item not in suffix:
            freq_items = [item] + suffix
            yield freq_items, tree_support
            proj_tree = project(tree.prefix_paths(item))
            for freq_items, tree_support in fp_search(proj_tree, epsilon, freq_items):
                yield freq_items, tree_support
        else:
            continue

def project(paths):
    '''
    This function constructs a projected tree
    given the item paths from a 'parent tree'.

    ARGUMENTS
        paths (iterable): The sequence of items from another tree.

    RETURNS
        tree (FPTree[object]): A FPTree object projected by the given item sequence.
    '''
    itemset = set()
    seed = False
    new_tree = FPTree()

    for path in paths:
        if not bool(seed):
            seed = path[-1].item
        else:
            pass

        current_node = new_tree.root
        for node in path:
            next_current_node = current_node.search(node.item)
            if not next_current_node:
                itemset.add(node.item)
                if node.item == seed:
                    support = node.support
                else:
                    support = 0
                next_current_node = FPNode(new_tree, node.item, support)
                current_node.add(next_current_node)
                new_tree.update_route(next_current_node)
            else:
                pass
            current_node = next_current_node

    for path in new_tree.prefix_paths(seed):
        support = path[-1].support
        for node in path[:-1][::-1]:
            node.support += support

    return new_tree

def write_rules(file_out, rules):
    '''
    This function writes the discovered
    frequent patterns into a text file.

    ARGUMENTS
        file_out (str): The output file name of frequent patterns.
        rules (dict[frozenset[int]:int]): Dictionary of all frequent patterns found by the algorithm.

    RETURNS
        None
    '''
    with open(file_out, 'w') as file:
        count = 0
        lines = []
        for (itemset, support) in rules.items():
            count += 1
            if isinstance(itemset, int):
                itemstr = str(itemset)
            else:
                itemstr = str(set(itemset)).replace('{', '').replace('}', '')
            line = f'{itemstr} : {support}\n'
            lines.append(line)
        file.write(f'|FPs| = {count}\n')
        print(f'|FPs| = {count}\n')
        for line in lines:
            file.write(line)

if __name__ == '__main__':
    # Prepare command line PARSER
    PARSER = argparse.ArgumentParser()
    PARSER.description = '''A CLI that performs the FP-Growth pattern learning algorithm.
    This program expects an input text file with a particular format.
    The first line of the input file should be the number of transactions in the transaction database.
    All subsequent lines are expected to have a tab-delimited format where the first column is the transaction ID,
    the second column is the number of items in the transaction, and the third column is a space-delimited set of items.
    Failure to format the input file correctly may result in errors or unexpected behaviour.'''
    REQUIRED = PARSER.add_argument_group('required arguments')
    REQUIRED.add_argument("-i",
                          "--in_file",
                          type=str,
                          required=True,
                          help="Input data file.")
    PARSER.add_argument("-o",
                        "--out_file",
                        type=str,
                        default="MiningResults.txt",
                        help="Output results file. (default='MiningResults.txt')")
    PARSER.add_argument("-m",
                        "--min_supp",
                        type=float,
                        default=0.5,
                        help="Minimum support threshold as a float between 0 and 1. (default=0.5)")
    ARGS = PARSER.parse_args()

    # Check validity of CLI arguments
    assert 0 <= ARGS.min_supp <= 1
    EPSILON = ARGS.min_supp * get_db_size(ARGS.in_file)

    print(ctime(), 'Performing first database scan...')
    L1, TRANSACTIONS = first_scan(ARGS.in_file, EPSILON)

    START_TREE = FPTree()

    print(ctime(), 'Building initial tree...')
    for transaction in TRANSACTIONS:
        START_TREE.add_transaction(transaction)

    del TRANSACTIONS

    print(ctime(), 'Finding frequent patterns...')
    RULES = {}
    for fset in fp_search(START_TREE, EPSILON):
        if len(fset[0]) == 1:
            RULES[frozenset((fset[0][0], ))] = fset[1]
        else:
            RULES[frozenset(fset[0])] = fset[1]

    print(ctime(), 'Writing frequent patterns to file...')
    write_rules(ARGS.out_file, RULES)
