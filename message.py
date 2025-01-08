import requests
import json
import os
from typing import Dict, Any

# 从环境变量中加载必要的配置信息
APP_TOKEN = os.getenv('APP_TOKEN')  # WxPusher应用令牌
UID = os.getenv('UID')  # 接收消息的用户ID

# WxPusher API endpoint
WXPUSHER_API_URL = 'https://wxpusher.zjiecode.com/api/send/message'

class WxPusherError(Exception):
    """自定义异常类，用于处理与WxPusher相关的错误"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def send_message(full_message: str, summary: str) -> Dict[str, str]:
    """
    发送消息到WxPusher。

    Args:
        full_message (str): 完整的消息内容。
        summary (str): 消息摘要。

    Returns:
        dict: 包含发送结果的状态信息。成功时返回包含"success"键的字典；失败时返回包含"error"键的字典。

    Raises:
        WxPusherError: 如果发送请求过程中发生特定错误。
    """
    try:
        headers = {
            'Content-Type': 'application/json',
        }

        payload = {
            "appToken": APP_TOKEN,  # 使用环境变量中的应用令牌
            "content": full_message,  # 完整的消息内容
            "summary": summary,  # 消息摘要
            "contentType": 3,  # 内容类型，3表示Markdown格式
            "uids": [UID],  # 接收消息的用户ID列表
        }

        response = requests.post(WXPUSHER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 检查HTTP响应状态码是否为200-299范围
        result = response.json()

        if result['code'] != 1000:
            # 如果API返回的code不是1000，表示请求失败
            raise WxPusherError(f"发送消息失败: {result['msg']}")

        return {"success": "消息发送成功"}

    except requests.exceptions.HTTPError as http_err:
        # 处理HTTP错误
        raise WxPusherError(f"HTTP错误发生: {http_err}")
    except WxPusherError as wx_err:
        # 处理WxPusher相关错误
        return {"error": wx_err.message}
    except Exception as e:
        # 处理其他未知错误
        raise WxPusherError(f"发送请求到WxPusher API失败: {e}")