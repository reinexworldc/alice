from abc import abstractmethod, ABC

class BaseProvider(ABC):
    @abstractmethod
    def model_call(self, input_content) -> str:
        raise NotImplementedError
