import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.account_crud import AccountCrud
from src.main.api.db.crud.transaction_crud import TransactionCrudDb
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.transfer_account_request import TransferAccountRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestTransferAccount:

    VALID_PASSWORD = "UserTest1!"
    VALID_ROLE = "ROLE_USER"

    INITIAL_BALANCE = 1000
    TRANSFER_AMOUNT = 500

    @staticmethod
    def generate_username() -> str:
        return f"Val{uuid.uuid4().hex[:8]}"

    def create_user_with_two_accounts(
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

        # Step 5. Create first bank account
        account_response_1 = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=self.VALID_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 6. Verify first bank account
        assert account_response_1.id is not None
        assert account_response_1.balance == 0

        # Step 7. Create second bank account
        account_response_2 = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=self.VALID_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 8. Verify second bank account
        assert account_response_2.id is not None
        assert account_response_2.balance == 0

        return (
            username,
            self.VALID_PASSWORD,
            account_response_1,
            account_response_2,
        )

    def deposit_money(
        self,
        username: str,
        password: str,
        account_id: int,
        amount: float,
    ):
        # Step 1. Prepare deposit request
        deposit_account_request = DepositAccountRequest(
            accountId=account_id,
            amount=amount,
        )

        # Step 2. Deposit money
        deposit_account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ACCOUNT_DEPOSIT,
        ).post(deposit_account_request)

        # Step 3. Verify deposit
        assert deposit_account_response.id == account_id
        assert deposit_account_response.balance == amount

        return deposit_account_response

    def test_transfer_account_valid_one_user(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create user with two bank accounts
        (
            username,
            password,
            account_response_1,
            account_response_2,
        ) = self.create_user_with_two_accounts(api_manager)

        from_account_id = account_response_1.id
        to_account_id = account_response_2.id

        # Step 2. Deposit money into source account
        self.deposit_money(
            username=username,
            password=password,
            account_id=from_account_id,
            amount=self.INITIAL_BALANCE,
        )

        # Step 3. Prepare transfer request
        transfer_account_request = TransferAccountRequest(
            fromAccountId=from_account_id,
            toAccountId=to_account_id,
            amount=self.TRANSFER_AMOUNT,
        )

        # Step 4. Transfer money
        transfer_account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ACCOUNT_TRANSFER,
        ).post(transfer_account_request)

        # Step 5. Verify API response
        assert (
            transfer_account_response.fromAccountId
            == from_account_id
        )

        assert (
            transfer_account_response.toAccountId
            == to_account_id
        )

        # Step 6. Get source account from database
        from_account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=from_account_id,
        )

        # Step 7. Get destination account from database
        to_account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=to_account_id,
        )

        # Step 8. Verify accounts exist
        assert from_account_from_db is not None, (
            "Source account should exist in the database"
        )

        assert to_account_from_db is not None, (
            "Destination account should exist in the database"
        )

        # Step 9. Verify source account balance
        assert (
            from_account_from_db.balance
            == self.INITIAL_BALANCE - self.TRANSFER_AMOUNT
        ), (
            "Source account balance should decrease "
            "after successful transfer"
        )

        # Step 10. Verify destination account balance
        assert (
            to_account_from_db.balance
            == self.TRANSFER_AMOUNT
        ), (
            "Destination account balance should increase "
            "after successful transfer"
        )

        # Step 11. Get transaction by source account
        transaction_from_db = (
            TransactionCrudDb.get_transaction_by_from_account_id(
                db=db_session,
                from_account_id=from_account_id,
            )
        )

        # Step 12. Get transaction by destination account
        transaction_to_db = (
            TransactionCrudDb.get_transaction_by_to_account_id(
                db=db_session,
                to_account_id=to_account_id,
            )
        )

        # Step 13. Verify transaction records
        assert transaction_from_db is not None, (
            "Transaction should exist for source account"
        )

        assert transaction_to_db is not None, (
            "Transaction should exist for destination account"
        )

        assert (
            transaction_from_db.from_account_id
            == from_account_id
        )

        assert (
            transaction_to_db.to_account_id
            == to_account_id
        )

        assert (
            transaction_from_db.amount
            == self.TRANSFER_AMOUNT
        )

    def test_transfer_account_invalid_401(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create user with two bank accounts
        (
            username,
            password,
            account_response_1,
            account_response_2,
        ) = self.create_user_with_two_accounts(api_manager)

        from_account_id = account_response_1.id
        to_account_id = account_response_2.id

        # Step 2. Deposit money into source account
        self.deposit_money(
            username=username,
            password=password,
            account_id=from_account_id,
            amount=self.INITIAL_BALANCE,
        )

        # Step 3. Prepare transfer request
        transfer_account_request = TransferAccountRequest(
            fromAccountId=from_account_id,
            toAccountId=to_account_id,
            amount=self.TRANSFER_AMOUNT,
        )

        # Step 4. Send transfer request without authorization
        transfer_account_response = CrudRequester(
            request_spec=RequestSpecs.no_auth_headers(),
            response_spec=ResponseSpecs.status_code_401(),
            endpoint=Endpoint.ACCOUNT_TRANSFER,
        ).post(transfer_account_request)

        # Step 5. Verify unauthorized response
        assert transfer_account_response.status_code == 401

        response_body = transfer_account_response.json()

        assert response_body["code"] == 401
        assert response_body["message"] == "JWT Token not found"

        # Step 6. Get source account from database
        from_account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=from_account_id,
        )

        # Step 7. Get destination account from database
        to_account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=to_account_id,
        )

        # Step 8. Verify accounts exist
        assert from_account_from_db is not None
        assert to_account_from_db is not None

        # Step 9. Verify source balance was not changed
        assert (
            from_account_from_db.balance
            == self.INITIAL_BALANCE
        ), (
            "Source account balance should not change "
            "after unauthorized transfer"
        )

        # Step 10. Verify destination balance was not changed
        assert (
            to_account_from_db.balance
            == 0
        ), (
            "Destination account balance should not change "
            "after unauthorized transfer"
        )