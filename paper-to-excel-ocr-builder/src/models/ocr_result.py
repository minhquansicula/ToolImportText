from dataclasses import dataclass

@dataclass
class BoundingBox:
    points: list[tuple[float, float]]  # Four corner points

    @property
    def x_min(self) -> float:
        return min(p[0] for p in self.points)

    @property
    def y_min(self) -> float:
        return min(p[1] for p in self.points)

    @property
    def x_max(self) -> float:
        return max(p[0] for p in self.points)

    @property
    def y_max(self) -> float:
        return max(p[1] for p in self.points)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_box: BoundingBox
    sequence_number: int
    source_image: str
    page_number: int = 1
