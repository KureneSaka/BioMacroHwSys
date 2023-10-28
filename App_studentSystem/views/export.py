from pathlib import Path
from django.http import HttpRequest
from .utils import *
from App_exportfile.export import exportfile_withsetting


def export_all(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getallquestions().filter(week=week)
    quesList = list(quesList_raw)
    export_setting = []
    if request.POST:
        export_setting = request.POST.getlist("export_setting")
    return exportfile_withsetting(quesList, f"STUDENT_{hash2id(hash)}_DISPLAY_ALL", export_setting)


def export_mine(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getmyquestions(hash).filter(week=week)
    quesList = list(quesList_raw)
    export_setting = []
    if request.POST:
        export_setting = request.POST.getlist("export_setting")
    return exportfile_withsetting(quesList, f"STUDENT_{hash2id(hash)}_DISPLAY_MINE", export_setting)

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# COLUMNS = 6


# def export_all(request: HttpRequest):
#     hash, r = checkcookies(request)
#     if r:
#         return r

#     quesList_raw = getallquestions()
#     quesList = list(quesList_raw)
#     return quesList2FileResponse(quesList, f"STUDENT_{hash2id(hash)}_DISPLAY_ALL")


# def export_mine(request: HttpRequest):
#     hash, r = checkcookies(request)
#     if r:
#         return r

#     quesList_raw = getmyquestions(hash)
#     quesList = list(quesList_raw)
#     return quesList2FileResponse(quesList, f"STUDENT_{hash2id(hash)}_DISPLAY_MINE")


# def quesList2FileResponse(quesList: list[quesBaseInfo], name: str) -> FileResponse:
#     doc: docx.document.Document = docx.Document()
#     table: Table = doc.add_table(1, COLUMNS)
#     table.autofit = True
#     head_l = ["#", "id", "问题", "👍", "👎", "时间"]
#     col_width = [1, 1, 5, 1, 1, 1]
#     rh = table.rows[0]
#     rh.height_rule = WD_ROW_HEIGHT_RULE.AUTO
#     for i in range(COLUMNS):
#         c = rh.cells[i]
#         c.text = head_l[i]
#         setCellColor(c, colorDict["thead-light"])
#         setAlignment(c)
#         setFont(c)
#         c.width = Inches(col_width[i])

#     quesDict = quesList2dict(quesList)
#     for i, j in quesDict.items():
#         rq = table.add_row()
#         rq.height_rule = WD_ROW_HEIGHT_RULE.AUTO
#         ques_l = [str(j["cnt"]), str(i), j["question"], str(j["seconded"]),
#                   str(j["disliked"]), j["date"]+"\n"+j["time"]]
#         for _i in range(COLUMNS):
#             c = rq.cells[_i]
#             c.text = ques_l[_i]
#             if _i != 2:
#                 setAlignment(c)
#             setFont(c)
#         setCellColor(rq.cells[0], colorDict["table-tertiary"])
#         setCellColor(rq.cells[1], colorDict["table-light"])
#         setCellColor(rq.cells[2], "FFFFFF"if not j["cnt"] % 2 else "F0F0F0")
#         setCellColor(rq.cells[5], "FFFFFF"if not j["cnt"] % 2 else "F0F0F0")
#         setCellColor(rq.cells[3], colorDict["table-secondary"])
#         setCellColor(rq.cells[4], colorDict["table-secondary"])

#         for ji, jj in j["responses"].items():
#             rr = table.add_row()
#             rr.height_rule = WD_ROW_HEIGHT_RULE.AUTO
#             setCellColor(rr.cells[2], colorDict["table-primary"]
#                          if jj["adminrespond"] else colorDict["table-info"])
#             setCellColor(rr.cells[5], colorDict["table-primary"]
#                          if jj["adminrespond"] else colorDict["table-info"])
#             rr.cells[2].merge(rr.cells[4])
#             rr.cells[2].text = jj["response"]
#             rr.cells[5].text = jj["date"]+"\n"+jj["time"]
#             setAlignment(rr.cells[5])
#             setFont(rr.cells[2])
#             setFont(rr.cells[5])
#         for _i in range(2):
#             lc = table.columns[_i]
#             lc.cells[-1].merge(lc.cells[-int(j["rowNum"])])
#     file_path = BASE_DIR/"caches" / \
#         f"{name}_{time.strftime('%y%m%d_%H%M')}.docx"
#     doc.save(file_path)

#     response = FileResponse(open(file_path, 'rb'))
#     response['Content-Type'] = "application/octet-stream"
#     response['Content-Disposition'] = 'attachment; filename="{}"'.format(
#         os.path.basename(file_path))
#     return response


# colorDict = {"table-primary": "C3DFFF",
#              "table-secondary": "F9FBFF",
#              "table-tertiary": "BFC4C9",
#              "table-light": "F9FAFB",
#              "table-info": "D8F9FB",
#              "table-success": "B8EFD1",
#              "table-danger": "FFB8C6",
#              "thead-light": "E9ECEf",
#              }


# def setCellColor(cell: _Cell, colorStr: str):
#     shading_list = locals()
#     shading_list['shading_elm_'+str(cell)] = parse_xml(
#         r'<w:shd {} w:fill="{bgColor}"/>'.format(nsdecls('w'), bgColor=colorStr))
#     cell._tc.get_or_add_tcPr().append(
#         shading_list['shading_elm_'+str(cell)])


# def setAlignment(cell: _Cell):
#     cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
#     cell.paragraphs[0].alignment = WD_TABLE_ALIGNMENT.CENTER


# def setFont(cell: _Cell):
#     cell.paragraphs[0].paragraph_format.space_after = Length(0)
#     for r in cell.paragraphs[0].runs:
#         r.font.name = 'Arial'
#         r._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
