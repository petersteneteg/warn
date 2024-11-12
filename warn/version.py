

class Version:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __init__(self, version: str) -> None:
        parts = version.strip().split(".")
        self.major = int(parts[0]) if (len(parts[0]) > 0) else 0
        self.minor = int(parts[1]) if (len(parts) > 1 and len(parts[1]) > 0) else 0
        self.patch = int(parts[2]) if (len(parts) > 2 and len(parts[2]) > 0) else 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch}, {self.prerelease}, {self.build})"

    def __lt__(self, other) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other) -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __eq__(self, other) -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __ge__(self, other) -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __gt__(self, other) -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ne__(self, other) -> bool:
        return (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch)
