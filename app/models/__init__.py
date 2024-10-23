type Rgba = list[int | float]  # [255, 100, 150, 0.5]
type Clue = dict[str, Rgba | int]
type ClueLine = list[Clue | None]
type Clues = list[list[ClueLine]]
type LineContent = list[
    Rgba | bool | None  # [[255, 100, 150, 0.5], None, False]
]
type Content = list[LineContent | None]
