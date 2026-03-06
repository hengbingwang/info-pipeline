#!/usr/bin/env python3
"""
查询飞书 Bitable 单选/多选字段的选项 ID
运行前确保已设置环境变量：
  FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID
"""

import os
import json
import urllib.request
import urllib.error

BASE_URL = "https://open.feishu.cn/open-apis"

TARGET_FIELDS = {"信息来源", "信息标签", "信息类型", "信息质量等级", "信息沉淀"}


def get_token(app_id: str, app_secret: str) -> str:
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"获取 token 失败: {result}")
    return result["tenant_access_token"]


def get_fields(token: str, app_token: str, table_id: str) -> list:
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"查询字段失败: {result}")
    return result["data"]["items"]


def main():
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    app_token = os.environ.get("FEISHU_BITABLE_APP_TOKEN")
    table_id = os.environ.get("FEISHU_BITABLE_TABLE_ID")

    missing = [k for k, v in {
        "FEISHU_APP_ID": app_id,
        "FEISHU_APP_SECRET": app_secret,
        "FEISHU_BITABLE_APP_TOKEN": app_token,
        "FEISHU_BITABLE_TABLE_ID": table_id,
    }.items() if not v]
    if missing:
        print(f"缺少环境变量: {', '.join(missing)}")
        return

    print("正在获取 token...")
    token = get_token(app_id, app_secret)

    print("正在查询字段...\n")
    fields = get_fields(token, app_token, table_id)

    # type 3 = 单选，type 4 = 多选
    select_types = {3: "单选", 4: "多选"}

    found_any = False
    for field in fields:
        name = field.get("field_name", "")
        ftype = field.get("type")
        if name not in TARGET_FIELDS or ftype not in select_types:
            continue

        found_any = True
        options = field.get("property", {}).get("options", [])
        print(f"【{name}】({select_types[ftype]})")
        for opt in options:
            print(f'  "{opt["name"]}"  →  id: "{opt["id"]}"')
        print()

    if not found_any:
        print("未找到目标字段，请确认表格中已创建对应字段。")


if __name__ == "__main__":
    main()
