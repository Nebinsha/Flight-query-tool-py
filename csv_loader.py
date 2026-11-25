"""Reading CSV files into flight records and error messages."""
import csv
import os
from validator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records =[]
    errors=[]
    seen_flights=set()
    for path in paths:
        with open(path,"r",encoding="utf-8",newline="") as file:
            line_number =0
            for line in file:
                line_number+=1
                if line_number==1:
                    continue
                if not line.strip():
                    continue
                if line.lstrip().startswith("#"):
                    continue
                fields =next(csv.reader([line]))
                error_code=validate_row(fields,airports)
                if error_code is not None:
                    errors.append(
                        f"{os.path.basename(path)}:{line_number}: "
                        f"{error_code} | {line.rstrip()}"
                    )
                    continue
                fields=[field.strip() for field in fields]
                flight_id=fields[0]
                departure=fields[3]
                duplicate_key=(flight_id,departure)
                if duplicate_key in seen_flights:
                    errors.append(f"{os.path.basename(path)}:{line_number}: "
                        f"DUPLICATE_FLIGHT | {line.rstrip()}"
                    )
                    continue
                seen_flights.add(duplicate_key)
                records.append(to_record(fields))
    return records, errors
