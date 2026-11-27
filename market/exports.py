from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

def safe_excel_value(value):
    if isinstance(value, datetime) and value.utcoffset() is not None:
        return value.isoformat(sep=" ")
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def make_excel(headers, rows):
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet("Данные")
    sheet.append(headers)
    for row in rows:
        sheet.append([safe_excel_value(value) for value in row])

    content = BytesIO()
    workbook.save(content)
    return content.getvalue()


def export_response(filename, headers, rows):
    content = make_excel(headers, rows)
    response = HttpResponse(content, content_type=EXCEL_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return response
