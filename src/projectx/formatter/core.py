from pathlib import Path
from typing import Union, Optional
from datetime import datetime, timezone

from projectx.formatter.schemas import SchemaRegistry, OutputSchema, FIELD_ORDER
from projectx.formatter.readers import JsonReader, ExcelReader
from projectx.formatter.writers import JsonWriter, ExcelWriter


class DataFormatter:
    """Main class that orchestrates reading, transforming, and writing data.

    Default schema is 'directory' which produces the 5-column output:
    - Name of the client
    - Name of organisation
    - Designation
    - Phone no
    - Location
    """

    def __init__(self, schema: Union[str, OutputSchema, None] = None):
        """Initialize with optional schema name or OutputSchema object.

        Args:
            schema: Schema name ('directory' or 'generic'), an OutputSchema instance,
                    or None (defaults to 'directory').
        """
        self.registry = SchemaRegistry()

        if isinstance(schema, str):
            self.schema = self.registry.get(schema)
        elif isinstance(schema, OutputSchema):
            self.schema = schema
        else:
            self.schema = self.registry.get('directory')

    def format_data(self, data: list[dict]) -> list[dict]:
        """Apply schema formatting to in-memory data.

        For 'generic' schema, passes through with a timestamp.
        For 'directory' schema, maps and transforms to the 5-column format.
        """
        if self.schema.name == 'generic':
            timestamp = datetime.now(timezone.utc).isoformat()
            formatted = []
            for record in data:
                new_record = record.copy()
                if '_formatted_at' not in new_record:
                    new_record['_formatted_at'] = timestamp
                formatted.append(new_record)
            return formatted

        return [self.schema.apply(record) for record in data]

    def get_summary(self, data: list[dict]) -> dict:
        """Return summary stats about the data."""
        return {
            "record_count": len(data),
            "fields": FIELD_ORDER,
            "sample_record": data[0] if data else None,
        }

    def json_to_json(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> Path:
        """Read JSON, apply schema formatting, write formatted JSON."""
        data = JsonReader().read(Path(input_path))
        formatted = self.format_data(data)
        return JsonWriter().write(formatted, Path(output_path))

    def excel_to_json(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        sheet_name: Optional[str] = None,
    ) -> Path:
        """Read Excel, apply schema formatting, write formatted JSON."""
        data = ExcelReader(sheet_name=sheet_name).read(Path(input_path))
        formatted = self.format_data(data)
        return JsonWriter().write(formatted, Path(output_path))

    def json_to_excel(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> Path:
        """Read JSON, apply schema formatting, write Excel (green header, 5 columns)."""
        data = JsonReader().read(Path(input_path))
        formatted = self.format_data(data)
        return ExcelWriter().write(formatted, Path(output_path))

    def excel_to_excel(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        sheet_name: Optional[str] = None,
    ) -> Path:
        """Read Excel, apply schema formatting, write new formatted Excel."""
        data = ExcelReader(sheet_name=sheet_name).read(Path(input_path))
        formatted = self.format_data(data)
        return ExcelWriter().write(formatted, Path(output_path))
