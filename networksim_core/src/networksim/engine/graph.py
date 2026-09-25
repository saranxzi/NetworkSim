"""SimGraph class."""
from typing import List, Tuple
import igraph

class SimGraph:
    __slots__ = ['_g', '_name_to_idx', '_idx_to_name', '_topo_order',
                 '_predecessors_map', '_successors_map']

    def __init__(self, node_ids: List[str], edges: List[Tuple[str, str]]):
        self._g = igraph.Graph(directed=True)
        self._g.add_vertices(len(node_ids))
        self._name_to_idx = {name: idx for idx, name in enumerate(node_ids)}
        self._idx_to_name = {idx: name for idx, name in enumerate(node_ids)}

        edge_indices = [(self._name_to_idx[src], self._name_to_idx[dst]) for src, dst in edges]
        self._g.add_edges(edge_indices)

        try:
            self._topo_order = [self._idx_to_name[i] for i in self._g.topological_sorting()]
        except igraph.InternalError:
            self._topo_order = [self._idx_to_name[i] for i in self._g.bfs(0)[0]]

        # Precompute adjacency lists once — graph is static during simulation.
        # Eliminates O(V) list allocation per predecessors/successors call.
        self._predecessors_map = {
            name: [self._idx_to_name[i] for i in self._g.predecessors(idx)]
            for name, idx in self._name_to_idx.items()
        }
        self._successors_map = {
            name: [self._idx_to_name[i] for i in self._g.successors(idx)]
            for name, idx in self._name_to_idx.items()
        }

    @property
    def topo_order(self) -> List[str]:
        return self._topo_order

    def predecessors(self, node_name: str) -> List[str]:
        return self._predecessors_map[node_name]

    def successors(self, node_name: str) -> List[str]:
        return self._successors_map[node_name]
