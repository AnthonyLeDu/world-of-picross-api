from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, BOOLEAN


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    difficulty: int
    content: list[list[bool]] | None = Field(
        default=None, sa_column=Column(ARRAY(BOOLEAN))
    )

    @property
    def rows_count(self) -> int:
        return len(self.content) if self.content else 0

    @property
    def cols_count(self) -> int:
        return len(max(self.content, key=len)) if self.content else 0

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
