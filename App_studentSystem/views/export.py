from pathlib import Path
import os
from django.http import HttpRequest, FileResponse
from .utils import *
import docx
import docx.document
from docx.table import Table, _Cell, _Row

BASE_DIR = Path(__file__).resolve().parent.parent.parent
COLUMNS = 4

def export_all(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    
    quesList = getallquestions()
    questions = {}

    doc:docx.document.Document= docx.Document()
    table:Table = doc.add_table(1,COLUMNS)
    head=["#","问题","附议/不喜欢","时间"]
    for i in range(0,COLUMNS):
        c:_Cell = table.row_cells(0)[i]
        c.text=head[i]

    file_path = BASE_DIR/"caches/a.docx"
    doc.save(file_path)

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            os.path.basename(file_path))
        return response
    else:
        return HttpResponse("Sorry, the file you requested does not exist.")
