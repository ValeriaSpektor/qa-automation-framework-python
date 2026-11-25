
import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.config import Config
from src.main.api.db.crud.account_crud import AccountCrud
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateAccount:

    ADMIN_USERNAME = Config.fetch("adminUsername")
    ADMIN_PASSWORD = Config.fetch("adminPassword")

    VALID_PASSWORD = "UserTest1!"
    VALID_ROLE = "ROLE_USER"

    @staticmethod
    def generate_username() -> str:
        return f"Val{uuid.uuid4().hex[:8]}"

    def create_user(
        self,
        api_manager,
        username: str,
        password: str = VALID_PASSWORD,
        role: str = VALID_ROLE,
    ):
        # Step 1. Prepare create-user request
        create_user_request = CreateUserRequest(
            username=username,
            password=password,
            role=role,
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

    def test_create_account_valid(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Prepare unique user data
        username = self.generate_username()

        # Step 2. Create user
        self.create_user(
            api_manager=api_manager,
            username=username,
            password=self.VALID_PASSWORD,
            role=self.VALID_ROLE,
        )

        # Step 3. Create bank account
        create_account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=self.VALID_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 4. Verify API response
        assert create_account_response.id is not None
        assert create_account_response.balance == 0

        # Step 5. Get created account from database
        account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=create_account_response.id,
        )

        # Step 6. Verify account in database
        assert account_from_db is not None
        assert account_from_db.id == create_account_response.id
        assert account_from_db.balance == 0

    def test_create_account_invalid_403(self):

        # Step 1. Try to create account using admin credentials
        response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=self.ADMIN_USERNAME,
                password=self.ADMIN_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_403(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 2. Verify forbidden response
        assert response.status_code == 403

        response_body = response.json()

        assert "error" in response_body
        assert response_body["error"]
