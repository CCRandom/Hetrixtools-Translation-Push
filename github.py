import json
import os
import requests
import base64
from typing import Dict, Any

class GitHubError(Exception):
    """自定义异常类，用于GitHub相关的错误"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def get_github_file_content(repo_path, path, token):
    """
    获取GitHub仓库中指定文件的内容和SHA值。

    Args:
        repo_path (str): 仓库路径，格式为owner/repo。
        path (str): 文件路径。
        token (str): GitHub访问令牌。

    Returns:
        tuple: 文件内容的base64编码字符串和文件的SHA值。如果文件不存在，返回(None, None)。

    Raises:
        GitHubError: 如果请求失败。
    """
    owner, repo = repo_path.split('/')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None, None
    try:
        response.raise_for_status()
        content = response.json()
        return content['content'], content['sha']
    except requests.exceptions.RequestException as e:
        raise GitHubError(f"获取GitHub文件内容失败: {str(e)}")

def update_github_file(repo_path, path, content, sha, token, commit_message):
    """
    更新GitHub仓库中的指定文件。

    Args:
        repo_path (str): 仓库路径，格式为owner/repo。
        path (str): 文件路径。
        content (str): 文件内容的base64编码字符串。
        sha (str): 文件的SHA值。
        token (str): GitHub访问令牌。
        commit_message (str): 提交信息。

    Returns:
        dict: 更新文件后的响应JSON。

    Raises:
        GitHubError: 如果请求失败。
    """
    owner, repo = repo_path.split('/')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": commit_message,
        "content": content,
        "sha": sha
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise GitHubError(f"更新GitHub文件失败: {str(e)}")

def create_github_file(repo_path, path, content, token, commit_message):
    """
    在GitHub仓库中创建指定文件。

    Args:
        repo_path (str): 仓库路径，格式为owner/repo。
        path (str): 文件路径。
        content (str): 文件内容的base64编码字符串。
        token (str): GitHub访问令牌。
        commit_message (str): 提交信息。

    Returns:
        dict: 创建文件后的响应JSON。

    Raises:
        GitHubError: 如果请求失败。
    """
    owner, repo = repo_path.split('/')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": commit_message,
        "content": content
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise GitHubError(f"创建GitHub文件失败: {str(e)}")

def open_github_json():
    """
    打开GitHub仓库中的JSON文件，并返回文件内容。

    Returns:
        dict: JSON文件内容。如果文件不存在或内容不是有效的JSON，则返回空字典。

    Raises:
        GitHubError: 如果请求失败或环境变量未设置。
    """
    try:
        # 从环境变量中获取GitHub相关信息
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo_path = os.getenv('GITHUB_REPO')
        github_file = os.getenv('GITHUB_FILE', 'translations.json')

        if not github_token or not github_repo_path or not github_file:
            raise GitHubError("GitHub相关信息未设置，请检查环境变量。")

        # 获取当前的JSON文件内容
        file_content_base64, _ = get_github_file_content(github_repo_path, github_file, github_token)

        if file_content_base64 is None:
            # 文件不存在，返回空字典
            return {}

        try:
            # 尝试解析文件内容为JSON
            file_content = json.loads(base64.b64decode(file_content_base64).decode('utf-8'))
            return file_content
        except json.JSONDecodeError:
            # 文件内容不是有效的JSON，返回空字典
            return {}
    except GitHubError as e:
        raise GitHubError(f"打开GitHub文件时出错: {e.message}")

def update_json_file(data):
    """
    更新GitHub仓库中的JSON文件内容。

    Args:
        data (dict): 要更新到JSON文件中的数据。

    Returns:
        dict: 更新操作的响应结果。包含状态码和消息。

    Raises:
        GitHubError: 如果请求失败或环境变量未设置。
    """
    try:
        # 从环境变量中获取GitHub相关信息
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo_path = os.getenv('GITHUB_REPO')
        github_file = os.getenv('GITHUB_FILE', 'translations.json')
        commit_message = os.getenv('COMMIT_MESSAGE', 'Update JSON file')

        if not github_token or not github_repo_path or not github_file:
            raise GitHubError("GitHub相关信息未设置，请检查环境变量。")

        # 获取当前的JSON文件内容
        file_content_base64, file_sha = get_github_file_content(github_repo_path, github_file, github_token)

        if file_content_base64 is None:
            # 文件不存在，创建一个新的JSON文件
            file_content = {}
            file_sha = None
            commit_message = "Create JSON file"
        else:
            try:
                # 尝试解析文件内容为JSON
                file_content = json.loads(base64.b64decode(file_content_base64).decode('utf-8'))
            except json.JSONDecodeError:
                # 文件内容不是有效的JSON，清空文件内容
                file_content = {}
                commit_message = "Fix invalid JSON file"

        # 更新JSON内容
        file_content.update(data)

        # 将更新后的内容编码为base64
        new_file_content_base64 = base64.b64encode(json.dumps(file_content).encode('utf-8')).decode('utf-8')

        if file_sha is None:
            # 创建新文件
            create_github_file(github_repo_path, github_file, new_file_content_base64, github_token, commit_message)
        else:
            # 更新现有文件
            update_github_file(github_repo_path, github_file, new_file_content_base64, file_sha, github_token, commit_message)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'JSON file updated successfully'
            })
        }
    except GitHubError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': e.message
            })
        }