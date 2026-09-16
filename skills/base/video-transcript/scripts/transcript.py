#!/usr/bin/env python3
"""
Чистая транскрипция из субтитров YouTube (.json3 / .srv1 / .vtt / .srt).
Только стандартная библиотека.

    python3 transcript.py sub.en.vtt                     # сплошной текст абзацами
    python3 transcript.py sub.en.json3 -m ts -i 30       # блоки с тайм-кодом раз в 30 с
    python3 transcript.py sub.vtt --chapters info.json   # + заголовки глав
"""

import argparse
import html
import json
import re
import sys
import textwrap

TAG_RE = re.compile(r"<[^>]*>")
TS_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")
CUE_RE = re.compile(r"(\S+)\s+-->\s+(\S+)")
VTT_SKIP = ("WEBVTT", "Kind:", "Language:", "NOTE", "STYLE", "REGION")


# ---------- разбор ----------

def parse_ts(value):
    m = TS_RE.match(value)
    if not m:
        return 0.0
    h, mnt, sec, ms = m.groups()
    return int(h or 0) * 3600 + int(mnt) * 60 + int(sec) + int(ms.ljust(3, "0")) / 1000


def clean(line):
    """Снять инлайн-теги, развернуть entity, схлопнуть пробелы."""
    line = TAG_RE.sub("", line)
    # srv1/srv3 приходят экранированными дважды: &amp;#39; вместо &#39;.
    # Разворачиваем до стабилизации, но не больше двух раз, чтобы не съесть текст.
    for _ in range(2):
        unescaped = html.unescape(line)
        if unescaped == line:
            break
        line = unescaped
    line = TAG_RE.sub("", line)          # entity мог развернуться в тег
    line = line.replace(" ", " ").replace("​", "")
    return " ".join(line.split())


def read_vtt(text):
    """-> [(start, end, text)] по одной записи на строку реплики."""
    cues, lines, i = [], text.replace("\r\n", "\n").split("\n"), 0
    while i < len(lines):
        raw = lines[i]
        m = CUE_RE.search(raw) if "-->" in raw else None
        if not m or raw.startswith(VTT_SKIP):
            i += 1
            continue
        start, end = parse_ts(m.group(1)), parse_ts(m.group(2))
        i += 1
        while i < len(lines):
            # блок кончается ПУСТОЙ строкой; строка из одного пробела/nbsp —
            # это плейсхолдер YouTube, за ним еще идет текст реплики
            if lines[i] == "" or "-->" in lines[i]:
                break
            body = clean(lines[i])
            if body:
                cues.append((start, end, body))
            i += 1
    return cues


SRV1_RE = re.compile(
    r'<text\s+start="([\d.]+)"(?:\s+dur="([\d.]+)")?[^>]*>(.*?)</text>', re.S)


def read_srv1(text):
    """Плоский XML YouTube: <transcript><text start dur>...</text></transcript>."""
    cues = []
    for start, dur, body in SRV1_RE.findall(text):
        body = clean(body)
        if not body:
            continue
        start = float(start)
        cues.append((start, start + float(dur or 0), body))
    return cues


def read_json3(text):
    data = json.loads(text)
    cues = []
    for ev in data.get("events", []):
        if ev.get("aAppend"):            # служебный перевод строки rolling window
            continue
        segs = ev.get("segs")
        if not segs:                     # событие-окно без текста
            continue
        body = clean("".join(s.get("utf8", "") for s in segs))
        if not body:
            continue
        start = ev.get("tStartMs", 0) / 1000
        cues.append((start, start + ev.get("dDurationMs", 0) / 1000, body))
    return cues


# ---------- дедупликация ----------

def strip_overlap(tail, words):
    """Убрать из words префикс, совпадающий с суффиксом уже накопленного."""
    for k in range(min(len(tail), len(words)), 0, -1):
        if tail[-k:] == words[:k]:
            return words[k:]
    return words


def to_chunks(cues, window=40):
    """[(start, end, [новые слова])] — без повторов rolling window."""
    chunks, acc = [], []
    for start, end, body in cues:
        words = strip_overlap(acc[-window:], body.split())
        if not words:
            continue
        acc.extend(words)
        chunks.append((start, end, words))
    return chunks


