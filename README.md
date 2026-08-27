# url-to-app

把任意网址一键变成带网站图标的桌面应用快捷方式。

[English](README.en.md) | 中文

## 功能

- 输入网址，自动抓取网站 favicon 并转换为多尺寸 `.ico` 图标
- 使用 Chrome / Edge 应用窗口模式打开，无地址栏，体验接近原生应用
- 快捷方式固定输出到用户桌面
- 图标缓存到技能目录，重复创建同一网站时直接复用

## 快速开始

把整个 `url-to-app` 文件夹放到 Codex 技能目录：

```
%USERPROFILE%\.codex\skills\url-to-app\
```

然后在 Codex 对话里说：

> 网址变应用 https://www.example.com

Codex 会自动执行脚本，在桌面生成带该网站图标的快捷方式。

## 手动执行

不通过 Codex，也可以直接用命令行：

```powershell
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com"

# 指定快捷方式名称
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com" --name "示例"

# 使用已有图标文件（跳过在线抓取）
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com" --icon "C:\path\to\icon.ico"
```

## 工作流程

1. 规范化 URL（自动补 `https://`）
2. 依次尝试下载网站图标：`/favicon.ico` → `/favicon.png` → `/apple-touch-icon.png` → HTML 里声明的图标
3. 如果图标不是 `.ico` 格式，用 Pillow 转换为多尺寸 `.ico`
4. 查找 Chrome 或 Edge 浏览器
5. 用 WScript.Shell COM 创建桌面快捷方式（`--app` 模式）
6. 刷新图标缓存
7. 输出结果路径（始终位于用户桌面）

## 依赖

- Windows 系统（依赖 WScript.Shell COM 创建快捷方式）
- Chrome 或 Edge 浏览器
- Python 3.10+
- Pillow（`python -m pip install Pillow`）

## 许可

MIT License
