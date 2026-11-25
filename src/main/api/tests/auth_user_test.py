import uuid

import pytest

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester
)
from src.main.api.models.auth_login_request import AuthLoginRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestAuthUser:

    @staticmethod
    def generate_username() -> str:
        return f"Valeria{uuid.uuid4().hex[:8]}"

    def create_user(
        self,
        api_manager,
        username: str,
        password: str = "UserTest1!",
        role: str = "ROLE_USER",

    ):
        # Step 1. Prepare create-user request
        create_user_request = CreateUserRequest(
            username=username,
            password=password,
            role=role
        )

        # Step 2. Create user through AdminSteps
        create_user_response = (
            api_manager
            .admin_steps
            .create_user(create_user_request)
        )

        # Step 3. Verify created user
        assert create_user_response.username == username
        assert create_user_response.role == role

        return create_user_response

    def test_auth_user_valid(
        self,
        api_manager
    ):
        # Step 1. Prepare unique user data
        username = self.generate_username()
        password = "UserTest1!"
        role = "ROLE_USER"

        # Step 2. Create a new user
        self.create_user(
            api_manager=api_manager,
            username=username,
            password=password,
            role=role
        )

        # Step 3. Prepare login request
        auth_user_request = AuthLoginRequest(
            username=username,
            password=password
        )

        # Step 4. Login as created user
        auth_user_response = ValidateCrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(auth_user_request)

        # Step 5. Verify authenticated user
        assert auth_user_response.user.username == username
        assert auth_user_response.user.role == role
        assert auth_user_response.token is not None
        assert auth_user_response.token != ""

    def test_auth_user_invalid_password(
        self,
        api_manager
    ):
        # Step 1. Prepare unique user data
        username = self.generate_username()
        password = "UserTest1!"
        wrong_password = "WrongPass1!"
        role = "ROLE_USER"

        # Step 2. Create a new user
        self.create_user(
            api_manager=api_manager,
            username=username,
            password=password,
            role=role
        )

        # Step 3. Prepare login request with wrong password
        auth_user_request = AuthLoginRequest(
            username=username,
            password=wrong_password
        )

        # Step 4. Send login request
        auth_user_response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_401(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(auth_user_request)

        # Step 5. Verify unauthorized response
        assert auth_user_response.status_code == 401

        response_body = auth_user_response.json()

        assert response_body["error"] == "Invalid credentials"