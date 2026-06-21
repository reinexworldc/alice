from core.providers.openai.provider import OpenAIProvider
from core.providers.transformers import TransformersProvider
from core.providers.base import LLMProvider


class ProvidersConfig:
    _providers = {
        "openai": lambda model: OpenAIProvider(model=model),
        "transformers": lambda model: TransformersProvider(model_name=model),     
    }

    _models = {
        "openai": ["gpt-4o", "gpt-5"],
        "transformers": ["meta-llama/Llama-3.1-8B", "Qwen/Qwen2.5-1.5B-Instruct"],
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
