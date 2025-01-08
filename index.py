import os
import pytz
import json
import base64
from datetime import datetime
from typing import Dict, Any
from github import update_json_file, open_github_json, GitHubError
from translation import translate_text, TranslationError
from message import send_message, WxPusherError

def generate_error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """
    生成统一的错误响应。

    Args:
        message (str): 错误信息。
        status_code (int): HTTP状态码，默认为500。

    Returns:
        Dict[str, Any]: 格式化的错误响应字典。
    """
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message})
    }

def parse_event(event: str) -> Dict[str, Any]:
    """
    解析传入的事件字符串为字典格式。

    Args:
        event (str): 事件字符串，通常是JSON格式。

    Returns:
        Dict[str, Any]: 包含解析结果的字典。

    Raises:
        ValueError: 如果事件缺少 'body' 字段或 body 内容为空。
        Exception: 如果 Base64 解码失败。
        json.JSONDecodeError: 如果 JSON 解析失败。
    """
    try:
        # 将事件字符串解析为字典
        event_dict = json.loads(event)
        
        # 检查事件中是否包含 'body' 字段
        if "body" not in event_dict:
            raise ValueError("事件缺少'body'")
        
        body = event_dict['body']
        
        # 检查 body 是否为空
        if not body:
            raise ValueError("body 内容为空")
        
        try:
            # 如果事件内容是Base64编码，则解码
            if 'isBase64Encoded' in event_dict and event_dict['isBase64Encoded']:
                body = base64.b64decode(body).decode("utf-8")
        except Exception as e:
            raise Exception(f"Base64 解码失败: {e}")
        
        try:
            # 将解码后的body解析为字典
            body_dict = json.loads(body)
            return body_dict
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON 解析失败: {e}", e.doc, e.pos)
    except json.JSONDecodeError:
        raise json.JSONDecodeError("JSON 无效", event, 0)

def translate_fields(required_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    翻译指定的字段并更新translations.json。

    Args:
        required_fields (Dict[str, Any]): 需要翻译的字段字典。

    Returns:
        Dict[str, Any]: 翻译后的字段字典。
    
    Raises:
        TranslationError: 如果在翻译字段时发生错误。
        GitHubError: 如果GitHub操作失败。
        Exception: 如果发生其他未预见的错误。
    """
    try:
        # 获取translations.json内容
        translations = open_github_json()
        
        translated_fields = {}
        for key, value in required_fields.items():
            if value is not None:
                if key in ["monitor_name", "monitor_type", "monitor_category", "monitor_status"]:
                    if value in translations:
                        translated_value = translations[value]
                    else:
                        try:
                            # 调用翻译API进行翻译
                            translated_value = translate_text(value, source_language='en', target_language='zh')
                            # 更新translations.json
                            translations[value] = translated_value
                            write_response = update_json_file(translations)
                            if write_response['statusCode'] != 200:
                                raise GitHubError(f"更新translations.json失败: {write_response['body']}")
                        except TranslationError as e:
                            raise TranslationError(f"翻译字段 {key} 失败: {str(e)}")
                    translated_fields[key] = translated_value
                else:
                    translated_fields[key] = value

        return translated_fields

    except TranslationError as e:
        raise TranslationError(f"{str(e)}")
    except GitHubError as e:
        raise GitHubError(f"{str(e)}")
    except Exception as e:
        raise Exception(f"函数translate_fields错误: {str(e)}")

def build_message(data: Dict[str, Any]) -> str:
    """
    构建消息内容。

    Args:
        data (Dict[str, Any]): 翻译后的字段字典。

    Returns:
        str: 消息内容。
    
    Raises:
        Exception: 如果在构建消息时发生错误。
    """
    try:
        monitor_name = data.get('monitor_name', None)
        monitor_category = data.get('monitor_category', None)
        monitor_status = data.get('monitor_status', None)
        timestamp = data.get('timestamp', None)

        # 时间转换：将UTC时间戳转换为本地时间（假设为上海时区）
        if timestamp:
            utc_dt = datetime.utcfromtimestamp(timestamp)
            local_tz = pytz.timezone('Asia/Shanghai')  # 假设使用上海时区
            local_dt = utc_dt.astimezone(local_tz)
            time = local_dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time = ''

        # 构建消息内容
        content_parts = [
            f"业务名称: {monitor_name}", 
            f"时间: {time}",
        ]
        if monitor_category:
            content_parts.append(f"分类: {monitor_category}")
        if monitor_status:
            content_parts.append(f"状态: {monitor_status}")       
    
        content = '\n'.join(content_parts)
        closing = "\n\n## [点击访问来源](https://hetrixtools.com)\n\n![logo](https://hetrixtools.com/img/ht_logo.png)"

        full_message = content + closing
        return full_message
    except Exception as e:
        raise Exception(f"构建消息时出错: {str(e)}")

def send_notification(translated_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送通知消息。

    Args:
        translated_fields (Dict[str, Any]): 翻译后的字段字典。

    Returns:
        Dict[str, Any]: 发送结果。
    
    Raises:
        WxPusherError: 如果发送消息时发生错误。
        Exception: 如果发生其他未预见的错误。
    """
    try:
        full_message = build_message(translated_fields)
        summary = translated_fields.get('monitor_name')

        send_response = send_message(full_message, summary)
        if "error" in send_response:
            raise Exception(f"{send_response['error']}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "消息发送成功"})
        }

    except WxPusherError as e:
        raise WxPusherError(f"发送消息失败: {e.message}")
    except Exception as e:
        raise Exception(f"函数send_notification错误: {str(e)}")

def handler(event, context):
    """
    处理Webhook事件的入口函数。

    Args:
        event: Webhook触发的事件内容。
        context: 上下文信息（通常用于云函数环境）。

    Returns:
        Dict[str, Any]: HTTP响应结果。
    """
    try:
        # 解析Webhook内容
        parsed_body = parse_event(event)
        if "status" in parsed_body and parsed_body["status"] == "error":
            return parsed_body
        
        # 提取所有的字段，使用默认值处理缺失的字段
        monitor_id = parsed_body.get('monitor_id', None)
        monitor_name = parsed_body.get('monitor_name', None)
        monitor_target = parsed_body.get('monitor_target', None)
        monitor_type = parsed_body.get('monitor_type', None)
        monitor_category = parsed_body.get('monitor_category', None)
        monitor_status = parsed_body.get('monitor_status', None)
        timestamp = parsed_body.get('timestamp', None)
        monitor_errors = parsed_body.get('monitor_errors', None)
        
        # 创建包含所有字段的字典
        required_fields = {
            "monitor_name": monitor_name,
            "monitor_type": monitor_type,
            "monitor_category": monitor_category,
            "monitor_status": monitor_status
        }
        
        # 翻译字段
        translated_fields = translate_fields(required_fields)
        
        # 添加未翻译的字段
        translated_fields.update({
            "monitor_id": monitor_id,
            "monitor_target": monitor_target,
            "timestamp": timestamp,
            "monitor_errors": monitor_errors
        })
        
        # 发送通知
        send_response = send_notification(translated_fields)
        return send_response

    except ValueError as e:
        return generate_error_response(f"解析事件时发生错误: {str(e)}", 400)
    except TranslationError as e:
        return generate_error_response(f"翻译字段时发生错误: {str(e)}", 500)
    except GitHubError as e:
        return generate_error_response(f"GitHub操作失败: {str(e)}", 500)
    except WxPusherError as e:
        return generate_error_response(f"发送消息失败: {str(e)}", 500)
    except Exception as e:
        return generate_error_response(f"主处理函数异常: {str(e)}", 500)