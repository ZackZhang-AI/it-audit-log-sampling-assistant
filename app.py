from pathlib import Path

import pandas as pd
import streamlit as st

from audit_rules import run_audit_checks
from data_loader import load_audit_log


SAMPLE_PATH = Path("sample_data/it_audit_log_sample.csv")


st.set_page_config(page_title="IT 审计日志抽查助手", layout="wide")
st.title("IT 审计日志抽查助手")
st.caption("上传系统操作日志，自动完成期间校验、字段完整性检查、异常时间识别和重复操作筛查。")


with st.sidebar:
    st.header("审计参数")
    audit_start = st.date_input("审计期间开始", value=pd.Timestamp("2025-01-01"))
    audit_end = st.date_input("审计期间结束", value=pd.Timestamp("2025-12-31"))
    if st.button("加载内置样例数据", use_container_width=True):
        st.session_state["use_sample_data"] = True

uploaded_file = st.file_uploader("上传日志文件（CSV / XLSX）", type=["csv", "xlsx", "xls"])


@st.cache_data
def load_sample(path: str) -> pd.DataFrame:
    return load_audit_log(path, path)


def load_uploaded(file) -> pd.DataFrame:
    return load_audit_log(file, file.name)


data = None
source_name = ""
if uploaded_file is not None:
    data = load_uploaded(uploaded_file)
    source_name = uploaded_file.name
elif st.session_state.get("use_sample_data"):
    data = load_sample(str(SAMPLE_PATH))
    source_name = "内置脱敏样例日志"

if data is None:
    st.info("请上传日志文件，或点击侧边栏按钮加载内置样例数据。")
    st.stop()

if audit_start > audit_end:
    st.error("审计期间开始日期不能晚于结束日期。")
    st.stop()

st.subheader(f"数据来源：{source_name}")
st.dataframe(data, use_container_width=True, hide_index=True)

results = run_audit_checks(
    data,
    audit_start=pd.Timestamp(audit_start),
    audit_end=pd.Timestamp(audit_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1),
)

st.subheader("异常检查结果")
total_records = len(data)
total_findings = len(results)
affected_records = results["record_index"].nunique() if not results.empty else 0

metric_cols = st.columns(3)
metric_cols[0].metric("日志记录数", total_records)
metric_cols[1].metric("异常发现数", total_findings)
metric_cols[2].metric("涉及记录数", affected_records)

if results.empty:
    st.success("未发现符合规则的异常记录。")
else:
    severity_order = ["High", "Medium", "Low"]
    selected_levels = st.multiselect("按风险等级筛选", severity_order, default=severity_order)
    filtered = results[results["risk_level"].isin(selected_levels)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv_bytes = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "导出异常结果 CSV",
        data=csv_bytes,
        file_name="it_audit_findings.csv",
        mime="text/csv",
        use_container_width=True,
    )
