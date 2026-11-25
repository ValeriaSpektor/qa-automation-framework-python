from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.requests.requester import Requester


class CreateAccountRequester(Requester):

    def post(self) -> CreateAccountResponse | Response:

        # Step 1. Prepare request URL
        url = f"{self.base_url}/account/create"

        # Step 2. Send create-account request
        response = requests.post(
            url=url,
            headers=self.headers
        )

        # Step 3. Verify response status code
        self.response_spec(response)

        # Step 4. Convert successful response to model
        if response.status_code == HTTPStatus.CREATED:
            return CreateAccountResponse(
                **response.json()
            )

        # Step 5. Return error response
        return response