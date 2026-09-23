from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from datetime import datetime


# ── The 5 target columns in exact order ──
FIELD_ORDER = [
    'name_of_the_client',
    'name_of_organisation',
    'designation',
    'phone_no',
    'location',
]

# ── Pretty column headers for Excel export ──
EXCEL_HEADERS = {
    'name_of_the_client': 'Name of the client',
    'name_of_organisation': 'Name of organisation',
    'designation': 'Designation',
    'phone_no': 'Phone no',
    'location': 'Location',
}


@dataclass
class FieldMapping:
    """Maps a source field name to a target field name with optional transform."""
    source_field: str
    target_field: str
    transform: Optional[Callable[[Any], Any]] = None
    default: Any = ''
    required: bool = False


@dataclass
class OutputSchema:
    """Defines a target JSON/Excel output format."""
    name: str
    description: str
    field_mappings: list[FieldMapping]

    def apply(self, data: dict) -> dict:
        """Apply this schema to transform a single data record."""
        result = {}
        for mapping in self.field_mappings:
            val = data.get(mapping.source_field)
            if val is None:
                val = mapping.default
            else:
                if mapping.transform:
                    try:
                        val = mapping.transform(val)
                    except Exception:
                        val = mapping.default
            result[mapping.target_field] = val
        return result

    def validate(self, data: dict) -> tuple[bool, list[str]]:
        """Validate data against this schema. Returns (is_valid, errors)."""
        errors = []
        for mapping in self.field_mappings:
            if mapping.required and not data.get(mapping.source_field):
                errors.append(f"Missing required field: {mapping.source_field}")
        return len(errors) == 0, errors


class SchemaRegistry:
    """Registry of available output schemas."""

    def __init__(self):
        self._schemas: dict[str, OutputSchema] = {}
        self._register_defaults()

    def register(self, schema: OutputSchema) -> None:
        self._schemas[schema.name] = schema

    def get(self, name: str) -> OutputSchema:
        if name not in self._schemas:
            raise KeyError(f"Schema '{name}' not found. Available: {list(self._schemas.keys())}")
        return self._schemas[name]

    def list_schemas(self) -> list[str]:
        return list(self._schemas.keys())

    def _register_defaults(self):
        """Register the default 'directory' schema matching the 5-column output."""

        def clean_str(s):
            return str(s).strip() if s is not None else ''

        def clean_phone(s):
            if not s:
                return ''
            phone = str(s).replace('tel:', '').replace('tel.', '').strip()
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            return f'tel:{phone}' if phone else ''

        def clean_location(s):
            return str(s).strip().lower() if s else ''

        # ── Primary schema: directory (the 5-column format) ──
        directory = OutputSchema(
            name='directory',
            description='Real estate directory — 5 columns: client, organisation, designation, phone, location',
            field_mappings=[
                FieldMapping('name_of_the_client', 'name_of_the_client', clean_str, required=True),
                FieldMapping('name_of_organisation', 'name_of_organisation', clean_str),
                FieldMapping('designation', 'designation', clean_str, default='Director'),
                FieldMapping('phone_no', 'phone_no', clean_phone),
                FieldMapping('location', 'location', clean_location),
            ],
        )

        # ── Generic passthrough schema ──
        generic = OutputSchema(
            name='generic',
            description='Passthrough — keeps all fields as-is',
            field_mappings=[],
        )

        self.register(directory)
        self.register(generic)
