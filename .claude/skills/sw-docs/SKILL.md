---
name: sw-docs
description: Визуализация и описание изделия — изображения модели, техническое описание, паспорт из свойств и BOM.
---
1. Изображения: открыть сборку → `model.ShowNamedView2("*Изометрия", 7)` → `ViewZoomtofit2` → `SaveAs3("07_render/<ОБОЗН>_iso.png")`; так же спереди/сверху; разнесённый вид — если есть конфигурация Exploded.
2. Данные: свойства (`CustomPropertyManager`), масса (`CreateMassProperty2`), состав (`GetComponents` или BOM XLSX), габарит (`part.GetPartBox`/`asm.GetBox`).
3. Заполнить шаблоны из `_AI/templates_text/`, сохранить в `08_docs_tech` и `09_passport`.
4. Ревизия ТО = ревизия модели.