# ---------- вывод ----------

def hhmmss(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def has_punctuation(chunks):
    total = sum(len(w) for _, _, w in chunks)
    dots = sum(1 for _, _, ws in chunks for w in ws if w[-1:] in ".!?")
    return total > 0 and dots / total > 0.01


def paragraphs(chunks, pause, max_words):
    """Резать по паузе, по длине, по концу предложения (если пунктуация есть)."""
    punct, out, cur, prev_end = has_punctuation(chunks), [], [], None
    for start, end, words in chunks:
        gap = start - prev_end if prev_end is not None else 0.0
        if cur and (gap >= pause or len(cur) >= max_words * 1.5
                    or (len(cur) >= max_words and (not punct or cur[-1][-1:] in ".!?"))):
            out.append(cur)
            cur = []
        cur.extend(words)
        prev_end = end
    if cur:
        out.append(cur)
    return out


def blocks(chunks, interval, boundaries=()):
    """[(start, [слова])] — блок не короче interval секунд, но рвется на границе главы."""
    out, cur, cur_start = [], [], None
    for start, _end, words in chunks:
        if cur_start is None:
            cur_start = start
        crossed = any(cur_start < b <= start for b in boundaries)
        if cur and (crossed or start - cur_start >= interval):
            out.append((cur_start, cur))
            cur, cur_start = [], start
        cur.extend(words)
    if cur:
        out.append((cur_start or 0.0, cur))
    return out


def load_chapters(path):
    with open(path, encoding="utf-8") as f:
        info = json.load(f)
    return [(c.get("start_time", 0), c.get("title", "")) for c in (info.get("chapters") or [])]


def chapter_at(chapters, t):
    title = None
    for start, name in chapters:
        if t >= start:
            title = name
        else:
            break
    return title


def main():
    ap = argparse.ArgumentParser(description="Субтитры YouTube -> читаемая транскрипция")
    ap.add_argument("input")
    ap.add_argument("-m", "--mode", choices=("plain", "ts"), default="plain")
    ap.add_argument("-i", "--interval", type=float, default=30.0, help="секунд на блок в режиме ts")
    ap.add_argument("-p", "--pause", type=float, default=1.5, help="пауза, дающая новый абзац")
    ap.add_argument("-w", "--width", type=int, default=0, help="перенос строк, 0 — без переноса")
    ap.add_argument("--max-words", type=int, default=110, help="предел слов в абзаце")
    ap.add_argument("--chapters", help="info.json от yt-dlp: вставить заголовки глав")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    text = open(args.input, encoding="utf-8-sig").read()
    head = text.lstrip()[:200]
    if args.input.endswith(".json3") or head.startswith("{"):
        cues = read_json3(text)
    elif "<transcript" in head or args.input.endswith(".srv1"):
        cues = read_srv1(text)
    else:
        cues = read_vtt(text)
    chunks = to_chunks(cues)
    if not chunks:
        sys.exit("пустая транскрипция: субтитры не распознаны")

    chapters = load_chapters(args.chapters) if args.chapters else []
    wrap = (lambda s: textwrap.fill(s, args.width)) if args.width else (lambda s: s)

    lines, seen_chapter = [], object()
    if args.mode == "plain":
        for par in paragraphs(chunks, args.pause, args.max_words):
            lines.append(wrap(" ".join(par)))
    else:
        for start, words in blocks(chunks, args.interval, [c[0] for c in chapters]):
            title = chapter_at(chapters, start)
            if chapters and title != seen_chapter:
                seen_chapter = title
                lines.append(f"## {title or 'без главы'}")
            lines.append(f"[{hhmmss(start)}] {wrap(' '.join(words))}")

    result = "\n\n".join(lines) + "\n"
    if args.output:
        open(args.output, "w", encoding="utf-8").write(result)
        words = sum(len(w) for _, _, w in chunks)
        print(f"{args.output}: {words} слов, {len(lines)} блоков", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
