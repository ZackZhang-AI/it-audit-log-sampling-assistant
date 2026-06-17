# IT 审计日志抽查助手

一个面向 IT 审计日志抽查场景的本地 Streamlit 工具。项目支持上传系统操作日志 Excel/CSV，自动完成期间校验、字段完整性检查、异常时间识别、重复操作筛查，并生成中文审计关注点说明。

这个项目适合放在 GitHub 中作为简历项目材料，用来支撑“抽取 IT 系统业务凭证、运行日志，完成多条数据交叉验证”的经历描述。

## 功能特点

- 支持上传 `.csv`、`.xlsx`、`.xls` 日志文件
- 支持加载内置脱敏样例数据，一键演示完整流程
- 自动识别常见中文字段名，并映射为标准日志字段
- 检查非工作时间操作、重复操作、账号状态异常、操作人与审批人一致、审计期间外日志、关键字段缺失
- 按风险等级展示异常结果
- 自动生成审计关注点说明和核查建议
- 支持导出异常检查结果 CSV

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

打开页面后，可以点击侧边栏的“加载内置样例数据”查看演示结果，也可以上传自己的日志文件。

## 输入字段

标准日志字段如下：

```text
user_id, username, operation_time, action, target_object,
operator_id, approver_id, account_status, ip_address, role_name
```

工具也支持常见中文字段名，例如：

```text
用户ID, 用户名, 操作时间, 操作, 操作对象,
操作人ID, 审批人ID, 账号状态, IP地址, 角色名称
```

## 审计规则

| 规则 | 风险等级 | 说明 |
| --- | --- | --- |
| 非工作时间操作 | Medium | 操作时间早于 09:00 或晚于 18:00 |
| 重复操作记录 | Medium | `user_id + action + target_object + operation_time` 完全重复 |
| 账号状态异常 | High | `account_status` 不等于 `active` |
| 操作人与审批人一致 | High | `operator_id` 与 `approver_id` 相同 |
| 审计期间外操作 | Medium | 日志时间未落在页面设置的审计期间内 |
| 关键字段缺失或格式异常 | Low | 必要字段为空，或操作时间无法解析 |

## 输出字段

```text
rule_id, rule_name, risk_level, record_index,
user_id, username, operation_time, action, target_object,
evidence, audit_finding, recommendation
```

示例审计关注点：

```text
发现用户 Bob 于非工作时间执行 grant_admin 操作，建议进一步核查该操作是否经过授权审批。
```

## 项目结构

```text
.
├── app.py
├── audit_rules.py
├── data_loader.py
├── report_writer.py
├── requirements.txt
├── sample_data/
│   └── it_audit_log_sample.csv
└── tests/
    ├── test_audit_rules.py
    └── test_data_loader.py
```

## 测试

```bash
python -m pytest tests/test_audit_rules.py tests/test_data_loader.py -q
```

测试覆盖数据读取、字段映射、时间解析和主要审计规则。

## 简历写法

基于 IT 审计日志抽查场景，开发日志异常检查助手，支持对系统操作日志进行期间校验、字段完整性检查、异常时间识别和重复操作筛查，并自动生成审计关注点说明，辅助提升 IT 审计资料核查效率。
