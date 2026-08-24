# Permissions

Система разрешений Claude Code: какие инструменты и какие аргументы разрешены/запрещены/требуют подтверждения.

## Структура

```json
"permissions": {
  "defaultMode": "auto",
  "allow": ["Bash(git status:*)", "Read(./**)"],
  "deny": ["Bash(rm -rf:*)"],
  "ask": ["Bash(git push:*)", "WebFetch(domain:*)"],
  "additionalDirectories": ["/tmp/shared"]
}
```

### defaultMode

- `default` — спрашивать при каждом чувствительном действии.
- `acceptEdits` — не спрашивать про Edit/Write.
- `plan` — запретить Edit/Write/Bash (plan mode).
- `auto` — автономный режим, меньше вопросов.
- `bypassPermissions` — отключить все запросы (dangerous).

### Приоритет

`deny` > `ask` > `allow` > defaults. Если действие попадает под `deny` — запрещено, даже если есть в `allow`.

## Паттерны

Формат: `ToolName(pattern)`.

### Bash

```
Bash(git status:*)        # git status с любыми аргументами
Bash(git status)          # только ровно "git status"
Bash(npm run test:*)      # npm run test *
Bash(docker:*)            # любая docker-команда
Bash(cd:*)                # любой cd
```

`:*` — любые аргументы/продолжение. Без `:*` — точное совпадение.

### Read / Write / Edit

```
Read(./src/**)            # читать что угодно в src/
Read(/etc/**)             # абсолютные пути
Write(~/.ssh/**)          # по `~` работает не всегда — дублируй с $HOME
Edit(**/*.env)            # .env-файлы
```

### WebFetch

```
WebFetch(domain:anthropic.com)
WebFetch(domain:*.github.com)
WebFetch(domain:*)                # любой домен
```

### MCP

```
mcp__<server>__<tool>           # конкретный MCP-инструмент
mcp__github__*                  # все инструменты сервера github
```

Например: `mcp__paper__get_basic_info`.

### Остальные tools

Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, TodoWrite, TaskCreate, Agent, Skill, NotebookEdit, Monitor, SendMessage, ScheduleWakeup, ToolSearch и т.д.

```
WebSearch                       # разрешить/запретить целиком
TodoWrite
Agent(subagent_type:Explore)
```

## additionalDirectories

Список каталогов **вне** рабочей директории, куда Claude Code может читать/писать. Полезно для мультирепо-setup'ов.

```json
"additionalDirectories": [
  "/Users/me/Projects/shared-lib",
  "/tmp"
]
```

## Выбор уровня

- **User (`~/.claude/settings.json`)** — твои личные предпочтения во всех проектах. Типичный кейс: разрешить безопасные bash-команды (`ls`, `cat`, `git status`).
- **Project (`./.claude/settings.json`)** — для команды: разрешения, специфичные для репозитория (например, скрипты `./scripts/build.sh`).
- **Local (`./.claude/settings.local.json`)** — личные разрешения внутри проекта (например, доступ к локальному БД-порту).

## Частые задачи

### «Разреши npm test»

```json
"permissions": { "allow": ["Bash(npm test:*)"] }
```

### «Разреши все git-команды кроме push»

```json
"permissions": {
  "allow": ["Bash(git:*)"],
  "ask": ["Bash(git push:*)"]
}
```

### «Запрети rm -rf»

```json
"permissions": { "deny": ["Bash(rm -rf:*)", "Bash(sudo rm:*)"] }
```

### «Разреши читать ~/.config, но не писать»

```json
"permissions": {
  "allow": ["Read(~/.config/**)"],
  "deny": ["Write(~/.config/**)", "Edit(~/.config/**)"]
}
```

### «Разреши MCP-сервер paper целиком»

```json
"permissions": { "allow": ["mcp__paper__*"] }
```

## Полезные скиллы

- `less-permission-prompts` — сканирует транскрипты и предлагает allowlist на основе реально встречавшихся команд.

## Антипаттерны

- **`Bash(*)` в project settings.** Слишком широко — оставляй это user/local.
- **Разрешение `Write(~/.ssh/**)`.** Почти всегда не то, что нужно. Секретные каталоги добавляй в `deny`.
- **Паттерн без `:*`.** `Bash(git status)` требует ТОЧНОГО совпадения без аргументов. В 95% случаев нужен `Bash(git status:*)`.
