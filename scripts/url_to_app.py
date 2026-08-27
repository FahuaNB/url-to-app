#!/usr/bin/env python3
"""Turn a URL into a desktop app shortcut with the site's favicon as icon."""
import argparse
import ctypes
import os
import re
import sys
import urllib.request

HOME = os.path.expanduser("~")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(SKILL_DIR, "icons")


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def normalize_url(raw):
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


def download_icon(base_url):
    candidates = ["/favicon.ico", "/favicon.png", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"]
    for path in candidates:
        try:
            data = fetch(base_url.rstrip("/") + path, timeout=8)
            if len(data) > 100:
                print(f"  icon found: {path} ({len(data)} bytes)")
                return data
        except Exception:
            pass
    try:
        html = fetch(base_url, timeout=10).decode("utf-8", errors="replace")
        for m in re.finditer(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*>', html, re.I):
            href = m.group(1)
            if not re.search(r"\.(ico|png|svg)", href, re.I):
                continue
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = base_url.rstrip("/") + href
            elif not href.startswith("http"):
                continue
            try:
                data = fetch(href, timeout=10)
                if len(data) > 100:
                    print(f"  icon found via HTML: {href} ({len(data)} bytes)")
                    return data
            except Exception:
                continue
    except Exception:
        pass
    return None


def save_as_ico(data, ico_path):
    with open(ico_path, "wb") as f:
        f.write(data)
    if data[:4] == b"\x00\x00\x01\x00":
        return
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
        img.save(ico_path, format="ICO", sizes=sizes)
    except Exception as e:
        print(f"  warning: icon conversion failed ({e})")


def get_desktop():
    CSIDL_DESKTOP = 0
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
    return buf.value


def find_browser():
    candidates = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise RuntimeError("Chrome or Edge not found")


def create_shortcut(url, name, icon_path):
    browser = find_browser()
    desktop = get_desktop()
    lnk_path = os.path.join(desktop, f"{name}.lnk")

    ws = ctypes.windll.shell32
    # Use PowerShell COM for shortcut creation
    import subprocess
    ps_script = f'''
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("{lnk_path}")
$sc.TargetPath = "{browser}"
$sc.Arguments = "--app={url}"
$sc.WorkingDirectory = "{os.path.dirname(browser)}"
$sc.IconLocation = "{icon_path},0"
$sc.Description = "{name}"
$sc.Save()
Write-Output "shortcut created"
'''
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        print(f"  shortcut error: {result.stderr}")
        return None
    # Refresh icon cache
    ctypes.windll.shell32.SHChangeNotify(0x8000000, 0, None, None)
    return lnk_path


def main():
    parser = argparse.ArgumentParser(description="Turn a URL into a desktop app shortcut")
    parser.add_argument("url", help="Target website URL")
    parser.add_argument("--name", "-n", default=None, help="Shortcut display name (default: domain)")
    parser.add_argument("--icon", "-i", default=None, help="Pre-existing .ico path (skip download)")
    args = parser.parse_args()

    url = normalize_url(args.url)
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace("www.", "")
    name = args.name or domain

    os.makedirs(ICON_DIR, exist_ok=True)
    safe_name = re.sub(r"[^\w\-.]", "_", name)

    if args.icon and os.path.isfile(args.icon):
        icon_path = args.icon
        print(f"using provided icon: {icon_path}")
    else:
        print("downloading site icon...")
        data = download_icon(url)
        if data is None:
            print("  no icon found, shortcut will use browser icon")
            icon_path = ""
        else:
            icon_path = os.path.join(ICON_DIR, f"{safe_name}.ico")
            save_as_ico(data, icon_path)
            print(f"  icon saved: {icon_path} ({os.path.getsize(icon_path)} bytes)")

    print(f"creating shortcut: {name}.lnk")
    lnk = create_shortcut(url, name, icon_path)
    if lnk:
        print(f"DONE: {lnk}")
    else:
        print("FAILED to create shortcut")
        sys.exit(1)


if __name__ == "__main__":
    main()
