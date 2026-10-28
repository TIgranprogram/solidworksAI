# SolidWorks API — справочник подключения (SW 2026)

Официально: https://help.solidworks.com/2026/English/api/sldworksapi/ (раздел *Release Notes* — изменения версии).
Что нового в API 2026: https://help.solidworks.com/2026/English/WhatsNew/c_wn2026_fundamentals_api.htm
(в 2026 существенно: уведомления о перестановке папок Cut List / Solid Bodies — полезно для Weldment).

## 1. Подключение
| Версия | Номер | ProgID |
|---|---|---|
| 2024 | 32 | `SldWorks.Application.32` |
| 2025 | 33 | `SldWorks.Application.33` |
| **2026** | **34** | `SldWorks.Application.34` |

- **Python**: `pip install pywin32` → `win32com.client.Dispatch("SldWorks.Application")` (уже запущенный SW подхватывается через `GetActiveObject`). Готово: `macros/python/sw_connect.py`.
- **VBA**: встроенный редактор макросов (Tools → Macro). Ссылки на `SldWorks` и `SwConst` Type Library.
- **C#/VB.NET**: `SolidWorks.Interop.sldworks.dll`, `swconst.dll` из `<SW>\api\redist\`.
- Python и SW должны быть одной разрядности (x64). Методы с `ByRef`-аргументами (Errors, Warnings) в Python требуют `VARIANT(pythoncom.VT_BYREF|pythoncom.VT_I4, 0)`.

## 2. Иерархия объектов
`ISldWorks` (приложение) → `IModelDoc2` (любой документ) → `IPartDoc` / `IAssemblyDoc` / `IDrawingDoc`
→ `IFeatureManager`, `ISketchManager`, `ISelectionMgr`, `IModelDocExtension`, `IEquationMgr`, `ICustomPropertyManager`.

## 3. Команды, которые нам нужны
| Задача | Вызов |
|---|---|
| Открыть | `sw.OpenDoc6(path, type, swOpenDocOptions_Silent=1, "", err, warn)` — type: 1 деталь, 2 сборка, 3 чертёж |
| Новый по шаблону | `sw.NewDocument(templatePath, 0, 0, 0)` |
| Сохранить | `model.Save3(1, err, warn)`; как: `model.Extension.SaveAs3(path, 0, 1, None, None, err, warn)` |
| Перестроить | `model.ForceRebuild3(False)`; ошибки дерева — `Feature.GetErrorCode2` |
| Глобальные переменные | `eq = model.GetEquationMgr()`; `eq.Equation(i)` чтение, `eq.SetEquationAndConfigurationOption(i, '"L" = 1500', 0, None)`; `eq.Add2(-1, '"L" = 1500', True)` |
| Размер по имени | `model.Parameter("D1@Эскиз1").SystemValue = 0.5` (**в метрах!**) |
| Свойства файла | `pm = model.Extension.CustomPropertyManager("")`; `pm.Add3(name, 30, value, 2)` (30 = текст, 2 = заменить); `pm.Get6(...)` |
| Материал | `part.SetMaterialPropertyName2("", "SOLIDWORKS Materials", "AISI 304")` |
| Масса | `model.Extension.CreateMassProperty2().Mass` (кг) |
| Тела | `part.GetBodies2(0, True)` (0 = solid) |
| Компоненты сборки | `asm.GetComponents(False)`; `comp.GetPathName()`, `comp.ReferencedConfiguration` |
| Интерференции | `asm.InterferenceDetectionManager` → `GetInterferences()` |
| Cut List (Weldment) | обход `model.FirstFeature()/GetNextFeature()`, тип `"CutListFolder"` → `GetSpecificFeature2().GetBodies()`, свойства: `feat.CustomPropertyManager` |
| Развёртка → DXF | `part.ExportToDWG2(dxfPath, modelPath, 1 /*swExportToDWG_ExportSheetMetal*/, True, None, False, False, opts, None)`; `opts`: 1 геометрия, +4 линии гиба, +8 эскизы, +2 скрытые кромки; **ExportFlatPatternView — устарел** |
| Версия DXF | `sw.SetUserPreferenceIntegerValue(swDxfVersion=…)`; масштаб 1:1 — `swDxfOutputNoScale=1` |
| Тело → отдельная деталь | `body.Select2(False, None)` → `part.SaveToFile3(path, 1, 1, False, "", err, warn)` |
| STEP/IGES | `model.Extension.SaveAs3("x.step", 0, 1, None, None, err, warn)`; AP214: `SetUserPreferenceIntegerValue(swStepAP=214)` |
| Чертёж → PDF | `drw.Extension.SaveAs3("x.pdf", ...)`; все листы — `ExportPdfData.SetSheets(1, None)` |
| Чертёж из модели | `sw.NewDocument(drwTpl)` → `drw.Create3rdAngleViews2(modelPath)` / `CreateDrawViewFromModelView3` → `InsertModelAnnotations3` |
| BOM | `view.InsertBomTable4(...)`; таблица → `ITableAnnotation`, сохранить `BomTable.SaveAsExcel` |
| Скорость | `model.FeatureManager.EnableFeatureTree=False`, `sw.CommandInProgress=True` на время пакета |

Все линейные величины в API — **метры**, углы — **радианы**.

## 4. Полезные источники
- API Help 2026 (примеры VBA/C#/VB.NET у каждого метода): https://help.solidworks.com/2026/English/api/sldworksapi/
- ExportToDWG2: https://help.solidworks.com/2026/English/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IPartDoc~ExportToDWG2.html
- CodeStack (большая библиотека макросов): https://www.codestack.net/solidworks-api/
- Константы: `SolidWorks.Interop.swconst` (swDocumentTypes_e, swSaveAsOptions_e, swUserPreferenceIntegerValue_e)

> Номера констант пользовательских настроек (`swDxfVersion`, `swStepAP` и т.п.) брать из swconst установленной версии — `macros/python/sw_connect.py` генерирует их через `gencache` при первом запуске.
