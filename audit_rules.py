from datetime import time
from typing import Any

import pandas as pd

from data_loader import STANDARD_COLUMNS
from report_writer import OUTPUT_COLUMNS, build_finding, findings_to_frame


REQUIRED_FIELDS = [
    "user_id",
    "username",
    "operation_time",
    "action",
    "target_object",
    "operator_id",
    "approver_id",
    "account_status",
]

WORK_START = time(9, 0)
WORK_END = time(18, 0)


def run_audit_checks(
    df: pd.DataFrame,
    audit_start: pd.Timestamp,
    audit_end: pd.Timestamp,
) -> pd.DataFrame:
    normalized = _ensure_columns(df)
    findings: list[dict[str, Any]] = []

    duplicate_mask = normalized.duplicated(
        subset=["user_id", "action", "target_object", "operation_time"],
        keep=False,
    )

    for record_index, row in normalized.iterrows():
        missing_fields = _missing_required_fields(row)
        if missing_fields:
            findings.append(
                build_finding(
                    "R006",
                    int(record_index),
                    row,
                    f"缺失或格式异常字段: {', '.join(missing_fields)}",
                )
            )

        operation_time = row.get("operation_time")
        if pd.notna(operation_time):
            current_time = operation_time.time()
            if current_time < WORK_START or current_time > WORK_END:
                findings.append(
                    build_finding(
                        "R001",
                        int(record_index),
                        row,
                        f"操作时间 {operation_time} 不在工作时间 09:00-18:00 内",
                    )
                )

            if operation_time < audit_start or operation_time > audit_end:
                findings.append(
                    build_finding(
                        "R005",
                        int(record_index),
                        row,
                        f"操作时间 {operation_time} 不在审计期间 {audit_start.date()} 至 {audit_end.date()} 内",
                    )
                )

        if bool(duplicate_mask.loc[record_index]):
            findings.append(
                build_finding(
                    "R002",
                    int(record_index),
                    row,
                    "user_id、action、target_object、operation_time 与其他记录重复",
                )
            )

        account_status = _text(row.get("account_status")).lower()
        if account_status and account_status != "active":
            findings.append(
                build_finding(
                    "R003",
                    int(record_index),
                    row,
                    f"账号状态为 {account_status}",
                )
            )

        operator_id = _text(row.get("operator_id"))
        approver_id = _text(row.get("approver_id"))
        if operator_id and approver_id and operator_id == approver_id:
            findings.append(
                build_finding(
                    "R004",
                    int(record_index),
                    row,
                    f"操作人 {operator_id} 与审批人 {approver_id} 一致",
                )
            )

    if not findings:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return findings_to_frame(findings)


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column in STANDARD_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA
    normalized["operation_time"] = pd.to_datetime(normalized["operation_time"], errors="coerce")
    return normalized[STANDARD_COLUMNS]


def _missing_required_fields(row: pd.Series) -> list[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if pd.isna(value) or str(value).strip() == "":
            missing.append(field)
    return missing


def _text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()
