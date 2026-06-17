from dataclasses import dataclass
from typing import Any

import pandas as pd


OUTPUT_COLUMNS = [
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


@dataclass(frozen=True)
class FindingTemplate:
    rule_id: str
    rule_name: str
    risk_level: str
    finding_template: str
    recommendation: str


TEMPLATES = {
    "R001": FindingTemplate(
        "R001",
        "非工作时间操作",
        "Medium",
        "发现用户 {username} 于非工作时间执行 {action} 操作，建议进一步核查该操作是否经过授权审批。",
        "核查该操作对应的工单、审批记录及业务背景，确认是否存在越权或异常操作。",
    ),
    "R002": FindingTemplate(
        "R002",
        "重复操作记录",
        "Medium",
        "发现用户 {username} 存在重复的 {action} 操作记录，建议核查日志是否重复采集或业务操作是否被重复执行。",
        "比对源系统流水号、操作对象和时间戳，确认重复记录的产生原因。",
    ),
    "R003": FindingTemplate(
        "R003",
        "账号状态异常",
        "High",
        "发现用户 {username} 在账号状态异常的情况下执行 {action} 操作，建议重点核查账号权限有效性。",
        "核查账号启停用记录、权限变更记录及操作授权依据。",
    ),
    "R004": FindingTemplate(
        "R004",
        "操作人与审批人一致",
        "High",
        "发现用户 {username} 的操作人与审批人为同一账号，可能存在职责分离控制不足。",
        "核查审批流配置和实际审批证据，确认是否违反不相容职责要求。",
    ),
    "R005": FindingTemplate(
        "R005",
        "审计期间外操作",
        "Medium",
        "发现用户 {username} 的日志时间未落在审计期间内，建议确认该记录是否应纳入本次抽查范围。",
        "复核审计期间设置和日志抽取条件，必要时重新获取范围内日志。",
    ),
    "R006": FindingTemplate(
        "R006",
        "关键字段缺失或格式异常",
        "Low",
        "发现用户 {username} 的日志记录存在关键字段缺失或格式异常，可能影响审计证据完整性。",
        "联系系统管理员补充字段说明或重新导出完整日志。",
    ),
}


def build_finding(
    rule_id: str,
    record_index: int,
    row: pd.Series,
    evidence: str,
) -> dict[str, Any]:
    template = TEMPLATES[rule_id]
    username = _display_value(row.get("username"), "未知用户")
    action = _display_value(row.get("action"), "未知操作")
    operation_time = row.get("operation_time")

    return {
        "rule_id": template.rule_id,
        "rule_name": template.rule_name,
        "risk_level": template.risk_level,
        "record_index": record_index,
        "user_id": _display_value(row.get("user_id")),
        "username": username,
        "operation_time": "" if pd.isna(operation_time) else operation_time,
        "action": action,
        "target_object": _display_value(row.get("target_object")),
        "evidence": evidence,
        "audit_finding": template.finding_template.format(username=username, action=action),
        "recommendation": template.recommendation,
    }


def findings_to_frame(findings: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(findings, columns=OUTPUT_COLUMNS)


def _display_value(value: Any, fallback: str = "") -> str:
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return str(value).strip()
