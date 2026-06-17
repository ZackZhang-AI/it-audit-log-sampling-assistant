import pandas as pd

from audit_rules import run_audit_checks


def _base_record(**overrides):
    record = {
        "user_id": "U001",
        "username": "Alice",
        "operation_time": pd.Timestamp("2025-03-01 10:00:00"),
        "action": "view_report",
        "target_object": "finance_report",
        "operator_id": "U001",
        "approver_id": "M001",
        "account_status": "active",
        "ip_address": "10.0.0.1",
        "role_name": "auditor",
    }
    record.update(overrides)
    return record


def _result_for(records):
    return run_audit_checks(
        pd.DataFrame(records),
        audit_start=pd.Timestamp("2025-01-01"),
        audit_end=pd.Timestamp("2025-12-31"),
    )


def test_detects_non_working_hours_operation():
    results = _result_for(
        [_base_record(operation_time=pd.Timestamp("2025-03-01 22:15:00"), action="grant_admin")]
    )

    assert "R001" in set(results["rule_id"])
    finding = results.loc[results["rule_id"] == "R001", "audit_finding"].iloc[0]
    assert "非工作时间" in finding
    assert "grant_admin" in finding


def test_detects_duplicate_operation_records():
    record = _base_record(action="export", target_object="customer_report")

    results = _result_for([record, record.copy()])

    duplicate_results = results[results["rule_id"] == "R002"]
    assert len(duplicate_results) == 2
    assert set(duplicate_results["risk_level"]) == {"Medium"}


def test_detects_abnormal_account_status():
    results = _result_for([_base_record(account_status="disabled")])

    assert "R003" in set(results["rule_id"])
    assert "账号状态为 disabled" in results.loc[results["rule_id"] == "R003", "evidence"].iloc[0]


def test_detects_operator_and_approver_same_person():
    results = _result_for([_base_record(operator_id="U001", approver_id="U001")])

    assert "R004" in set(results["rule_id"])
    assert set(results.loc[results["rule_id"] == "R004", "risk_level"]) == {"High"}


def test_detects_record_outside_audit_period():
    results = _result_for([_base_record(operation_time=pd.Timestamp("2026-01-01 09:30:00"))])

    assert "R005" in set(results["rule_id"])
    assert "审计期间" in results.loc[results["rule_id"] == "R005", "audit_finding"].iloc[0]


def test_detects_missing_required_fields_and_invalid_time():
    results = _result_for(
        [
            _base_record(
                user_id="",
                username=None,
                operation_time=pd.NaT,
                action="delete",
            )
        ]
    )

    missing = results[results["rule_id"] == "R006"]
    assert len(missing) == 1
    assert missing["risk_level"].iloc[0] == "Low"
    assert "user_id" in missing["evidence"].iloc[0]
    assert "operation_time" in missing["evidence"].iloc[0]


def test_output_columns_are_stable_when_no_findings():
    results = _result_for([_base_record()])

    assert list(results.columns) == [
        "rule_id",
        "rule_name",
        "risk_level",
        "record_index",
        "user_id",
        "username",
        "operation_time",
        "action",
        "target_object",
        "evidence",
        "audit_finding",
        "recommendation",
    ]
    assert results.empty
