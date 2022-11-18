from typing import List, Tuple
from applayer.artist import Artist
from multipledispatch import dispatch
from applayer.graphbase import GraphBase
from applayer.artistlist import ArtistList
from datalayer.mongobridge import MongoBridge
from applayer.collaboration import Collaboration
from datalayer.artistnotfound import ArtistNotFound
import networkx as nx
from networkx.algorithms import degree_centrality, closeness_centrality, betweenness_centrality
from datalayer.discogsbridge import DiscogsBridge


class ArtistGraph(GraphBase):
    """
    This class implements creation of a graph.
    """
    @dispatch()
    def __init__(self) -> None:
        super().__init__()
        self.__artists: List[Artist] = []
        self.__collaborations: List[Collaboration] = []
        self.__expansion: List[Artist] = []
        self.__mb = MongoBridge()

    @dispatch(ArtistList, int)
    def __init__(self, artist_list: ArtistList, depth: int) -> None:
        """
        Constructor for the ArtistGraph class; The graph is generated by recursively searching
        for collaborators of an artist
        :param artist_list: List of root nodes for the graph
        :param depth: Number of levels to be visualized in the graph
        """
        super().__init__()
        self.__artists: List[Artist] = []
        self.__collaborations: List[Collaboration] = []
        self.__expansion: List[Artist] = []
        self.__mb = MongoBridge()

        node_queue = [] + artist_list.artist_objects

        # Iterate through the queue and find the collaborators
        level = 0
        for node in node_queue:
            self.add_artist(node)
            if level <= depth and node.collaborators is not None:
                for coll in node.collaborators:
                    level = node.level + 1
                    # Find the collaborator in the database or create it
                    # Add the collaborator to the graph ONLY if the node isn't
                    # already in the graph; only add if the level is <= depth
                    collaborator, roles = self.__get_collaborator(coll, level)
                    if not self.has_node(collaborator):
                        self.add_artist(collaborator)
                        node_queue.append(collaborator)

                    # Add the collaboration/edge to the graph
                    collaboration = Collaboration(node, collaborator, roles)
                    self.add_collaboration(collaboration)

    @property
    def artists(self) -> List[Artist]:
        return self.__artists

    @property
    def collaborations(self) -> List[Collaboration]:
        return self.__collaborations

    def add_collaboration(self, collab: Collaboration) -> None:
        """
        Checks to see if the edge already exists in the graph by using the super class method has_edge
        If the edge is not in the graph already, add it using add_edge; otherwise, use incr_edge to modify the weight
        of the edge
        :param collab: Add the collaboration edge to the graph
        """
        if not super().has_edge(collab.artist0, collab.artist1):
            self.__collaborations.append(collab)
            super().add_edge(collab.artist0, collab.artist1)
        else:
            super().incr_edge(collab.artist0, collab.artist1)

    def add_artist(self, artist: Artist) -> None:
        """
        Add the artist to the __artist list, add the node to the graph by using the superclass add_node operation
        :param artist: Artist object to be added to graph
        """
        if not super().has_node(artist):
            self.__artists.append(artist)
            super().add_node(artist)

    def compute_degree_centrality(self):
        """
        Compute the degree centrality of the graph
        """
        pass

    def compute_closeness_centrality(self):
        """
        Compute the closeness centrality of the graph
        """
        pass

    def compute_betweenness_centrality(self):
        """
        Compute the betweenness centrality of the graph
        """
        pass

    def __get_collaborator(self, coll: dict, level: int) -> Tuple[Artist, List]:
        """
        This is a convenience method and doesn't need to be implemented as part of the class
        :param self:
        :param coll:
        :param level:
        :return:
        """
        try:
            raw_artist = self.__mb.get_artist_by_id(coll['collaboratorID'])
            collaborator = Artist(raw_artist)
            collaborator.level = level
        except ArtistNotFound:
            collaborator = Artist(coll['collaboratorID'], coll['collaboratorName'], coll['collaboratorName'], "", level)
            if collaborator not in self.__expansion:
                self.__expansion.append(collaborator)
        roles = coll['roles']
        return collaborator, roles

    def get_expansion_list(self) -> List[Tuple[int, str]]:
        result: List[Tuple[int, str]] = []
        for i in self.__expansion:
            result.append((i.artistID, i.artistName))
        result.sort(key=lambda x: x[1])
        return result

    def expand_graph(self, aid: int):
        try:
            self.__mb.get_artist_by_id(aid)
        except ArtistNotFound:
            db = DiscogsBridge()
            artist_dictionary = db.get_artist_by_id(aid)
            self.__mb.add_artist(artist_dictionary)
