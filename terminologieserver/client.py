import enum
import typing
import requests
import urllib.parse
import logging


logger = logging.getLogger(__name__)


class TerminologieRequestError(Exception):
    """Base Exception for all Client related errors in TerminologieClient."""
    pass


class TerminiologieClient:
    """
    Terminologie Client.

    Set of tools used to fetch data from terminologie.nl(or otherwise) server.
    """

    FSN_CODE = "900000000000003001"

    class OutputFormat(enum.Enum):
        default = "Default"
        snowstorm = "Snowstorm compatible"

    uri: typing.Optional[str] = None  # Contains base URI for terminologie server
    session: typing.Optional[requests.Session] = None  # Contains request session with auth headers

    def __init__(self, uri: str) -> None:
        """Init class by storing base URI and starting requests.Session.

        Args:
            uri (str): Base URI for terminologie server. Usually corresponds to settings.TERMINOLOGIE_URI
            output_format (OutputFormat): Output format to use.
        """
        self.uri = uri
        self.session = requests.Session()

    def login(self, username: str, password: str) -> None:
        """
        Fetch Login details using login and password.
        AUTH Details will be stored to self.session.headers.

        Args:
            username (str): Username
            password (str): Password

        Raises:
            TerminologieRequestError in case login is unsuccessul or another error occured.
        """
        try:
            response = requests.post(
                url=f"{self.uri}/auth/realms/nictiz/protocol/openid-connect/token",
                data={
                    "grant_type": "password",
                    "client_id": "cli_client",
                    "username": username,
                    "password": password
                },
                timeout=10
            )
        except requests.RequestException as e:
            raise TerminologieRequestError from e
        else:
            if "access_token" not in response.json():
                raise TerminologieRequestError(f"Incorrect response from server: {response.json()}")
        
            token = response.json()['access_token']
            self.session.headers = {
                "Content-Type" : "application/json",
                "Authorization": f"Bearer {token}"
            }

    def expand_snomed_ecl_valueset(self, ecl_query: str) -> dict:
        """
        Expand Snomed ECL Value Set.
        
        Args:
            ecl_query (str): ECL query string.
            
        Returns:
            dictionary containing response data.
        
        Raises:
            TerminologieRequestError in case ECL query fails.
        """

        def get_results(session, url, results=None):
            """Recursively fetch results.
            
            Args:
                session (requests.Session): Authenticated requests session.
                url (str): Base URL for all requests.
                results (Optional[list]): Lis of results if available.

            Returns:
                list with results.

            Raises:
                TerminologieRequestError in case results could not be fetched.
            """
            _url = url
            if results is None:
                results = []
            else:
                _url += f"&offset={len(results)}"
        
            response = session.get(url=_url)

            if response.status_code != 200:
                raise TerminologieRequestError(f"Could not fetch ecl results: {response.text}")
            
            expansion = response.json()["expansion"]
            if "contains" in expansion:
                results += expansion["contains"]
            print(expansion["total"])

            if len(results) < expansion["total"]:
                results += get_results(session=session, url=url, results=results)
            return results

        return get_results(
            session=self.session,
            url=f"{self.uri}/fhir/ValueSet/$expand?count=1000&url=http://snomed.info/sct?fhir_vs=ecl/{urllib.parse.quote_plus(ecl_query)}",
        )

    def lookup_code(self, system: str, code: str) -> dict:
        """Retrieves the properties for a code within a CodeSystem.
        
        Args:
            system (str): Code System to Use
            code (str): Code ID.

        Returns:
            either dictionary with details or None if code is not found.
        """
        url = f"{self.uri}/fhir/CodeSystem/$lookup?system={system}&code={code}"

        response = self.session.get(url=url)

        return response.json()

    @staticmethod
    def params_to_dict(params):
        """Get Fully specified name for given language.

        Args:
            params (list): list of dictionaries.

        Returns:
            dictionary with lang and term keys.
        """
        data = {
            i['name']: i['valueString']
            for i in params if i['name'] not in ["designation", "property"]
        }

        decompressed_params = [
            {
                i['name']: i.get("valueCode", i.get("valueCoding", i.get("valueString", None)))
                for i in d['part']
            } for d in params if d.get("name") == "designation"
        ]

        designations = {":".join([n["language"].split("-")[0], n["use"]["code"]]): n["value"] for n in decompressed_params}

        properties_list = [
            d['part'] for d in params if d.get("name") == "property"
        ]

        properties = {}
        for prop in properties_list:
            try:
                key = [z.get("valueCode") for z in prop if z.get("name") == "code"][0]
                value_dict = [z for z in prop if z.get("name") != "code"][0]
            except IndexError:
                logger.error(f"Incorrect property received. {prop}")
                continue
            
            value = None
            if value_dict["name"] == "value":
                value = value_dict["valueCode"]
            elif value_dict["name"] == "valueBoolean":
                value = value_dict["valueBoolean"]
            elif value_dict["name"] == "valueString":
                value = value_dict["valueString"]
            
            properties[key] = value

        return data | designations | properties
    
    @staticmethod
    def expanded_data_to_snowstorm_mapping(expanded_data):
        """Convert Expanded data to Snowstorm output.
        
        Args:
            expanded_data (dict): Dictionary with expanded data parameters.
            
        Returns:
            Dictionary conforming with snowstorm output.
        """
        mapped = {
            "id": expanded_data['code'],
            "conceptId": expanded_data["code"],
            "moduleId": expanded_data["moduleId"],
            "effectiveTime": expanded_data.get("effectiveTime", ""),
            "definitionStatus": "COMPLEX" if expanded_data["sufficientlyDefined"] else "PRIMITIVE",
            "idAndFsnTerm": " | ".join([
                expanded_data["code"],
                expanded_data[f"en:{TerminiologieClient.FSN_CODE}"],
                ""
            ]).strip(),
            "active": True,  # TODO: Revisit.
            "pt": {
                "lang": "en",
                "term": expanded_data["en:preferredForLanguage"]
            },
            "fsn": {
                "lang": "en",
                "term": expanded_data[f"en:{TerminiologieClient.FSN_CODE}"]
            }
        }
        return mapped
