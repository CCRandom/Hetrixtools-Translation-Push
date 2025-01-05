import json
import base64
from datetime import datetime
from typing import Dict, Any
import pytz
import os
from github import Github

# 用于加载环境变量
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_TRANSLATION_PATH = os.getenv('GITHUB_TRANSLATION_PATH', 'translations.json')
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID')
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET')

# 时区设置
local_tz = pytz.timezone('Asia/Shanghai')

def load_translations_from_github(github: Github, repo_name: str, file_path: str) -> Dict[str, str]:
    try:
        repo = github.get_repo(repo_name)
        contents = repo.get_contents(file_path)
        translations = json.loads(base64.b64decode(contents.content).decode('utf-8'))
        return translations
    except Exception as e:
        return {"error": f"Failed to load translations from GitHub: {e}"}

def save_translations_to_github(github: Github, repo_name: str, file_path: str, translations: Dict[str, str]) -> None:
    try:
        repo = github.get_repo(repo_name)
        contents = repo.get_contents(file_path)
        repo.update_file(
            path=file_path,
            message="Update translations",
            content=json.dumps(translations, ensure_ascii=False, indent=4),
            sha=contents.sha
        )
        return None
    except Exception as e:
        return {"error": f"Failed to save translations to GitHub: {e}"}

def translate_text(text: str, source_language: str, target_language: str, translations: Dict[str, str]) -> str:
    if text in translations:
        return translations[text]

    client = Github(GITHUB_TOKEN)
    github = Github(GITHUB_TOKEN)
    request = CommonRequest()
    request.set_domain('mt.cn-hangzhou.aliyuncs.com')
    request.set_version('2018-10-12')
    request.set_action_name('TranslateGeneral')
    request.add_query_param('SourceLanguage', source_language)
    request.add_query_param('TargetLanguage', target_language)
    request.add_query_param('FormatType', 'text')
    request.add_query_param('SourceText', text)

    try:
        response = client.do_action_with_exception(request)
        response_json = json.loads(response)
        translated_text = response_json['Data']['Translated']
        translations[text] = translated_text
        save_result = save_translations_to_github(github, GITHUB_REPO, GITHUB_TRANSLATION_PATH, translations)
        if save_result is not None:
            return save_result
        return translated_text
    except Exception as e:
        return {"error": f"Translation failed: {e}"}
