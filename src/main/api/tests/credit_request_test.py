import uuid

import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.account_crud import AccountCrud
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreditRequest:

    VALID_PASSWORD = "UserTest1!"
    CREDIT_ROLE = "ROLE_CREDIT_SECRET"

    INITIAL_BALANCE = 1000.5
    CREDIT_AMOUNT = 5000
    TERM_MONTHS = 12

    @staticmethod
    def generate_username() -> str:
        return f"Val{uuid.uuid4().hex[:8]}"

    def create_credit_user_with_account(
        self,
        api_manager,
    ):
        # Step 1. Prepare unique user data
        username = self.generate_username()

        # Step 2. Prepare create-user request
        create_user_request = CreateUserRequest(
            username=username,
            password=self.VALID_PASSWORD,
            role=self.CREDIT_ROLE,
        )

        # Step 3. Create user
        create_user_response = (
            api_manager
            .admin_steps
            .create_user(create_user_request)
        )

        # Step 4. Verify created user
        assert create_user_response.username == username
        assert create_user_response.role == self.CREDIT_ROLE

        # Step 5. Create bank account
        create_account_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=self.VALID_PASSWORD,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.ACCOUNT_CREATE,
        ).post(None)

        # Step 6. Verify created account
        assert create_account_response.id is not None
        assert create_account_response.balance == 0

        return (
            username,
            self.VALID_PASSWORD,
            create_account_response,
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

    def test_credit_request_valid(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create credit user and bank account
        (
            username,
            password,
            create_account_response,
        ) = self.create_credit_user_with_account(api_manager)

        account_id = create_account_response.id

        # Step 2. Deposit money into account
        self.deposit_money(
            username=username,
            password=password,
            account_id=account_id,
            amount=self.INITIAL_BALANCE,
        )

        # Step 3. Prepare credit request
        credit_request = CreditRequestRequest(
            accountId=account_id,
            amount=self.CREDIT_AMOUNT,
            termMonths=self.TERM_MONTHS,
        )

        # Step 4. Create credit
        credit_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.CREDIT_REQUEST,
        ).post(credit_request)

        # Step 5. Verify API response
        assert credit_response.id == account_id
        assert credit_response.amount == self.CREDIT_AMOUNT
        assert credit_response.termMonths == self.TERM_MONTHS

        assert (
            credit_response.balance
            == self.INITIAL_BALANCE + self.CREDIT_AMOUNT
        )

        assert credit_response.creditId is not None

        # Step 6. Get credit from database
        credit_from_db = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=credit_response.creditId,
        )

        # Step 7. Verify credit exists in database
        assert credit_from_db is not None, (
            "Credit should exist in the database"
        )

        # Step 8. Verify credit data in database
        assert credit_from_db.id == credit_response.creditId
        assert credit_from_db.account_id == account_id
        assert credit_from_db.amount == self.CREDIT_AMOUNT
        assert credit_from_db.term_months == self.TERM_MONTHS

        # Step 9. Get account from database
        account_from_db = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        # Step 10. Verify account exists
        assert account_from_db is not None, (
            "Account should exist in the database"
        )

        # Step 11. Verify account balance after credit
        assert (
            account_from_db.balance
            == self.INITIAL_BALANCE + self.CREDIT_AMOUNT
        ), (
            "Account balance should increase "
            "after successful credit request"
        )

    def test_credit_request_invalid_second_active_credit(
        self,
        api_manager,
        db_session: Session,
    ):
        # Step 1. Create credit user and bank account
        (
            username,
            password,
            create_account_response,
        ) = self.create_credit_user_with_account(api_manager)

        account_id = create_account_response.id

        # Step 2. Deposit money into account
        self.deposit_money(
            username=username,
            password=password,
            account_id=account_id,
            amount=self.INITIAL_BALANCE,
        )

        # Step 3. Prepare first credit request
        first_credit_request = CreditRequestRequest(
            accountId=account_id,
            amount=self.CREDIT_AMOUNT,
            termMonths=self.TERM_MONTHS,
        )

        # Step 4. Create first active credit
        first_credit_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.CREDIT_REQUEST,
        ).post(first_credit_request)

        # Step 5. Verify first credit
        assert first_credit_response.id == account_id
        assert first_credit_response.amount == self.CREDIT_AMOUNT
        assert first_credit_response.termMonths == self.TERM_MONTHS

        assert (
            first_credit_response.balance
            == self.INITIAL_BALANCE + self.CREDIT_AMOUNT
        )

        assert first_credit_response.creditId is not None

        # Step 6. Get first credit from database
        first_credit_from_db = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=first_credit_response.creditId,
        )

        assert first_credit_from_db is not None, (
            "First credit should exist in the database"
        )

        # Step 7. Save account balance before second request
        account_before_second_request = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_before_second_request is not None

        expected_balance = (
            self.INITIAL_BALANCE
            + self.CREDIT_AMOUNT
        )

        assert (
            account_before_second_request.balance
            == expected_balance
        )

        # Step 8. Prepare second credit request
        second_credit_request = CreditRequestRequest(
            accountId=account_id,
            amount=self.CREDIT_AMOUNT,
            termMonths=self.TERM_MONTHS,
        )

        # Step 9. Try to create second active credit
        second_credit_response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_404(),
            endpoint=Endpoint.CREDIT_REQUEST,
        ).post(second_credit_request)

        # Step 10. Verify business error
        assert second_credit_response.status_code == 404

        response_body = second_credit_response.json()

        assert (
            response_body["error"]
            == "Only one active credit allowed per user"
        )

        # Step 11. Verify account balance was not changed
        account_after_second_request = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_after_second_request is not None

        assert (
            account_after_second_request.balance
            == expected_balance
        ), (
            "Account balance should not change "
            "after failed second credit request"
        )

        # Step 12. Verify existing credit was not changed
        credit_after_second_request = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=first_credit_response.creditId,
        )

        assert credit_after_second_request is not None

        assert (
            credit_after_second_request.amount
            == self.CREDIT_AMOUNT
        )

        assert (
            credit_after_second_request.term_months
            == self.TERM_MONTHS
        )