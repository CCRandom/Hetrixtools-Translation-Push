# 基于阿里云机器翻译及函数计算，自动翻译hetrixtools的Webhook信息，并将翻译结果保存至github,同时调用wxpusher发送信息

因hetrixtools无法设置中文名字,且阿里云对机器翻译及函数计算均有免费额度故编写以下代码

## 前置工作

本代码需提前获取以下环境变量
| 变量名                  | 示例                      | 备注                       |
| ------------------------| ------------------------  | --------------------------- |
| ALIYUN_ACCESS_KEY_ID    | 随机数字字母组合           | 用于调用阿里云机器翻译      |
| ALIYUN_ACCESS_KEY_SECRET| 随机数字字母组合           | 用于调用阿里云机器翻译      |
| APP_TOKEN               | AT_开头的随机数字字母组合  | 用于调用wxpusher发送信息    |
| UID                     | UID_开头的随机数字字母组合 | 用于调用wxpusher发送信息    |
| GITHUB_REPO             | xxx/xxx仓库地址            | 用于调用github存储翻译结果  |
| GITHUB_TOKEN            | ghp_开头的随机数字字母组合 | 用于调用github存储翻译结果  |

## 获取方式

```s
阿里云机器翻译：https://help.salesmartly.com/docs/ru-he-huo-qu-a-li-fan-yi-AccessKey-ID-he-AccessKey-Secret
wxpusher：https://wxpusher.zjiecode.com/docs/#/
github获取令牌：https://blog.jankiny.ninja/Tech/%E8%8E%B7%E5%8F%96github%E4%B8%AA%E4%BA%BA%E8%AE%BF%E9%97%AE%E4%BB%A4%E7%89%8C%EF%BC%88github-token%EF%BC%89/
```
