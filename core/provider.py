from abc import abstractmethod, ABC

class BaseProvider(ABC):
    @abstractmethod
    async def async_model_call(self, input_content) -> str:
        raise NotImplementedError
