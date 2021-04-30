import copy
from collections import defaultdict, deque


def pytest_collection_modifyitems(session, config, items):
    return order_tests_plugin.pytest_collection_modifyitems(session, config, items)


def pytest_configure(config):
    return order_tests_plugin.pytest_configure(config)


class OrderTestsPlugin:
    AFTER = 'after'
    BEFORE = 'before'

    def __init__(self):
        self.items_to_sort = {}
        self.test_names_to_nodeid = defaultdict(list)

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f"{self.AFTER}(list): list of tests that precede given test")
        config.addinivalue_line('markers', f"{self.BEFORE}(list): list of tests that follow given test")

    def _get_neighbours(self, item, marker_name):
        order_ids = list(item.iter_markers(name=marker_name))
        return list(set([arg for order_id in order_ids for arg in order_id.args]))

    def get_predecessors(self, item):
        return self._get_neighbours(item, self.AFTER)

    def get_followers(self, item):
        return self._get_neighbours(item, self.BEFORE)

    def to_nodeid(self, test_marker):
        # fast try
        if test_marker in self.test_names_to_nodeid.keys():
            assert (
                len(self.test_names_to_nodeid[test_marker]) <= 1
            ), f"ambiguous marker: {test_marker}! Possible choices are: {self.test_names_to_nodeid[test_marker]}"
            assert self.test_names_to_nodeid[test_marker], "https://xkcd.com/2200/"
            return self.test_names_to_nodeid[test_marker][0]

        # linear try
        candidate = None
        for nodeid in self.items_to_sort.keys():
            if nodeid.endswith(test_marker):
                assert not candidate, f"ambiguous marker {test_marker}! Possible choices are: {[candidate, nodeid]}"
                candidate = nodeid

        assert candidate, f'no candidate found for {test_marker}!!'
        return candidate

    def sort_DAG(self):
        edges = defaultdict(list)
        inverted_edges = defaultdict(list)
        no_incoming = set(self.items_to_sort.keys())

        for nodeid, item in self.items_to_sort.items():

            for predecessor in self.get_predecessors(item):
                predecessor_nodeid = self.to_nodeid(predecessor)
                edges[predecessor_nodeid].append(nodeid)
                inverted_edges[nodeid].append(predecessor_nodeid)
                if nodeid in no_incoming:
                    no_incoming.remove(nodeid)

            for follower in self.get_followers(item):
                follower_nodeid = self.to_nodeid(follower)
                edges[nodeid].append(follower_nodeid)
                inverted_edges[follower_nodeid].append(nodeid)
                if follower_nodeid in no_incoming:
                    no_incoming.remove(follower_nodeid)

        # https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm
        L = []
        S = deque(sorted(list(no_incoming)))  # any container will do here, but use deque for keeping tests sorted

        while S:
            n = S.popleft()
            L.append(n)
            neighbors = copy.copy(edges[n])
            for m in neighbors:
                edges[n].remove(m)
                inverted_edges[m].remove(n)
                if not inverted_edges[m]:
                    S.append(m)

        for nodeid in edges.keys():
            assert not edges[nodeid], f"cycle detected! {edges}"

        return [self.items_to_sort[order_id] for order_id in L]

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            self.items_to_sort[item.nodeid] = item
            self.test_names_to_nodeid[item.name].append(item.nodeid)

        items[:] = self.sort_DAG()


order_tests_plugin = OrderTestsPlugin()
