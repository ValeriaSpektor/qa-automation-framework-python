from http import HTTPStatus

import requests

from src.main.api.configs.config import Config
from src.main.api.models.auth_login_request import AuthLoginRequest
from src.main.api.models.auth_login_response import AuthLoginResponse


class RequestSpecs:

    BASE_URL = Config.fetch("backendUrl")

    @staticmethod
    def base_headers() -> dict[str, str]:

        return {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    @staticmethod
    def auth_headers(
        username: str,
        password: str
    ) -> dict:

        # Step 1. Prepare login request body
        auth_login_request = AuthLoginRequest(
            username=username,
            password=password
        )

        # Step 2. Send login request
        response = requests.post(
            url=f"{RequestSpecs.BASE_URL}/auth/token/login",
            json=auth_login_request.model_dump(),
            headers=RequestSpecs.base_headers()
        )

        # Step 3. Verify successful authorization
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                f"Failed to authorize user '{username}'. "
                f"Status code: {response.status_code}. "
                f"Response: {response.text}"
            )

        # Step 4. Convert response JSON to model
        auth_login_response = AuthLoginResponse(
            **response.json()
        )

        # Step 5. Prepare headers with token
        headers = RequestSpecs.base_headers()

        headers["Authorization"] = (
            f"Bearer {auth_login_response.token}"
        )

        # Step 6. Return request specification
        return {
            "base_url": RequestSpecs.BASE_URL,
            "headers": headers
        }

    @staticmethod
    def no_auth_headers() -> dict:

        return {
            "base_url": RequestSpecs.BASE_URL,
            "headers": RequestSpecs.base_headers()
        }