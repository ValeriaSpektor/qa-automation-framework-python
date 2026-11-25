
from src.main.api.configs.config import Config
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):

    def create_user(
        self,
        create_user_request: CreateUserRequest
    ):

        response = ValidateCrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=Config.fetch("adminUsername"),
                password=Config.fetch("adminPassword")
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ADMIN_CREATE_USER
        ).post(create_user_request)

        self.created_obj.append(response)

        return response

    def delete_user(
        self,
        user_id: int
    ):

        response = CrudRequester(
            request_spec=RequestSpecs.auth_headers(
                username=Config.fetch("adminUsername"),
                password=Config.fetch("adminPassword")
            ),
            response_spec=ResponseSpecs.status_code_200(),
            endpoint=Endpoint.ADMIN_DELETE_USER
        ).delete(user_id)

        return response
