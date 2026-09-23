import argparse
from pathlib import Path
import json

from projectx.formatter.core import DataFormatter
from projectx.formatter.schemas import SchemaRegistry
from projectx.formatter.readers import JsonReader, ExcelReader

def main():
    parser = argparse.ArgumentParser(description='ProjectX Data Formatter')
    parser.add_argument('input', nargs='?', help='Input file path (JSON or Excel)')
    parser.add_argument('output', nargs='?', help='Output file path (JSON or Excel)')
    parser.add_argument('--schema', '-s', default='generic', help='Schema to apply')
    parser.add_argument('--sheet', help='Excel sheet name (for Excel input)')
    parser.add_argument('--list-schemas', action='store_true', help='List available schemas')
    parser.add_argument('--preview', action='store_true', help='Preview first 5 records without writing')
    
    args = parser.parse_args()
    
    if args.list_schemas:
        registry = SchemaRegistry()
        print("Available schemas:")
        for name in registry.list_schemas():
            schema = registry.get(name)
            print(f"  - {name}: {schema.description}")
        return
        
    if not args.input:
        parser.error("Input file is required unless --list-schemas is specified")
        
    input_path = Path(args.input)
    
    try:
        formatter = DataFormatter(schema=args.schema)
        
        if args.preview:
            if input_path.suffix.lower() == '.json':
                reader = JsonReader()
            elif input_path.suffix.lower() in ('.xlsx', '.xls'):
                reader = ExcelReader(sheet_name=args.sheet)
            else:
                print(f"Unsupported input format: {input_path.suffix}")
                return
                
            stream = reader.read_stream(input_path)
            data = []
            for i, record in enumerate(stream):
                if i >= 5:
                    break
                data.append(record)
                
            formatted = formatter.format_data(data)
            print(json.dumps(formatted, indent=2, ensure_ascii=False))
            
            summary = formatter.get_summary(formatted)
            print(f"\nPreview Summary: {summary['record_count']} records, {len(summary['fields'])} fields.")
            return

        if not args.output:
            parser.error("Output file is required unless --list-schemas or --preview is specified")
            
        output_path = Path(args.output)
        in_ext = input_path.suffix.lower()
        out_ext = output_path.suffix.lower()
        
        if in_ext == '.json' and out_ext == '.json':
            formatter.json_to_json(input_path, output_path)
        elif in_ext in ('.xlsx', '.xls') and out_ext == '.json':
            formatter.excel_to_json(input_path, output_path, args.sheet)
        elif in_ext == '.json' and out_ext in ('.xlsx', '.xls'):
            formatter.json_to_excel(input_path, output_path)
        elif in_ext in ('.xlsx', '.xls') and out_ext in ('.xlsx', '.xls'):
            formatter.excel_to_excel(input_path, output_path, args.sheet)
        else:
            print(f"Unsupported conversion: {in_ext} to {out_ext}")
            return
            
        print(f"Successfully formatted data to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
