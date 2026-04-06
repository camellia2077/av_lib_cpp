# Basic Smoke Test (CLI + GUI)

## Test data
Use `tests/smoke/test_ids.txt`:

```
a-123
abc-1234
abcd-1234
efgh5678
```

Expected export content (`tests/smoke/expected_export_ids.txt`):

```
a123
abc1234
abcd1234
efgh5678
```

## 1) CLI smoke test (automated)
1. Build:
   `python .\tools\script\run.py build --mode release`
2. Run:
   `python .\tools\script\run.py smoke-cli`
3. Pass criteria:
   - Import result contains success count `4`.
   - Query `abc-1234` returns found `1`.
   - Query `zz-9999` returns not found `1`.
   - Export file exists and content equals `tests/smoke/expected_export_ids.txt` (order-insensitive check).

## 2) GUI smoke test (manual)
1. Start GUI:
   `.\out\bin\MyAVLib_Gui.exe`
2. In GUI, create a new database (for example: `smoke_gui_001`).
3. In `从 .txt 文件导入到当前库`:
   - Set path to `tests/smoke/test_ids.txt` (use absolute path).
   - Click `导入`.
   - Check status contains: import success `4`.
4. In query section:
   - Query `abc-1234`, expect status shows found `1`.
   - Query `zz-9999`, expect status shows not found `1`.
5. In export section:
   - Set output path (for example: `C:\Temp\gui_export_ids.txt`).
   - Click `导出`.
6. Verify exported file content equals `tests/smoke/expected_export_ids.txt` (line set equal).

## Notes
- IDs are normalized before storage/export (for example `abc-1234` -> `abc1234`).
- GUI and CLI share the same core business logic, so this smoke test covers end-to-end behavior in both entry points.
