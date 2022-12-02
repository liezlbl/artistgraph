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
        self.__temp_collaborators.clear()
        collaborators: List[dict] = []
        collab_ids: List[int] = []
        try:
            artist = self.__dc.artist(aid)
            releases = artist.releases
            if releases is not None:
                for release in releases:
                    if hasattr(release, "year"):
                        if 0 < release.year <= year:
                            # access individual release object
                            release_id = release.id
                            r = self.__dc.release(release_id)
                            # check release->artists attribute
                            if hasattr(r, "artists"):
                                if r.artists is not None:
                                    for ra in r.artists:
                                        if ra.id != aid:
                                            # make collab dict
                                            collab_info = {
                                                "collaboratorID": ra.id,
                                                "collaboratorName": ra.name,
                                                "releaseID": r.id,
                                                "roles": ra.fetch("role")
                                            }
                                            if ra.id not in collab_ids and ra.id != aid:
                                                # append collab dict to list
                                                self.__temp_collaborators.append(collab_info)
                                                collaborators = self.__temp_collaborators
                                                collab_ids.append(ra.id)
                            # check release->extraartists attribute
                            if hasattr(r, "extraartists"):
                                if r.extraartists is not None:
                                    for e in r.extraartists:
                                        collab_info = {
                                            "collaboratorID": e.id,
                                            "collaboratorName": e.name,
                                            "releaseID": r.id,
                                            "roles": e.fetch("role")
                                        }
                                        if e.id not in collab_ids and e.id != aid:
                                            self.__temp_collaborators.append(collab_info)
                                            collaborators = self.__temp_collaborators
                                            collab_ids.append(e.id)
                            # check release->tracklist->"extraartists" attribute
                            if hasattr(r, "tracklist") and r.tracklist is not None:
                                for t in r.tracklist:
                                    ea = t.fetch("extraartists")
                                    if ea is not None:
                                        for a in ea:
                                            collab_info = {
                                                "collaboratorID": a['id'],
                                                "collaboratorName": a['name'],
                                                "releaseID": r.id,
                                                "roles": [a['role']]
                                            }
                                            if a["id"] not in collab_ids and a["id"] != aid:
                                                self.__temp_collaborators.append(collab_info)
                                                collaborators = self.__temp_collaborators
                                                collab_ids.append(a["id"])
            # create artist dictionary
            artist_dict = {
                "artistID": artist.id,
                "artistName": artist.name,
                "realname": artist.real_name,
                "profile": artist.profile,
                # returns list of collaborator dicts
                "collaborators": collaborators,
                'level': 0
            }
        # handle exception
        except HTTPError:
            artist_dict = {
                "artistID": aid
            }
            raise ArtistNotFound("No artists found", 404)
        return artist_dict

    def get_artists_from_list(self, a_list: list[int], year: int = 1935) -> list[dict]:
        """
        Get all the artists from Discogs based on the input list of int ids
        :param a_list: list of integer ids
        :param year: year filter
        """
        result: List[dict] = []
        for i in a_list:
            a = self.get_artist_by_id(i, year)
            if a is not None:
                result.append(a)
        if not result:
            raise ArtistNotFound("No artists found", 404)
        else:
            return result
