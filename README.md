# Text Toolbox MCP

一个无需业务密钥、无外部写入副作用的 Python MCP 服务，提供三个纯文本工具。

## 工具

| 工具 | 参数 | 返回 |
| --- | --- | --- |
| `text_stats` | `text: str` | Unicode 码点数、UTF-8 字节数、按空白切分的词数、行数 |
| `sha256_text` | `text: str` | 原始文本 UTF-8 编码的 SHA-256 十六进制摘要，以及算法与编码名 |
| `deduplicate_lines` | `text: str`, `case_sensitive: bool = true` | 保留首次出现行的文本、输入/输出行数和删除行数 |

### 明确的行为和限制

- 每次输入最多 100,000 个 Unicode 码点；超限抛出 `ValueError`，通过 MCP 作为工具错误返回。
- 不执行输入内容、不读写文件、不访问外部网络、不在应用中持久化输入。MCP 客户端及平台日志策略不由本服务控制，不建议提交机密文本。
- 统计不是中文分词；词数为连续非空白片段数。空文本行数为 0，末尾换行不额外计一行。
- 摘要不做 Unicode 或换行归一化；哈希不是加密，也不能代替安全的密码存储方案。
- 去重保留行内空格和首次出现顺序；不区分大小写时使用 Unicode `casefold`。输出统一为 LF，输入有末尾换行时输出也保留一个末尾 LF。
- 只接受有效 Unicode 文本；无法编码为 UTF-8 的孤立代理字符会返回工具错误。
- 无需业务环境变量或下游授权。Hub 网关访问权限由平台管理。

## 平台入口

- Python：3.10 及以上；目标 Hub 运行时：`python3.10`。
- SDK：官方 `mcp>=1.26,<2`，不使用第三方同名 FastMCP 包。
- 入口模块：`text_toolbox_mcp.server`；模块级对象：`mcp`。
- 无状态 Streamable HTTP，端口 `9000`，路径 `/mcp`；平台负责托管和网关鉴权，不在导入时启动服务器。

## 本地开发

```bash
uv sync --python 3.10 --locked
uv run --python 3.10 --locked python -m unittest discover -s tests -v
uv build
```

需要手动启动本地 HTTP 调试时（仅用于开发，默认未开启平台网关鉴权）：

```bash
uv run python -c "from text_toolbox_mcp.server import mcp; mcp.run(transport='streamable-http')"
```

该开发服务监听 `0.0.0.0:9000`，请只在可信本地网络调试，不直接暴露到公网。

## MCP Hub 发布

`mcp-hub-draft.json` 为本地发布表单，不是上传源码的替代品。需先取得用户公开代码授权，将项目推送到匿名可拉取的公开 HTTPS Git 仓库，再由 Hub inspect 获取真实 `inspection_id` 和固定 commit 后发布。

未配置仓库时 `repo_url` 为空、`inspection_id` 为 null；这些字段不代表已通过平台验证。Hub Token 仅保存在客户端安全配置中，不写入代码、草稿或 Git。
