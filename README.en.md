# url-to-app

Turn any URL into a desktop app shortcut with the site favicon as its icon, in one step.

English | [中文](README.md)

## Features

- Give it a URL and it fetches the site favicon, converting it to a multi-size `.ico` icon
- Opens in Chrome / Edge app-window mode — no address bar, feels like a native app
- Shortcuts are always placed on the user's desktop
- Icons are cached in the skill directory, reused for the same site

## Quick Start

Place the entire `url-to-app` folder into your Codex skills directory:

```
%USERPROFILE%\.codex\skills\url-to-app\
```

Then say this in a Codex conversation:

> URL to app https://www.example.com

Codex runs the script and creates a shortcut with the site's icon on your desktop.

## Manual Execution

You can also run it directly without Codex:

```powershell
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com"

# Custom shortcut name
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com" --name "Example"

# Use an existing icon file (skips online fetch)
python "%USERPROFILE%\.codex\skills\url-to-app\scripts\url_to_app.py" "https://www.example.com" --icon "C:\path\to\icon.ico"
```

## How It Works

1. Normalizes the URL (adds `https://` if missing)
2. Tries site icons in order: `/favicon.ico` → `/favicon.png` → `/apple-touch-icon.png` → HTML-declared icons
3. Converts to multi-size `.ico` via Pillow if needed
4. Locates Chrome or Edge browser
5. Creates a desktop shortcut via WScript.Shell COM (`--app` mode)
6. Refreshes the icon cache
7. Outputs the result path (always on the user's desktop)

## Requirements

- Windows (uses WScript.Shell COM for shortcut creation)
- Chrome or Edge browser
- Python 3.10+
- Pillow (`python -m pip install Pillow`)

## License

MIT License
