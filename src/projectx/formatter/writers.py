from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
import json
from datetime import datetime, timezone

from projectx.formatter.schemas import FIELD_ORDER, EXCEL_HEADERS


class BaseWriter(ABC):
    """Abstract base writer."""

    @abstractmethod
    def write(self, data: list[dict], destination: Union[str, Path]) -> Path:
        ...


class JsonWriter(BaseWriter):
    """Writes data to JSON file with the 5-column structure."""

    def __init__(self, compact: bool = False, add_metadata: bool = True):
        self.compact = compact
        self.add_metadata = add_metadata

    def write(self, data: list[dict], destination: Union[str, Path]) -> Path:
        """Write data to JSON file. Enforces the 5-column field order."""
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Reorder each record to match the 5-column structure
        ordered_data = []
        for record in data:
            ordered = {}
            for field in FIELD_ORDER:
                ordered[field] = record.get(field, '')
            ordered_data.append(ordered)

        if self.add_metadata:
            output = {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "record_count": len(ordered_data),
                "data": ordered_data,
            }
        else:
            output = ordered_data

        indent = None if self.compact else 2
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=indent, ensure_ascii=False)

        return path


class ExcelWriter(BaseWriter):
    """Writes data to Excel (.xlsx) matching the target green-header format."""

    def write(self, data: list[dict], destination: Union[str, Path]) -> Path:
        """Write data to Excel with green header row and 5-column format."""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            raise ImportError(
                "openpyxl is required for Excel export. "
                "Install it with: pip install openpyxl"
            )

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Data"

        # ── Header styling (green background, bold white text — matching user's screenshot) ──
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
        header_alignment = Alignment(horizontal="left", vertical="center")
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin'),
        )

        # ── Write header row with pretty names ──
        headers = [EXCEL_HEADERS.get(f, f) for f in FIELD_ORDER]
        ws.append(headers)

        # Style header row
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # ── Write data rows ──
        data_font = Font(size=11)
        data_alignment = Alignment(horizontal="left", vertical="center")

        for record in data:
            row = []
            for field in FIELD_ORDER:
                val = record.get(field, '')
                if isinstance(val, dict):
                    val = json.dumps(val, ensure_ascii=False)
                elif isinstance(val, list):
                    val = ', '.join(str(x) for x in val)
                row.append(val if val is not None else '')
            ws.append(row)

        # Style data rows
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(FIELD_ORDER)):
            for cell in row:
                cell.font = data_font
                cell.alignment = data_alignment
                cell.border = thin_border

        # ── Auto-adjust column widths ──
        column_widths = {
            'Name of the client': 25,
            'Name of organisation': 30,
            'Designation': 15,
            'Phone no': 20,
            'Location': 20,
        }
        for i, header in enumerate(headers, 1):
            col_letter = openpyxl.utils.get_column_letter(i)
            ws.column_dimensions[col_letter].width = column_widths.get(header, 20)

        # Freeze header row
        ws.freeze_panes = 'A2'

        wb.save(path)
        return path
