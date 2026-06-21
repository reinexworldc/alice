from core.providers.openai.provider import OpenAIProvider
from core.providers.transformers import TransformersProvider
from core.providers.base import LLMProvider


class ProvidersConfig:
    _providers = {
        "openai": lambda model: OpenAIProvider(model=model),
        "transformers": lambda model: TransformersProvider(model_name=model),     
    }

    _models = {
        "openai": [
            "gpt-5.5",
            "gpt-5.4",
            "gpt-5.4-pro",
            "gpt-5.4-mini",
            "gpt-5.4-nano",
            "gpt-5.3-chat-latest",
            "gpt-5.2",
            "gpt-5.2-pro",
            "gpt-5.1",
            "gpt-5",
            "gpt-5-pro",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "o3",
            "o3-mini",
            "o4-mini",
        ],
        "transformers": [
            "meta-llama/Llama-3.1-8B",
            "Qwen/Qwen2.5-1.5B-Instruct",
        ],
    }

    _optional_auth = {"transformers"}

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def available_models(cls, provider: str) -> list[str]:
        return cls._models[provider]
    
    @classmethod
    def create(cls, provider: str, model: str) -> LLMProvider:
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")
        return cls._providers[provider](model)
    
    @classmethod
    def supports_optional_auth(cls, provider: str) -> bool:
        return provider in cls._optional_auth
