from typing import List
from multipledispatch import dispatch
import discogs_client
from datalayer.artistnotfound import ArtistNotFound
from applayer.artist import Artist
from discogs_client.exceptions import HTTPError


class DiscogsBridge(object):
    @dispatch(str, str)
    def __init__(self, key: str, secret: str):
        self.__temp_collaborators: list[dict] = []
        self.__dc: discogs_client.Client = discogs_client.Client(
            'CSC2310_Lecture/1.0',
            consumer_key=key,
            consumer_secret=secret
        )

    @dispatch()
    def __init__(self):
            key = "YsjDzHkEyasXAQGNHOMa"
            secret = "QQXsuuwTXkzmBjlgIyiQXedlcuvCXroX"
            self.__temp_collaborators: list[dict] = []

            self.__dc: discogs_client.Client = discogs_client.Client(
                'CSC2310_Lecture/1.0',
                consumer_key=key,
                consumer_secret=secret
            )

    def get_artist_by_id(self, aid: int, year: int = 1935) -> dict:
        """
        Get a dictionary of information about an artist from Discogs
        :param aid: artist id
        :param year: optional year
        :return: dictionary with artist info
        :raises: ArtistNotFound if the artist is not found in Discogs
        """
        try:
            artist = self.__dc.artist(aid)
            # collaborators = []
            # releases = artist.releases
            # for r in releases:
            #     if hasattr(r, "year"):
            #         if r.year < year:
            #             if hasattr(r, "artists"):
            #                 for a in r.artists:
            #                     aa = a.fetch("artists")
            #                     if a.id != aid and aa is not None:
            #                         for p in aa:
            #                             collab_info = {
            #                                 "collaboratorID": p["id"],
            #                                 "collaboratorName": p["name"],
            #                                 "releaseID": r.id,
            #                                 "roles": p["role"]
            #                             }
            #                             if collab_info not in collaborators and collab_info["collaboratorID"] != aid:
            #                                 collaborators.append(collab_info)
            #             if hasattr(r, "extraartists"):
            #                 for ea in r. extraartists:
            #                     ee = ea.fetch("extraartists")
            #                     if ea.id != aid and ee is not None:
            #                         for e in ee:
            #                             collab_info = {
            #                                 "collaboratorID": e["id"],
            #                                 "collaboratorName": e["name"],
            #                                 "releaseID": r.id,
            #                                 "roles": e["role"]
            #                             }
            #                             if collab_info not in collaborators and collab_info["collaboratorID"] != aid:
            #                                 collaborators.append(collab_info)
            #             if hasattr(r, "tracklist"):
            #                 for t in r.tracklist:
            #                     ea = t.fetch("extraartists")
            #                     if ea is not None:
            #                         for a in ea:
            #                             collab_info = {
            #                                 "collaboratorID": a["id"],
            #                                 "collaboratorName": a["name"],
            #                                 "releaseID": r.id,
            #                                 "roles": a["role"]
            #                             }
            #                             if collab_info not in self.__temp_collaborators and collab_info["collaboratorID"] != aid:
            #                                 collaborators.append(collab_info)
            #                                 self.__temp_collaborators = collaborators
            artist_dict = {
                "artistID": artist.id,
                "artistName": artist.name,
                "realname": artist.real_name,
                "profile": artist.profile,
                # "collaborators": self.__temp_collaborators,
                'level': 0
                }
        except HTTPError:
        #     # artist_dict = {
        #     #     "artistID": aid
        #     # }
            raise ArtistNotFound("Error Code", 404)

        return artist_dict

    # def get_artists_from_list(self, a_list: list[int], year: int = 1935) -> list[dict]:
    #     """
    #     Get all the artists from Discogs based on the input list of int ids
    #     :param a_list: list of integer ids
    #     :param year: year filter
    #     """
    #     result: List[dict] = []
    #     for i in a_list:
    #         a = self.get_artist_by_id(i, year)
    #         if a is not None:
    #             result.append(a)
    #     if not result:
    #         raise ArtistNotFound("No artists found", 404)
    #     else:
    #         return result



