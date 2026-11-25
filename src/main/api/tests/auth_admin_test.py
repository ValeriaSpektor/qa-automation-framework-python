
import pytest

from src.main.api.configs.config import Config
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester
)
from src.main.api.models.auth_login_request import AuthLoginRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestAuthAdmin:

    ADMIN_USERNAME = Config.fetch("adminUsername")
    ADMIN_PASSWORD = Config.fetch("adminPassword")

    def test_auth_admin_login_valid(self):

        # Step 1. Prepare valid admin login request
        auth_admin_request = AuthLoginRequest(
            username=self.ADMIN_USERNAME,
            password=self.ADMIN_PASSWORD
        )

        # Step 2. Send login request
        auth_admin_response = ValidateCrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(auth_admin_request)

        # Step 3. Verify authenticated admin data
        assert auth_admin_response.user.username == self.ADMIN_USERNAME
        assert auth_admin_response.user.role == "ROLE_ADMIN"
        assert auth_admin_response.token is not None
        assert auth_admin_response.token != ""

    @pytest.mark.parametrize(
        "scenario",
        [
            "empty_username",
            "empty_password",
        ]
    )
    def test_auth_admin_login_invalid_empty_fields(
        self,
        scenario: str
    ):

        # Step 1. Prepare request with empty credentials
        username = (
            "" if scenario == "empty_username"
            else self.ADMIN_USERNAME
        )

        password = (
            "" if scenario == "empty_password"
            else self.ADMIN_PASSWORD
        )

        auth_admin_request = AuthLoginRequest(
            username=username,
            password=password
        )

        # Step 2. Send login request
        auth_admin_response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_400(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(auth_admin_request)

        # Step 3. Verify bad-request response
        response_body = auth_admin_response.json()

        assert auth_admin_response.status_code == 400
        assert "error" in response_body
        assert response_body["error"] != ""

    @pytest.mark.parametrize(
        "scenario",
        [
            "invalid_username",
            "invalid_password",
        ]
    )
    def test_auth_admin_login_invalid_credentials(
        self,
        scenario: str
    ):

        # Step 1. Prepare request with invalid credentials
        username = (
            f"{self.ADMIN_USERNAME}_invalid"
            if scenario == "invalid_username"
            else self.ADMIN_USERNAME
        )

        password = (
            f"{self.ADMIN_PASSWORD}_invalid"
            if scenario == "invalid_password"
            else self.ADMIN_PASSWORD
        )

        auth_admin_request = AuthLoginRequest(
            username=username,
            password=password
        )

        # Step 2. Send login request
        auth_admin_response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_401(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(auth_admin_request)

        # Step 3. Verify unauthorized response
        response_body = auth_admin_response.json()

        assert auth_admin_response.status_code == 401
        assert response_body["error"] == "Invalid credentials"
