from requests.sessions import Session
from requests.models import Response
from typing import Optional, Dict
from fishtext.types import TextType, TextFormat, JsonAPIResponse
from fishtext.errors import (
    TextFormatRequired, TooManyContentExceeded, CallLimitExceeded, BannedForever,
    InternalServerError
)

FISH_TEXT_API_URL = "https://fish-text.ru/get"
FISH_TEXT_API_DOCS = "https://fish-text.ru/api"


class FishTextAPI:

    def __init__(self, session: Optional[Session], api_url: str, text_type: TextType, text_format: TextFormat):
        if session:
            self.session = session
        else:
            self.session = Session()

        self.api_url = api_url
        self.text_type = text_type
        if text_format:
            self.text_format = text_format
        else:
            raise TextFormatRequired()

    def process_response(self, response) -> None:
        raise NotImplementedError

    def get(self):
        raise NotImplementedError


class FishTextJson(FishTextAPI):

    def __init__(self, session: Optional[Session] = None,
                 api_url: str = FISH_TEXT_API_URL,
                 text_type: TextType = TextType.Sentence
                 ):
        super().__init__(
            session=session,
            api_url=api_url,
            text_type=text_type,
            text_format=TextFormat.json
        )

    def process_response(self, response: JsonAPIResponse) -> None:

        error_codes = {
            11: TooManyContentExceeded,
            21: CallLimitExceeded,
            22: BannedForever,
            31: BannedForever
        }

        if response.errorCode is not None:
            exception = error_codes.get(response.errorCode, None)
            if exception:
                raise exception(response.text)

    def get(self, number: int = 100) -> JsonAPIResponse:
        json_response = self.session.get(
            FISH_TEXT_API_URL, params=dict(
                format=self.text_format, number=number, type=self.text_type
            )
        ).json()
        json_api_response_object = JsonAPIResponse(
            status=json_response.get("status"),
            text=json_response.get("text"),
            errorCode=json_response.get("errorCode", None)
        )
        self.process_response(json_api_response_object)
        return json_api_response_object
