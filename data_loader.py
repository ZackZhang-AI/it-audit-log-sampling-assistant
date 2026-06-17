from pathlib import Path
from typing import BinaryIO, TextIO

import pandas as pd


STANDARD_COLUMNS = [
    "user_id",
    "username",
    "operation_time",
    "action",
    "target_object",
    "operator_id",
    "approver_id",
    "account_status",
    "ip_address",
    "role_name",
]


COLUMN_ALIASES = {
    "用户ID": "user_id",
    "用户id": "user_id",
    "账号ID": "user_id",
    "账号": "user_id",
    "用户名": "username",
    "用户名称": "username",
    "姓名": "username",
    "操作时间": "operation_time",
    "日志时间": "operation_time",
    "时间": "operation_time",
    "操作": "action",
    "操作类型": "action",
    "操作名称": "action",
    "操作对象": "target_object",
    "业务对象": "target_object",
    "目标对象": "target_object",
    "操作人ID": "operator_id",
    "操作人": "operator_id",
    "执行人": "operator_id",
    "审批人ID": "approver_id",
    "审批人": "approver_id",
    "复核人": "approver_id",
    "账号状态": "account_status",
    "账户状态": "account_status",
    "状态": "account_status",
    "IP地址": "ip_address",
    "登录IP": "ip_address",
    "来源IP": "ip_address",
    "角色名称": "role_name",
    "角色": "role_name",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename known Chinese/English variants to the standard audit log schema."""
    rename_map = {}
    for column in df.columns:
        cleaned = str(column).strip()
        lower_cleaned = cleaned.lower()
        rename_map[column] = COLUMN_ALIASES.get(cleaned, COLUMN_ALIASES.get(lower_cleaned, lower_cleaned))

    normalized = df.rename(columns=rename_map).copy()
    for column in STANDARD_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    return normalized[STANDARD_COLUMNS]


def load_audit_log(file: str | Path | BinaryIO | TextIO, filename: str | None = None) -> pd.DataFrame:
    suffix_source = filename or getattr(file, "name", "")
    suffix = Path(str(suffix_source)).suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        raw = pd.read_excel(file)
    elif suffix == ".csv" or not suffix:
        raw = pd.read_csv(file)
    else:
        raise ValueError("仅支持 CSV、XLSX 或 XLS 格式的日志文件。")

    normalized = normalize_columns(raw)
    normalized["operation_time"] = pd.to_datetime(normalized["operation_time"], errors="coerce")
    return normalized
