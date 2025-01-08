from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
import json
import os

class TranslationError(Exception):
    """自定义异常类，用于处理翻译相关的错误"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def translate_text(source_text: str, source_language: str = 'en', target_language: str = 'zh') -> str:
    """
    使用阿里云翻译服务将文本从一种语言翻译成另一种语言。

    Args:
        source_text (str): 要翻译的源文本。
        source_language (str, optional): 源语言代码，默认为'en'（英文）。
        target_language (str, optional): 目标语言代码，默认为'zh'（中文）。

    Returns:
        str: 翻译后的文本。

    Raises:
        TranslationError: 如果阿里云访问密钥未设置或翻译请求失败。
    """
    try:
        # 从环境变量中获取阿里云访问密钥ID和密钥
        access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')

        if not access_key_id or not access_key_secret:
            raise TranslationError("阿里云访问密钥未设置，请检查环境变量。")

        # 创建AccessKeyCredential实例，用于认证
        credentials = AccessKeyCredential(access_key_id, access_key_secret)

        # 创建AcsClient实例，用于与阿里云API进行交互
        client = AcsClient(region_id='ap-northeast-1', credential=credentials)

        # 创建CommonRequest实例，用于构建具体的API请求
        request = CommonRequest()
        request.set_accept_format('json')  # 设置响应格式为JSON
        request.set_domain('mt.aliyuncs.com')  # 设置请求域名
        request.set_method('POST')  # 设置HTTP方法为POST
        request.set_protocol_type('https')  # 设置协议类型为HTTPS
        request.set_version('2018-10-12')  # 设置API版本
        request.set_action_name('TranslateGeneral')  # 设置API操作名称

        # 设置请求参数，包括源语言、目标语言、格式类型和要翻译的文本
        request.add_query_param('SourceLanguage', source_language)
        request.add_query_param('TargetLanguage', target_language)
        request.add_query_param('SourceText', source_text)
        request.add_query_param('FormatType', 'text')  # 添加格式类型参数

        # 发送请求并获取响应
        response = client.do_action(request)

        # 将响应转换为JSON格式
        response_json = json.loads(response.decode('utf-8'))

        # 打印响应内容以便调试
        print(f"Translation Response: {response_json}")

        # 检查响应中是否包含预期的字段
        if 'Data' in response_json and 'Translated' in response_json['Data']:
            translated_text = response_json['Data']['Translated']
            return translated_text
        else:
            raise TranslationError(f"响应中未找到翻译结果: {response_json}")

    except Exception as e:
        raise TranslationError(f"{str(e)}")