from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from django.http import HttpResponse


CONTENT_TYPES = '''<?xml version="1.0"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>'''

ROOT_RELATIONSHIPS = '''<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''

WORKBOOK = '''<?xml version="1.0"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Pendaftaran" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''

WORKBOOK_RELATIONSHIPS = '''<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>'''


def xlsx_response(rows):
    sheet_rows = []
    for row_number, row in enumerate(rows, 1):
        cells = ''.join(
            _cell_xml(row_number, index, value)
            for index, value in enumerate(row, 1)
        )
        sheet_rows.append(f'<row r="{row_number}">{cells}</row>')

    worksheet = _worksheet_xml(sheet_rows, len(rows))
    output = BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', CONTENT_TYPES)
        archive.writestr('_rels/.rels', ROOT_RELATIONSHIPS)
        archive.writestr('xl/workbook.xml', WORKBOOK)
        archive.writestr('xl/_rels/workbook.xml.rels', WORKBOOK_RELATIONSHIPS)
        archive.writestr('xl/worksheets/sheet1.xml', worksheet)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ),
    )
    response['Content-Disposition'] = 'attachment; filename="pendaftaran-dn40.xlsx"'
    return response


def _cell_xml(row_number, column_number, value):
    column = ''
    number = column_number
    while number:
        number, remainder = divmod(number - 1, 26)
        column = chr(65 + remainder) + column

    reference = f'{column}{row_number}'
    if isinstance(value, int):
        return f'<c r="{reference}"><v>{value}</v></c>'
    return (
        f'<c r="{reference}" t="inlineStr">'
        f'<is><t>{escape(str(value))}</t></is></c>'
    )


def _worksheet_xml(sheet_rows, last_row):
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews>'
        '<sheetData>'
        + ''.join(sheet_rows)
        + '</sheetData>'
        + f'<autoFilter ref="A1:L{last_row}"/>'
        + '</worksheet>'
    )
