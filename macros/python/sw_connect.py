"""Подключение к SolidWorks 2026 через COM и базовые операции. Требует: pip install pywin32."""
import sys
import pythoncom
import win32com.client
from win32com.client import VARIANT

PROGID = "SldWorks.Application.34"  # 2026; без номера — любая установленная версия


def connect(visible=True):
    try:
        sw = win32com.client.GetActiveObject(PROGID)
    except Exception:
        sw = win32com.client.Dispatch(PROGID)
    sw.Visible = visible
    return sw


def _ref():
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)


def open_doc(sw, path):
    ext = path.lower().rsplit(".", 1)[-1]
    doc_type = {"sldprt": 1, "sldasm": 2, "slddrw": 3}[ext]
    err, warn = _ref(), _ref()
    model = sw.OpenDoc6(path, doc_type, 1, "", err, warn)
    if model is None:
        raise RuntimeError(f"Не открылся {path}: err={err.value}")
    return model


def save_as(model, path):
    err, warn = _ref(), _ref()
    ok = model.Extension.SaveAs3(path, 0, 1, None, None, err, warn)
    if not ok:
        raise RuntimeError(f"Не сохранился {path}: err={err.value}")


def set_variable(model, name, value_mm):
    """Меняет глобальную переменную "name" (мм) и перестраивает модель."""
    eq = model.GetEquationMgr()
    for i in range(eq.GetCount()):
        if eq.Equation(i).replace(" ", "").startswith(f'"{name}"='):
            eq.Equation(i, f'"{name}" = {value_mm}')
            break
    else:
        eq.Add2(-1, f'"{name}" = {value_mm}', True)
    model.ForceRebuild3(False)


def set_props(model, **props):
    pm = model.Extension.CustomPropertyManager("")
    for k, v in props.items():
        pm.Add3(k, 30, str(v), 2)


def export_flat_dxf(model, dxf_path, bend_lines=True):
    opts = 1 | (4 if bend_lines else 0)
    return model.ExportToDWG2(dxf_path, model.GetPathName(), 1, True, None,
                              False, False, opts, None)


if __name__ == "__main__":
    sw = connect()
    print("SolidWorks", sw.RevisionNumber())
    if len(sys.argv) > 1:
        m = open_doc(sw, sys.argv[1])
        print("Открыт:", m.GetTitle())
