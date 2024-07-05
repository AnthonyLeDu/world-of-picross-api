from pydantic import BaseModel


class Game(BaseModel):
    id: int
    name: str
    difficulty: int
    serialized_content: str
    content: list[list[int]] | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = eval(self.serialized_content)

    @property
    def rows_count(self) -> int:
        return len(self.content)

    @property
    def cols_count(self) -> int:
        return len(max(self.content, key=len))
    
    @property
    def model_dump_preview(self) -> dict:
        """Return model data only needed for preview: id, name, difficulty,
        rows count and columns count.

        Returns:
            dict: Preview data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": self.difficulty,
            "rowsCount": self.rows_count,
            "colsCount": self.cols_count,
        }
