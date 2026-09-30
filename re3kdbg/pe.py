"""Small PE reader used for profile/hash/AOB validation and static xrefs."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int

    @property
    def executable(self) -> bool:
        return bool(self.characteristics & 0x20000000)


class PEImage:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe_offset:pe_offset + 4] != b"PE\0\0":
            raise ValueError(f"not a PE image: {self.path}")
        self.machine = struct.unpack_from("<H", self.data, pe_offset + 4)[0]
        self.section_count = struct.unpack_from("<H", self.data, pe_offset + 6)[0]
        optional = pe_offset + 24
        self.magic = struct.unpack_from("<H", self.data, optional)[0]
        self.image_base = struct.unpack_from("<Q", self.data, optional + 24)[0]
        self.size_of_image = struct.unpack_from("<I", self.data, optional + 56)[0]
        table = optional + 240
        self.sections: list[Section] = []
        for index in range(self.section_count):
            offset = table + index * 40
            name = self.data[offset:offset + 8].rstrip(b"\0").decode("ascii", "replace")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            characteristics = struct.unpack_from("<I", self.data, offset + 36)[0]
            self.sections.append(Section(name, virtual_address, virtual_size, raw_offset, raw_size, characteristics))

    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest().upper()

    def va_to_offset(self, address: int) -> int:
        rva = address - self.image_base
        for section in self.sections:
            span = max(section.virtual_size, section.raw_size, 1)
            if section.virtual_address <= rva < section.virtual_address + span:
                relative = rva - section.virtual_address
                if relative < section.raw_size:
                    return section.raw_offset + relative
        raise ValueError(f"address outside raw PE sections: 0x{address:X}")

    def read_va(self, address: int, size: int) -> bytes:
        offset = self.va_to_offset(address)
        return self.data[offset:offset + size]

    @staticmethod
    def parse_pattern(pattern: str) -> list[int | None]:
        result: list[int | None] = []
        for token in pattern.split():
            result.append(None if token in ("?", "??") else int(token, 16))
        return result

    def verify_aob(self, address: int, pattern: str) -> bool:
        expected = self.parse_pattern(pattern)
        actual = self.read_va(address, len(expected))
        return all(want is None or want == got for want, got in zip(expected, actual))

    def scan_aob(self, pattern: str, executable_only: bool = True) -> list[int]:
        expected = self.parse_pattern(pattern)
        hits: list[int] = []
        for section in self.sections:
            if executable_only and not section.executable:
                continue
            blob = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            end = len(blob) - len(expected) + 1
            for index in range(max(0, end)):
                if all(want is None or want == blob[index + i] for i, want in enumerate(expected)):
                    hits.append(self.image_base + section.virtual_address + index)
        return hits

    def call_xrefs(self, target: int) -> list[int]:
        """Find direct E8/E9 rel32 calls/jumps to target in executable sections."""
        hits: list[int] = []
        for section in self.sections:
            if not section.executable:
                continue
            blob = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            base = self.image_base + section.virtual_address
            for index in range(0, max(0, len(blob) - 4)):
                if blob[index] not in (0xE8, 0xE9):
                    continue
                rel = struct.unpack_from("<i", blob, index + 1)[0]
                destination = base + index + 5 + rel
                if destination == target:
                    hits.append(base + index)
        return hits

    def summary(self) -> dict:
        return {
            "path": str(self.path),
            "sha256": self.sha256(),
            "machine": f"0x{self.machine:X}",
            "magic": f"0x{self.magic:X}",
            "image_base": f"0x{self.image_base:X}",
            "size_of_image": f"0x{self.size_of_image:X}",
            "sections": [
                {
                    "name": s.name,
                    "rva": f"0x{s.virtual_address:X}",
                    "raw_size": f"0x{s.raw_size:X}",
                    "executable": s.executable,
                }
                for s in self.sections
            ],
        }
