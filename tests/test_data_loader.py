from io import BytesIO, StringIO

import pandas as pd

from data_loader import load_audit_log, normalize_columns


def test_normalize_columns_maps_common_chinese_names():
    raw = pd.DataFrame(
        {
            "用户ID": ["U001"],
            "用户名": ["张三"],
            "操作时间": ["2025-03-01 10:00:00"],
            "操作": ["查询报表"],
            "操作对象": ["财务报表"],
            "操作人ID": ["U001"],
            "审批人ID": ["M001"],
            "账号状态": ["active"],
            "IP地址": ["10.0.0.1"],
            "角色名称": ["审计员"],
        }
    )

    normalized = normalize_columns(raw)

    assert list(normalized.columns) == [
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
    assert normalized.loc[0, "username"] == "张三"


def test_load_audit_log_reads_csv_and_parses_operation_time():
    csv_data = StringIO(
        "user_id,username,operation_time,action,target_object,operator_id,approver_id,account_status\n"
        "U001,Alice,2025-03-01 10:00:00,export,customer_report,U001,M001,active\n"
    )

    loaded = load_audit_log(csv_data, "case.csv")

    assert loaded.loc[0, "operation_time"] == pd.Timestamp("2025-03-01 10:00:00")
    assert loaded.loc[0, "user_id"] == "U001"


def test_load_audit_log_reads_xlsx():
    workbook = BytesIO()
    pd.DataFrame(
        {
            "user_id": ["U002"],
            "username": ["Bob"],
            "operation_time": ["2025-04-01 11:30:00"],
            "action": ["approve"],
            "target_object": ["change_request"],
            "operator_id": ["U002"],
            "approver_id": ["M002"],
            "account_status": ["active"],
        }
    ).to_excel(workbook, index=False)
    workbook.seek(0)

    loaded = load_audit_log(workbook, "case.xlsx")

    assert loaded.loc[0, "operation_time"] == pd.Timestamp("2025-04-01 11:30:00")
    assert loaded.loc[0, "target_object"] == "change_request"


def test_load_audit_log_keeps_invalid_time_as_nat_without_crashing():
    csv_data = StringIO(
        "user_id,username,operation_time,action,target_object,operator_id,approver_id,account_status\n"
        "U003,Cara,not-a-date,delete,user_table,U003,M003,active\n"
    )

    loaded = load_audit_log(csv_data, "case.csv")

    assert pd.isna(loaded.loc[0, "operation_time"])
