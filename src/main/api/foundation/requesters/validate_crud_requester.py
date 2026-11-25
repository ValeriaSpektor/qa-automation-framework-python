from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.base_model import BaseModel
from src.main.api.configs.config import Config
import allure


class ValidateCrudRequester(HttpRequester):
    def __init__(self, request_spec, response_spec,endpoint):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            response_spec=response_spec,
            endpoint=endpoint
        )

    def post(self,model: BaseModel) -> BaseModel:
        response = self.crud_requester.post(model)
        with allure.step(f"POST {Config.fetch("backendUrl")}{self.endpoint.value.url} Validate model:"):
            allure.attach(
                f"Validate model response: {self.endpoint.value.response_model.__name__}",
            )

        self.response_spec(response)
        return self.endpoint.value.response_model.model_validate(response.json())


    def delete(self,user_id: int):
        response = self.crud_requester.delete(user_id)
        self.response_spec(response)
        return self.endpoint.value.response_model.model_validate(response.json())
