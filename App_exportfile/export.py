from pathlib import Path
import os
from django.http import  FileResponse
from .utils import *
import docx
import docx.document
from docx.table import Table, _Cell
from docx.shared import Inches
from docx.enum.table import WD_ROW_HEIGHT_RULE
import time

BASE_DIR = Path(__file__).resolve().parent.parent


def exportfile_withsetting(quesList: list[quesBaseInfo], name: str, export_setting: list[str]) -> FileResponse:
    no_index = True
    no_id = True
    no_evaluation = True
    no_operator = True
    no_time = True
    no_admin_response = True
    no_student_response = True
    if "show_index" in export_setting:
        no_index = False
    if "show_id" in export_setting:
        no_id = False
    if "show_evaluation" in export_setting:
        no_evaluation = False
    if "show_admin_response" in export_setting:
        no_admin_response = False
    if "show_student_response" in export_setting:
        no_student_response = False
    if "show_operator" in export_setting:
        no_operator = False
    if "show_time" in export_setting:
        no_time = False
    return exportfile(quesList, name,
                      no_index=no_index,
                      no_id=no_id,
                      no_evaluation=no_evaluation,
                      no_operator=no_operator,
                      no_time=no_time,
                      no_admin_response=no_admin_response,
                      no_student_response=no_student_response)




def exportfile(quesList: list[quesBaseInfo],
               name:str,
               no_index: bool = False,
               no_id: bool = False,
               no_evaluation: bool = False,
               no_operator: bool = False,
               no_time: bool = False,
               no_admin_response: bool = False,
               no_student_response: bool = False
               ) -> FileResponse:
    col_info = {"index": {"name": "#", "show": True, "ind": 0, "color_0": colorDict["table-tertiary"], "color_1": colorDict["table-tertiary"]},
                "id": {"name": "id", "show": True, "ind": 0, "color_0": colorDict["table-light"], "color_1": colorDict["table-light"]},
                "question": {"name": "问题", "show": True, "ind": 0, "color_0": "FFFFFF", "color_1": "F0F0F0"},
                "seconded": {"name": "👍", "show": True, "ind": 0, "color_0": colorDict["table-success"], "color_1": colorDict["table-success"]},
                "disliked": {"name": "👎", "show": True, "ind": 0, "color_0": colorDict["table-danger"], "color_1": colorDict["table-danger"]},
                "operator": {"name": "操作人", "show": True, "ind": 0, "color_0": "FFFFFF", "color_1": "F0F0F0"},
                "time": {"name": "时间", "show": True, "ind": 0, "color_0": "FFFFFF", "color_1": "F0F0F0"},
                }
    col_num = 7
    if no_index:
        col_info.pop("index")
        col_num -= 1
    if no_id:
        col_info.pop("id")
        col_num -= 1
    if no_evaluation:
        col_info.pop("seconded")
        col_info.pop("disliked")
        col_num -= 2
    if no_operator:
        col_info.pop("operator")
        col_num -= 1
    if no_time:
        col_info.pop("time")
        col_num -= 1
    doc: docx.document.Document = docx.Document()
    table: Table = doc.add_table(1, col_num)
    table.autofit = True
    rh = table.rows[0]
    rh.height_rule = WD_ROW_HEIGHT_RULE.AUTO
    cnt = 0
    for i,j in col_info.items():
        j["ind"] = cnt
        c = rh.cells[cnt]
        c.text = j["name"]
        setCellColor(c, colorDict["thead-light"])
        setAlignment(c)
        setFont(c)
        c.width = Inches(1 if i != "question" else 11-col_num)
        cnt += 1

    quesDict = quesList2dict(quesList)
    for i, j in quesDict.items():
        rq = table.add_row()
        rq.height_rule = WD_ROW_HEIGHT_RULE.AUTO
        question_info = {"index": str(j["cnt"]),
                         "id": str(i),
                         "question": j["question"],
                         "seconded": str(j["seconded"]),
                         "disliked": str(j["disliked"]),
                         "operator": j["asker"],
                         "time": j["date"]+"\n"+j["time"]}
        for ii,ij in col_info.items():
            c:_Cell = rq.cells[ij["ind"]]
            c.text = question_info[ii]
            if ii != "question":
                setAlignment(c)
            setFont(c)
            setCellColor(c, ij["color_0"] if not j["cnt"] % 2 else ij["color_1"])
        for ji,jj in j["responses"].items():
            if no_admin_response and jj["adminrespond"]:
                continue
            if no_student_response and not jj["adminrespond"]:
                continue
            rr = table.add_row()
            rr.height_rule = WD_ROW_HEIGHT_RULE.AUTO
            setCellColor(rr.cells[col_info["question"]["ind"]], colorDict["table-primary"]
                            if jj["adminrespond"] else colorDict["table-info"])
            rr.cells[col_info["question"]["ind"]].text = jj["response"]
            setFont(rr.cells[col_info["question"]["ind"]])
            if not no_operator:
                setCellColor(rr.cells[col_info["operator"]["ind"]], colorDict["table-primary"]
                                if jj["adminrespond"] else colorDict["table-info"])
                rr.cells[col_info["operator"]["ind"]].text = jj["responder"]
                setFont(rr.cells[col_info["operator"]["ind"]])
                setAlignment(rr.cells[col_info["operator"]["ind"]])
            if not no_time:
                setCellColor(rr.cells[col_info["time"]["ind"]], colorDict["table-primary"]
                                if jj["adminrespond"] else colorDict["table-info"])
                rr.cells[col_info["time"]["ind"]
                        ].text = jj["date"]+"\n"+jj["time"]
                setFont(rr.cells[col_info["time"]["ind"]])
                setAlignment(rr.cells[col_info["time"]["ind"]])
            if not no_evaluation:
                rr.cells[col_info["question"]["ind"]].merge(
                    rr.cells[col_info["question"]["ind"]+2])
        for _i in range(col_info["question"]["ind"]):
            lc = table.columns[_i]
            lc.cells[-1].merge(lc.cells[-int(j["rowNum"])])
    file_path = BASE_DIR/"caches" / \
        f"{name}_{time.strftime('%y%m%d_%H%M')}.docx"
    doc.save(file_path)

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = "application/octet-stream"
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        os.path.basename(file_path))
    return response
