#!/usr/bin/env python3
"""OGP画像（1200×630）を作る。

トップページ（index.html）の各ゲームカードの絵柄を流用して assets/og/<slug>.svg を書き、
Google Chrome（ヘッドレス）で assets/og/<slug>.png に書き出す。

使い方:  python3 tools/build-og.py
Chrome の場所が違うときは  CHROME=/path/to/chrome python3 tools/build-og.py
"""
import html
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
W, H = 1200, 630

# slug: (ゲーム名, 一般名・ひとこと, 絵の背景)
GAMES = {
    "dots": ("陣取りドット", "ドット＆ボックス", "soft"),
    "memory": ("ふたりの神経衰弱", "トランプいらずの記憶ゲーム", "soft"),
    "number-poker": ("数字ポーカー", "1〜10で読み合う心理戦", "felt"),
    "push": ("押し込みならべ", "押し込んで5つ並べる", "soft"),
    "connect4": ("コネクト4", "四目並べ", "soft"),
    "gogo-shogi": ("5五将棋", "5×5のミニ将棋", "soft"),
    "nim": ("ニム", "最後の1個を取ったら負け", "soft"),
}

# サイトと同じ M PLUS Rounded 1c を Google Fonts から読み込む（読めないときはヒラギノ丸ゴ）
FONT = "'M PLUS Rounded 1c','Hiragino Maru Gothic ProN',sans-serif"
# トップページの絵柄が使う色（ライトテーマの値）
STYLE = """<style>
@import url("https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800&amp;display=block");
svg{--bg:#eef1f6;--fg:#1d2433;--muted:#6b7488;--card:#ffffff;--hl:#f0b429;--p1:#2f5bd3;--p2:#d9466f;
--p1-soft:rgba(47,91,211,.18);--p2-soft:rgba(217,70,111,.18);--bg-soft:#e3e8f1;--ink:#1d2433;--line:#cfd5e1;
--paper:#fbf8f1;--felt:#1e2d29;--gold:#e8b64c;--tile:#f7f1e6;--tile-edge:#cbb894}
text{font-family:%s}
</style>""" % FONT


def card_art(slug):
    """index.html から、そのゲームのカードに描かれている <svg viewBox="0 0 120 84"> の中身を取り出す。"""
    src = (ROOT / "index.html").read_text()
    i = src.index(f'href="games/{slug}.html"')
    m = re.search(r'<svg viewBox="0 0 120 84">(.*?)</svg>', src[i:], re.S)
    # パターンの id が画像ごとに重ならないようにする
    return m.group(1).replace('id="mback"', f'id="mback-{slug}"').replace("url(#mback)", f"url(#mback-{slug})")


def logo(x, y, r, size, fill="var(--fg)"):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--p1)"/>'
            f'<circle cx="{x + r * 1.45}" cy="{y}" r="{r}" fill="var(--p2)" fill-opacity=".9"/>'
            f'<text x="{x + r * 2.45 + 10}" y="{y + size * .36}" font-size="{size}" font-weight="800" fill="{fill}">ふたりあそび</text>')


def game_svg(slug):
    name, sub, bg = GAMES[slug]
    e = html.escape
    panel = "var(--felt)" if bg == "felt" else "var(--bg-soft)"
    name_size = min(84, int(500 / len(name)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{STYLE}
<rect width="{W}" height="{H}" fill="var(--bg)"/>
<rect x="56" y="56" width="560" height="518" rx="36" fill="{panel}"/>
<svg x="86" y="141" width="500" height="350" viewBox="0 0 120 84">{card_art(slug)}</svg>
{logo(670, 132, 14, 30)}
<text x="668" y="{300}" font-size="{name_size}" font-weight="800" fill="var(--fg)">{e(name)}</text>
<text x="670" y="{300 + 64}" font-size="34" font-weight="800" fill="var(--muted)">{e(sub)}</text>
<g font-size="24" font-weight="800">
  <rect x="668" y="420" width="156" height="48" rx="24" fill="var(--card)"/><text x="746" y="452" text-anchor="middle" fill="var(--fg)">2人対戦</text>
  <rect x="836" y="420" width="104" height="48" rx="24" fill="var(--card)"/><text x="888" y="452" text-anchor="middle" fill="var(--fg)">無料</text>
  <rect x="952" y="420" width="164" height="48" rx="24" fill="var(--card)"/><text x="1034" y="452" text-anchor="middle" fill="var(--fg)">スマホ1台</text>
</g>
<text x="670" y="548" font-size="22" fill="var(--muted)">futari-asobi.pages.dev</text>
</svg>
"""


def top_svg():
    tiles = []
    n, tw, th, gap = len(GAMES), 140, 98, 14
    x0 = (W - (n * tw + (n - 1) * gap)) / 2
    for k, (slug, (_, _, bg)) in enumerate(GAMES.items()):
        x = x0 + k * (tw + gap)
        panel = "var(--felt)" if bg == "felt" else "var(--card)"
        tiles.append(f'<rect x="{x}" y="420" width="{tw}" height="{th}" rx="18" fill="{panel}"/>'
                     f'<svg x="{x + 10}" y="427" width="{tw - 20}" height="{th - 14}" viewBox="0 0 120 84">{card_art(slug)}</svg>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{STYLE}
<rect width="{W}" height="{H}" fill="var(--bg)"/>
<circle cx="390" cy="176" r="30" fill="var(--p1)"/><circle cx="433" cy="176" r="30" fill="var(--p2)" fill-opacity=".9"/>
<text x="490" y="206" font-size="84" font-weight="800" fill="var(--fg)">ふたりあそび</text>
<text x="600" y="290" text-anchor="middle" font-size="38" font-weight="800" fill="var(--fg)">スマホ1台で、2人ですぐ対戦</text>
<text x="600" y="346" text-anchor="middle" font-size="26" fill="var(--muted)">インストール不要・無料のミニゲーム集　｜　futari-asobi.pages.dev</text>
{''.join(tiles)}
</svg>
"""


def export(svg_path, png_path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--virtual-time-budget=8000",  # Webフォントの読み込みを待つ
                   
                    f"--window-size={W},{H}", f"--screenshot={png_path}", svg_path.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = {slug: game_svg(slug) for slug in GAMES}
    pages["top"] = top_svg()
    for slug, svg in pages.items():
        svg_path = OUT / f"{slug}.svg"
        svg_path.write_text(svg)
        export(svg_path, OUT / f"{slug}.png")
        print("wrote", (OUT / f"{slug}.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
