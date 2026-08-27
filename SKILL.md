---
name: url-to-app
description: 把网址变成带网站图标的桌面应用快捷方式。当用户说"网址变应用"或要求将某个网站做成桌面应用时触发。使用 Edge/Chrome 应用窗口模式，自动抓取网站 favicon 作为图标。
---

# URL to App

把任意网址一键变成带网站图标的桌面应用快捷方式。

## 使用场景
- 用户说「网址变应用」
- 用户要求把某个网站做成桌面应用/快捷方式
- 用户想让某个网页像独立应用一样打开（无浏览器地址栏）

## 执行方式

运行以下命令（替换 `<URL>` 为目标网址）：

```powershell
python "$env:USERPROFILE\.codex\skills\url-to-app\scripts\url_to_app.py" "<URL>"
```

### 可选参数

```powershell
# 指定快捷方式名称（默认使用域名）
python "$env:USERPROFILE\.codex\skills\url-to-app\scripts\url_to_app.py" "<URL>" --name "自定义名称"

# 使用已有图标文件（跳过在线抓取）
python "$env:USERPROFILE\.codex\skills\url-to-app\scripts\url_to_app.py" "<URL>" --icon "C:\path\to\icon.ico"
```

## 工作流程

1. 规范化 URL（自动补 `https://`）
2. 依次尝试下载网站图标：`/favicon.ico` → `/favicon.png` → `/apple-touch-icon.png` → HTML 里声明的图标
3. 如果图标不是 `.ico` 格式，用 Pillow 转换为多尺寸 `.ico`
4. 查找 Chrome 或 Edge 浏览器
5. 用 WScript.Shell COM 创建桌面快捷方式（`--app` 模式）
6. 刷新图标缓存
7. 输出结果路径（必须位于用户桌面）

## 输出位置（硬性规则）
- 快捷方式 .lnk 文件**只能**输出到用户桌面，通过 SHGetFolderPathW(CSIDL_DESKTOP) 获取路径
- 即使脚本参数指定了其他目录，也必须强制覆盖为桌面路径
- 图标缓存文件保存在技能目录的 icons/ 子目录，不属于用户输出物

## 注意事项
- 图标缓存在 `icons/` 子目录，按网站名保存，重复创建同一网站时会复用
- 需要已安装 Pillow（`python -m pip install Pillow`）
- **快捷方式必须始终输出到用户桌面（硬性规则）**：使用 SHGetFolderPathW(CSIDL_DESKTOP) 获取真实桌面路径，不得输出到其他位置
- 如果找不到任何图标，快捷方式会退回使用浏览器默认图标

