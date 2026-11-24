from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

from docx import Document
from django.http import HttpResponse
from openpyxl import Workbook


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
WORD_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def format_cell(value):
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


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


def make_word(title, headers, rows):
    document = Document()
    document.add_heading(title, level=1)
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for cell, header in zip(table.rows[0].cells, headers):
        cell.text = str(header)

    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = format_cell(value)

    content = BytesIO()
    document.save(content)
    return content.getvalue()


def export_response(request, filename, title, headers, rows):
    export_format = request.query_params.get("export_format")
    if export_format == "excel":
        content = make_excel(headers, rows)
        extension = "xlsx"
        content_type = EXCEL_CONTENT_TYPE
    elif export_format == "word":
        content = make_word(title, headers, rows)
        extension = "docx"
        content_type = WORD_CONTENT_TYPE

    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}.{extension}"'
    )
    return response
