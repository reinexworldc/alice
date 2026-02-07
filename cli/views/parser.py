from pydantic import BaseModel

class ChunkParser(BaseModel):
    in_red_state: bool = False

    def parse(self, chunk: str) -> str:
        if "*" in chunk and not self.in_red_state:
            self.in_red_state = True
            chunk = chunk.replace("*", "", 1)
        elif "/*" in chunk and self.in_red_state:
            self.in_red_state = False
            chunk = chunk.replace("/*", "", 1)

        if chunk:
            if self.in_red_state:
                print(f"\033[31m{chunk}\033[0m", end="", flush=True)
            else:
                print(chunk, end="", flush=True)

        return chunk
    