import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.account_crud import AccountCrud
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestDepositAccount:

    VALID_PASSWORD = "UserTest1!"
    VALID_ROLE = "ROLE_USER"
    DEPOSIT_AMOUNT = 1000

    @staticmethod
    def generate_username() -> str:
        return f"Val{uuid.uuid4().hex[:8]}"

    def create_user_and_account(
        self,
        api_manager,
    ):
        # Step 1. Prepare unique user data
        username = self.generate_username()

        # Step 2. Prepare create-user request
        create_user_request = CreateUserRequest(
            username=username,
            password=self.VALID_PASSWORD,
            role=self.VALID_ROLE,
        )

        # Step 3. Create user
        create_user_response = (
            api_manager
            .admin_steps
            .create_user(create_user_request)
        )

        # Step 4. Verify created user
        assert create_user_response.username == username
        assert create_user_response.role == self.VALID_ROLE

        # Step 5. Create bank account
        account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=self.VALID_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 6. Verify created account
        assert account_response.id is not None
        assert account_response.balance == 0

        return username, self.VALID_PASSWORD, account_response

    def test_deposit_account_valid(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create user and bank account
        username, password, account_response = (
            self.create_user_and_account(api_manager)
        )

        account_id = account_response.id

        # Step 2. Prepare valid deposit request
        deposit_account_request = DepositAccountRequest(
            accountId=account_id,
            amount=self.DEPOSIT_AMOUNT,
        )

        # Step 3. Deposit money
        deposit_account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ACCOUNT_DEPOSIT,
        ).post(deposit_account_request)

        # Step 4. Verify API response
        assert deposit_account_response.id == account_id
        assert (
            deposit_account_response.balance
            == self.DEPOSIT_AMOUNT
        )

        # Step 5. Get account from database
        account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        # Step 6. Verify database state
        assert account_from_db is not None, (
            "Account should exist in the database"
        )

        assert account_from_db.id == account_id

        assert account_from_db.balance == self.DEPOSIT_AMOUNT, (
            "Account balance should be updated after successful deposit"
        )

    def test_deposit_account_invalid_400(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create user and bank account
        username, password, account_response = (
            self.create_user_and_account(api_manager)
        )

        account_id = account_response.id

        # Step 2. Prepare invalid deposit request
        deposit_account_request = DepositAccountRequest(
            accountId=account_id,
            amount=0,
        )

        # Step 3. Send invalid deposit request
        deposit_account_response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_400(),
            endpoint=Endpoint.ACCOUNT_DEPOSIT,
        ).post(deposit_account_request)

        # Step 4. Verify bad request response
        assert deposit_account_response.status_code == 400

        # Step 5. Get account from database
        account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        # Step 6. Verify database state was not changed
        assert account_from_db is not None, (
            "Account should still exist after failed deposit"
        )

        assert account_from_db.balance == 0, (
            "Account balance should not change after a 400 response"
        )

    def test_deposit_account_invalid_401(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create user and bank account
        _, _, account_response = (
            self.create_user_and_account(api_manager)
        )

        account_id = account_response.id

        # Step 2. Prepare valid deposit request
        deposit_account_request = DepositAccountRequest(
            accountId=account_id,
            amount=self.DEPOSIT_AMOUNT,
        )

        # Step 3. Send deposit request without authorization
        deposit_account_response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_401(),
            endpoint=Endpoint.ACCOUNT_DEPOSIT,
        ).post(deposit_account_request)

        # Step 4. Verify unauthorized response
        assert deposit_account_response.status_code == 401

        response_body = deposit_account_response.json()

        assert response_body["code"] == 401
        assert response_body["message"] == "JWT Token not found"

        # Step 5. Get account from database
        account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        # Step 6. Verify database state was not changed
        assert account_from_db is not None, (
            "Account should still exist after unauthorized request"
        )

        assert account_from_db.balance == 0, (
            "Account balance should not change after a 401 response"
        )