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
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreditRepay:

    VALID_PASSWORD = "UserTest1!"
    CREDIT_ROLE = "ROLE_CREDIT_SECRET"

    CREDIT_AMOUNT = 5000
    TERM_MONTHS = 12
    INSUFFICIENT_AMOUNT = 2000

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

    def create_credit(
        self,
        username: str,
        password: str,
        account_id: int,
        amount: float = CREDIT_AMOUNT,
        term_months: int = TERM_MONTHS,
    ):
        # Step 1. Prepare credit request
        credit_request = CreditRequestRequest(
            accountId=account_id,
            amount=amount,
            termMonths=term_months,
        )

        # Step 2. Create credit
        credit_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_201(),
            endpoint=Endpoint.CREDIT_REQUEST,
        ).post(credit_request)

        # Step 3. Verify created credit
        assert credit_response.id == account_id
        assert credit_response.amount == amount
        assert credit_response.termMonths == term_months
        assert credit_response.balance == amount
        assert credit_response.creditId is not None

        return credit_response

    def test_credit_repay_valid(
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

        # Step 2. Create credit
        credit_response = self.create_credit(
            username=username,
            password=password,
            account_id=account_id,
            amount=self.CREDIT_AMOUNT,
            term_months=self.TERM_MONTHS,
        )

        credit_id = credit_response.creditId

        # Step 3. Get credit from database before repayment
        credit_before_repay = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=credit_id,
        )

        # Step 4. Verify credit state before repayment
        assert credit_before_repay is not None, (
            "Credit should exist before repayment"
        )

        assert credit_before_repay.account_id == account_id
        assert credit_before_repay.amount == self.CREDIT_AMOUNT
        assert credit_before_repay.term_months == self.TERM_MONTHS

        assert (
            credit_before_repay.balance
            == -self.CREDIT_AMOUNT
        ), (
            "Credit balance should represent outstanding debt"
        )

        # Step 5. Get account from database before repayment
        account_before_repay = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_before_repay is not None

        assert (
            account_before_repay.balance
            == self.CREDIT_AMOUNT
        ), (
            "Account should contain credited funds before repayment"
        )

        # Step 6. Prepare repay request
        credit_repay_request = CreditRepayRequest(
            creditId=credit_id,
            accountId=account_id,
            amount=self.CREDIT_AMOUNT,
        )

        # Step 7. Repay credit
        credit_repay_response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.CREDIT_REPAY,
        ).post(credit_repay_request)

        # Step 8. Verify API response
        assert credit_repay_response.creditId == credit_id

        assert (
            credit_repay_response.amountDeposited
            == self.CREDIT_AMOUNT
        )

        # Step 9. Expire cached ORM objects
        db_session.expire_all()

        # Step 10. Get fresh credit state from database
        credit_after_repay = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=credit_id,
        )

        assert credit_after_repay is not None, (
            "Credit should still exist after repayment"
        )

        # Step 11. Verify credit balance after repayment
        assert credit_after_repay.balance == 0, (
            "Credit balance should be zero after full repayment"
        )

        # Step 12. Get fresh account state from database
        account_after_repay = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_after_repay is not None

        # Step 13. Verify account balance after repayment
        assert account_after_repay.balance == 0, (
            "Account balance should decrease after credit repayment"
        )

    def test_credit_repay_invalid_422(
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

        # Step 2. Create credit
        credit_response = self.create_credit(
            username=username,
            password=password,
            account_id=account_id,
            amount=self.CREDIT_AMOUNT,
            term_months=self.TERM_MONTHS,
        )

        credit_id = credit_response.creditId

        # Step 3. Get credit state before failed repayment
        credit_before_repay = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=credit_id,
        )

        assert credit_before_repay is not None

        assert (
            credit_before_repay.balance
            == -self.CREDIT_AMOUNT
        )

        # Step 4. Get account state before failed repayment
        account_before_repay = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_before_repay is not None

        assert (
            account_before_repay.balance
            == self.CREDIT_AMOUNT
        )

        # Step 5. Prepare repay request with insufficient amount
        credit_repay_request = CreditRepayRequest(
            creditId=credit_id,
            accountId=account_id,
            amount=self.INSUFFICIENT_AMOUNT,
        )

        # Step 6. Try to repay credit
        credit_repay_response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=username,
                password=password,
            ),
            response_spec=ResponseSpecs.status_code_422(),
            endpoint=Endpoint.CREDIT_REPAY,
        ).post(credit_repay_request)

        # Step 7. Verify validation response
        assert credit_repay_response.status_code == 422

        response_body = credit_repay_response.json()

        assert (
            response_body["error"]
            == "The amount is not enough. Credit balance: -5000"
        )

        # Step 8. Expire cached ORM objects
        db_session.expire_all()

        # Step 9. Get fresh credit state from database
        credit_after_failed_repay = CreditCrudDb.get_credit_by_id(
            db=db_session,
            credit_id=credit_id,
        )

        assert credit_after_failed_repay is not None

        # Step 10. Verify credit was not changed
        assert (
            credit_after_failed_repay.balance
            == -self.CREDIT_AMOUNT
        ), (
            "Credit balance should not change "
            "after failed repayment"
        )

        # Step 11. Get fresh account state from database
        account_after_failed_repay = AccountCrud.get_account_by_id(
            db=db_session,
            account_id=account_id,
        )

        assert account_after_failed_repay is not None

        # Step 12. Verify account was not changed
        assert (
            account_after_failed_repay.balance
            == self.CREDIT_AMOUNT
        ), (
            "Account balance should not change "
            "after failed repayment"
        )