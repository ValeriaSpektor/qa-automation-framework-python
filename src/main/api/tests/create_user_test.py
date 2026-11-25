import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.user_crud import UserCrudDb
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs

import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.config import Config
from src.main.api.db.crud.user_crud import UserCrudDb
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateUser:

    ADMIN_USERNAME = Config.fetch("adminUsername")
    ADMIN_PASSWORD = Config.fetch("adminPassword")

    VALID_PASSWORD = "UserTest1!"
    VALID_ROLE = "ROLE_USER"

    @staticmethod
    def generate_username() -> str:
        return f"Val{uuid.uuid4().hex[:8]}"

    def create_user_request(
        self,
        password: str = VALID_PASSWORD,
        role: str = VALID_ROLE,
    ) -> CreateUserRequest:
        return CreateUserRequest(
            username=self.generate_username(),
            password=password,
            role=role,
        )

    def test_create_user_valid(self, db_session: Session):

        # Step 1. Prepare request
        create_user_request = self.create_user_request()

        # Step 2. Create user via API
        create_user_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=self.ADMIN_USERNAME,
                password=self.ADMIN_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ADMIN_CREATE_USER,
        ).post(create_user_request)

        # Step 3. Verify API response
        assert (
            create_user_response.username
            == create_user_request.username
        )

        assert (
            create_user_response.role
            == create_user_request.role
        )

        # Step 4. Get created user from database
        user_from_db = UserCrudDb.get_user_by_username(
            db=db_session,
            username=create_user_request.username,
        )

        # Step 5. Verify database data
        assert user_from_db is not None

        assert (
            user_from_db.username
            == create_user_request.username
        )

        assert (
            user_from_db.role
            == create_user_request.role
        )

    def test_create_user_invalid_role(self):

        # Step 1. Prepare request with invalid role
        create_user_request = self.create_user_request(
            role="ROLE"
        )

        # Step 2. Send request
        response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=self.ADMIN_USERNAME,
                password=self.ADMIN_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_400(),
            endpoint=Endpoint.ADMIN_CREATE_USER,
        ).post(create_user_request)

        # Step 3. Verify response
        response_body = response.json()

        assert response.status_code == 400
        assert (
            response_body["error"]
            == "The role must be: ROLE_USER or ROLE_ADMIN"
        )

    def test_create_user_invalid_password(self):

        # Step 1. Prepare request with invalid password
        create_user_request = self.create_user_request(
            password="User"
        )

        # Step 2. Send request
        response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=self.ADMIN_USERNAME,
                password=self.ADMIN_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_400(),
            endpoint=Endpoint.ADMIN_CREATE_USER,
        ).post(create_user_request)

        # Step 3. Verify response
        response_body = response.json()

        assert response.status_code == 400
        assert "error" in response_body
        assert response_body["error"]

    def test_create_user_without_token(self):

        # Step 1. Prepare valid request
        create_user_request = self.create_user_request()

        # Step 2. Send request without authorization
        response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_401(),
            endpoint=Endpoint.ADMIN_CREATE_USER,
        ).post(create_user_request)

        # Step 3. Verify response
        response_body = response.json()

        assert response.status_code == 401
        assert response_body["error"] == "Unauthorized"
