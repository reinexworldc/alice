from core.providers.base import LLMProvider
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from threading import Thread
from typing import Iterator
import torch


class TransformersProvider(LLMProvider):
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device_map="auto" if device != "cpu" else None,
        )
        if device == "cpu":
            self.model.to(device)
        self.device = device

    def _build_input(self, messages: list[dict]) -> dict:
        """Tokenize messages using the model's chat template."""
        input_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        return self.tokenizer(input_text, return_tensors="pt").to(self.device)
    
    def _parse_tool_calls(self, text: str) -> list | None:
        """
        Models like Llama-3.1 can output tool calls as JSON — parse here.
        """
        return None  # Extend this for tool-calling models

    def llm_generate(self, messages: list[dict], tools: list[dict]):
        inputs = self._build_input(messages)

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        new_tokens = output_ids[0][inputs["input_ids"].shape[-1]:]
        content = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        return {
            "content": content,
            "tool_calls": self._parse_tool_calls(content),
        }

    def llm_stream(self, messages: list[dict], tools: list[dict]) -> Iterator[dict]:
        inputs = self._build_input(messages)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

        thread = Thread(
            target=self.model.generate,
            kwargs=dict(
                **inputs,
                streamer=streamer,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
        )
        thread.start()

        for token in streamer:
            yield {
                "content": token if token else None,
                "tool_calls": None,  # Tool calls aren't available mid-stream
            }

        thread.join()
