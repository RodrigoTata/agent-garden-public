"""
safe_excel.py - Utilidad para lectura y manipulacion segura de Excel en entornos Windows / SharePoint / OneDrive.
Bypassea bloqueos de lectura de Microsoft Excel usando FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE.
"""
import io
import os
import ctypes
import datetime
import collections
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation

def load_workbook_safe(path, data_only=False):
    """Carga un archivo Excel incluso si esta abierto en modo exclusivo en Microsoft Excel o OneDrive."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateFileW(
        path,
        0x80000000, # GENERIC_READ
        1 | 2 | 4,   # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
        None, 3, 0x80, None
    )
    if handle == -1 or handle == 0:
        raise PermissionError(f"No se pudo acceder al archivo (Handle invalido): {path}")

    size = kernel32.GetFileSize(handle, None)
    buf = ctypes.create_string_buffer(size)
    bytes_read = ctypes.c_ulong()
    kernel32.ReadFile(handle, buf, size, ctypes.byref(bytes_read), None)
    kernel32.CloseHandle(handle)

    return openpyxl.load_workbook(io.BytesIO(buf.raw), data_only=data_only)

def check_write_lock(path):
    """Verifica si el archivo esta bloqueado para escritura por Excel."""
    if not os.path.exists(path):
        return False
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateFileW(path, 0x40000000 | 0x80000000, 1 | 2, None, 3, 0x80, None)
    if handle != -1 and handle != 0:
        kernel32.CloseHandle(handle)
        return False # No bloqueado
    return True # Bloqueado

def save_workbook_safe(wb, path):
    """Guarda el workbook. Si esta bloqueado por Excel, lo guarda como _temp y retorna (False, temp_path)."""
    if check_write_lock(path):
        temp_path = path.replace(".xlsx", "_temp.xlsx")
        wb.save(temp_path)
        return False, temp_path
    wb.save(path)
    return True, path

def audit_sheet(ws, key_col=1):
    """Ejecuta una auditoria exhaustiva de calidad de datos y estructura sobre una hoja."""
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1) if ws.cell(1, c).value is not None]
    total_rows = ws.max_row - 1

    # Deteccion de IDs duplicados
    keys = [ws.cell(r, key_col).value for r in range(2, ws.max_row + 1) if ws.cell(r, key_col).value is not None]
    key_counts = collections.Counter(keys)
    duplicate_keys = {k: v for k, v in key_counts.items() if v > 1}

    # Analisis por columna
    col_analysis = []
    for c_idx in range(1, len(headers) + 1):
        col_name = headers[c_idx - 1]
        vals = [ws.cell(r, c_idx).value for r in range(2, ws.max_row + 1)]
        non_nulls = [v for v in vals if v is not None and str(v).strip() != '']
        types = collections.Counter(type(v).__name__ for v in non_nulls)
        unique_vals = set(str(v).strip() for v in non_nulls)

        col_analysis.append({
            "col_idx": c_idx,
            "name": col_name,
            "non_null_count": len(non_nulls),
            "null_count": total_rows - len(non_nulls),
            "types": dict(types),
            "unique_count": len(unique_vals),
            "sample_uniques": list(unique_vals)[:10] if len(unique_vals) <= 15 else []
        })

    return {
        "sheet_name": ws.title,
        "total_rows": total_rows,
        "total_cols": len(headers),
        "headers": headers,
        "duplicate_keys": duplicate_keys,
        "col_analysis": col_analysis,
        "freeze_panes": ws.freeze_panes,
        "conditional_formatting_rules": len(ws.conditional_formatting)
    }
