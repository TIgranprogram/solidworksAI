"""Проверка готовности рабочего места: Python, pywin32, SolidWorks, папки. Запуск: python macros/python/check_setup.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ok = True


def report(name, good, hint=""):
    global ok
    ok &= good
    print(f"[{'OK' if good else '!!'}] {name}" + ("" if good else f" -> {hint}"))


report("Python 64-bit", sys.maxsize > 2**32, "нужен 64-битный Python")
try:
    import win32com.client  # noqa: F401
    report("pywin32", True)
except ImportError:
    report("pywin32", False, "pip install -r requirements.txt")
else:
    try:
        from sw_connect import connect
        sw = connect(visible=False)
        report(f"SolidWorks {sw.RevisionNumber()}", True)
    except Exception as e:
        report("SolidWorks", False, f"не найден/не запускается: {e}")

for d in ["00_INBOX", "10_LIBRARY/standards_company", "_AI/knowledge", "projects/_TEMPLATE"]:
    report(d, os.path.isdir(os.path.join(ROOT, d)), "папка отсутствует")
tpl = os.listdir(os.path.join(ROOT, "10_LIBRARY/standards_company"))
report("шаблоны в standards_company", any(f.lower().endswith((".drwdot", ".prtdot", ".asmdot")) for f in tpl),
       "положить шаблоны чертежа/детали/сборки (.drwdot/.prtdot/.asmdot)")
print("\nГотово к работе." if ok else "\nЕсть пункты для исправления (см. !!).")
