import httpx
from httpx_retries import Retry, RetryTransport

import swcpy.swc_config as config
from .schemas import League, Team, Player, Performance, Counts
from typing import List
import backoff
import logging

logger = logging.getLogger(__name__)


class SWCClient:
    """Interacts with the SportsWorldCentral API.

        This SDK class simplifies the process of using the SWC Fantasy
        Football API. It supports all the functions of the SWC API and returns
        validated data types.

    Typical usage example:

        client = SWCClient()
        response = client.get_health_check()

    """

    HEALTH_CHECK_ENDPOINT = "/"
    LIST_LEAGUES_ENDPOINT = "/v0/leagues/"
    LIST_PLAYERS_ENDPOINT = "/v0/players/"
    LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"
    LIST_TEAMS_ENDPOINT = "/v0/teams/"
    GET_COUNTS_ENDPOINT = "/v0/counts/"

    BULK_FILE_BASE_URL = (
        'https://raw.githubusercontent.com/evrins/hands-on-api-data/main/bulk/'
    )

    def __init__(self, cfg: config.SWCConfig):
        logger.debug(f'Bulk file base URL: {self.BULK_FILE_BASE_URL}')
        logger.debug(f'Swc client configuration: {cfg}')

        self.base_url = cfg.swc_base_url
        self.backoff = cfg.swc_backoff
        self.backoff_max_time = cfg.swc_backoff_max_time
        self.bulk_file_format = cfg.swc_bulk_file_format

        self.BULK_FILE_NAMES = {
            'players': 'player_data',
            'leagues': 'league_data',
            'performances': 'performance_data',
            'teams': 'team_data',
            'team_players': 'team_player_data',
        }

        if self.backoff:
            exp_retry = Retry(
                max_backoff_wait=self.backoff_max_time,
                retry_on_exceptions=[httpx.RequestError, httpx.HTTPStatusError],
            )

            transport = RetryTransport(retry=exp_retry)

            self.http_client = httpx.Client(base_url=self.base_url, transport=transport)
        else:
            self.http_client = httpx.Client(base_url=self.base_url)

        # if self.backoff:
        #     self.call_api = backoff.on_exception(
        #         wait_gen=backoff.expo,
        #         exception=(httpx.RequestError, httpx.HTTPStatusError),
        #         max_time=self.backoff_max_time,
        #         jitter=backoff.random_jitter,
        #     )(self.__call_api)

        if self.bulk_file_format.lower() == 'parquet':
            ext = '.parquet'
        else:
            ext = '.csv'

        self.BULK_FILE_NAMES = {
            k: v + ext for k, v in self.BULK_FILE_NAMES.items()
        }

        logger.debug(f'Bulk file dictionary: {self.BULK_FILE_NAMES}')

    def call_api(self, endpoint: str, params: dict = None) -> httpx.Response:
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            logger.debug(f'base_url: {self.base_url}, endpoint: {endpoint}, params: {params}')
            response = self.http_client.get(endpoint, params=params)
            logger.debug(f'response in json: {response.json()}')
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f'HTTP status error occurred: {e.response.status_code} {e.response.text}')
            raise
        except httpx.RequestError as e:
            logger.error(f'Request error occurred: {str(e)}')
            raise

    def get_health_check(self) -> httpx.Response:
        """
        Checks if API is running and healthy.

        Calls the API health check endpoint and returns a standard message if the API is running normally.
        Can be used to check status of API before making more complicated API calls.

        :returns:
            A httpx.Response object that contains the HTTP status,
            JSON response and other information received from the API.
        """
        logger.debug('Getting health check endpoint...')
        endpoint = self.HEALTH_CHECK_ENDPOINT
        return self.call_api(endpoint)

    def list_leagues(self, skip: int = 0,
                     limit: int = 100,
                     min_last_changed_date: str = None,
                     league_name: str = None) -> List[League]:
        """
        Returns a List of Leagues filtered by parameters.

        Calls the API v0/leagues endpoint and returns a list of League objects.

        :returns:
            A List of schemas.League objects. Each represents one SportsWorldCentral fantasy league.

        """
        logger.debug('Listing leagues...')

        params = {
            "skip": skip,
            "limit": limit,
            "min_last_changed_date": min_last_changed_date,
            "league_name": league_name,
        }

        response = self.call_api(self.LIST_LEAGUES_ENDPOINT, params=params)
        return [League(**it) for it in response.json()]

    def get_league_by_id(self, league_id: int) -> League:
        """Returns a Leagues matching a league_id.

        Calls the API v0/leagues/{league_id} endpoint and returns single League.

        Returns:
        A schemas.League objects representing one SportsWorldCentral fantasy league.

        """
        logger.debug("Entered get league by ID")
        # build URL
        endpoint_url = f"{self.LIST_LEAGUES_ENDPOINT}{league_id}"
        # make the API call
        response = self.call_api(endpoint_url)
        response_league = League(**response.json())
        return response_league

    def get_counts(self) -> Counts:
        """Returns Counts of several endpoints.

        Calls the API v0/counts endpoint and returns a Counts object.

        Returns:
        Counts object representing counts of elements in the API.,

        """
        logger.debug("Entered get counts")

        response = self.call_api(self.GET_COUNTS_ENDPOINT)
        counts = Counts(**response.json())
        return counts

    def list_teams(
            self,
            skip: int = 0,
            limit: int = 100,
            min_last_changed_date: str = None,
            team_name: str = None,
            league_id: int = None,
    ):
        """Returns a List of Teams filtered by parameters.

        Calls the API v0/teams endpoint and returns a list of
        Team objects.

        Returns:
        A List of schemas.Team objects. Each represents one
        team in a SportsWorldCentral fantasy league.

        """

        logger.debug("Entered list teams")

        params = {
            "skip": skip,
            "limit": limit,
            "min_last_changed_date": min_last_changed_date,
            "team_name": team_name,
            "league_id": league_id,
        }
        response = self.call_api(self.LIST_TEAMS_ENDPOINT, params)
        return [Team(**team) for team in response.json()]

    def list_players(
            self,
            skip: int = 0,
            limit: int = 100,
            min_last_changed_date: str = None,
            first_name: str = None,
            last_name: str = None,
    ):
        """Returns a List of Players filtered by parameters.

        Calls the API v0/players endpoint and returns a list of
        Player objects.

        Returns:
        A List of schemas.Player objects. Each represents one
        NFL player.

        """
        logger.debug("Entered list players")

        params = {
            "skip": skip,
            "limit": limit,
            "min_last_changed_date": min_last_changed_date,
            "first_name": first_name,
            "last_name": last_name,
        }

        response = self.call_api(self.LIST_PLAYERS_ENDPOINT, params)
        return [Player(**player) for player in response.json()]

    def get_player_by_id(self, player_id: int):
        """Returns a Players matching the SWC Player ID.

        Calls the API v0/players/{player_id} endpoint and returns one Player object.

        Returns:
        A List of schemas.Player object representing an
        NFL player.

        """
        logger.debug("Entered get player by ID")

        # build URL
        endpoint_url = f"{self.LIST_PLAYERS_ENDPOINT}{player_id}"
        # make the API call
        response = self.call_api(endpoint_url)
        player = Player(**response.json())
        return player

    def list_performances(
            self, skip: int = 0, limit: int = 100, min_last_changed_date: str = None
    ):
        """Returns a List of Performances filtered by parameters.

        Calls the API v0/performances endpoint and returns a list of
        Performance objects.

        Returns:
        A List of schemas.Performance objects. Each represents one
        player's scoring for one NFL week.

        """
        logger.debug("Entered get performances")

        params = {
            "skip": skip,
            "limit": limit,
            "min_last_changed_date": min_last_changed_date,
        }

        response = self.call_api(self.LIST_PERFORMANCES_ENDPOINT, params)
        return [Performance(**it) for it in response.json()]

    def __get_bulk_file(self, key: str) -> bytes:
        logger.debug(f"Entered get bulk {key} file")

        player_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES[key]

        response = httpx.get(player_file_path, follow_redirects=True)

        if response.status_code == 200:
            logger.debug("File downloaded successfully")
        return response.content

    def get_bulk_player_file(self) -> bytes:
        """Returns a bulk file with player data"""

        return self.__get_bulk_file('players')

    def get_bulk_league_file(self) -> bytes:
        """Returns a CSV file with league data"""

        return self.__get_bulk_file('leagues')

    def get_bulk_performance_file(self) -> bytes:
        """Returns a CSV file with performance data"""

        return self.__get_bulk_file('performances')

    def get_bulk_team_file(self) -> bytes:
        """Returns a CSV file with team data"""

        return self.__get_bulk_file('teams')

    def get_bulk_team_player_file(self) -> bytes:
        """Returns a CSV file with team player data"""

        return self.__get_bulk_file('team_players')
