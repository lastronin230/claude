# settings.json — полная схема

Файл настроек Claude Code. Существует на трёх уровнях:

- `~/.claude/settings.json` — user, глобальный
- `./.claude/settings.json` — project, коммитится
- `./.claude/settings.local.json` — project, НЕ коммитится (секреты, личные правки)

Нижестоящий уровень переопределяет вышестоящий: local > project > user > defaults.

## Корневые ключи

```json
{
  "permissions": { },
  "env": { },
  "hooks": { },
  "statusLine": { },
  "model": "claude-opus-4-7",
  "effortLevel": "xhigh",
  "language": "Russian",
  "theme": "dark",
  "autoMemoryEnabled": false,
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30,
  "enabledPlugins": { },
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": [],
  "disabledMcpjsonServers": [],
  "apiKeyHelper": "/path/to/script",
  "forceLoginMethod": "claudeai",
  "skipDangerousModePermissionPrompt": true,
  "skipAutoPermissionPrompt": true
}
```

### permissions

См. `permissions.md`. Кратко:

```json
"permissions": {
  "defaultMode": "auto",
  "allow": ["Bash(git status:*)", "Read(~/.config/**)"],
  "deny": ["Bash(rm -rf:*)", "Write(~/.ssh/**)"],
  "ask": ["Bash(git push:*)"],
  "additionalDirectories": ["/extra/path"]
}
```

`defaultMode`: `default` | `acceptEdits` | `plan` | `auto` | `bypassPermissions` (последний — dangerous).

### env

Переменные окружения, видимые Claude Code и всем порождаемым процессам.

```json
"env": {
  "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
  "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "20",
  "MY_API_TOKEN": "..."
}
```

Значения — всегда строки. Для секретов используй `settings.local.json`.

### hooks

См. `hooks.md`.

### statusLine

```json
"statusLine": {
  "type": "command",
  "command": "bash ~/.claude/statusline.sh",
  "padding": 0
}
```

Скрипт получает JSON на stdin (model, cwd, transcript_path, session_id и т.д.) и должен вывести одну строку в stdout. Обновляется не чаще раза в 300 мс.

Пример минимального `statusline.sh`:

```bash
#!/bin/bash
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name')
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
echo "$model | ${cwd/#$HOME/~}"
```

### model

ID модели, которую CC использует по умолчанию. Точные ID — в system prompt текущей сессии. Популярные: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`. Можно также `opus` / `sonnet` / `haiku` как короткий алиас.

### effortLevel

Уровень размышлений: `low` | `medium` | `high` | `xhigh`. Чем выше — тем больше thinking tokens.

### language

Язык ответов. `Russian`, `English`, и т.д. Эквивалент правила «Always respond in <lang>» в system prompt.

### theme

`dark` | `light` | `dark-daltonized` | `light-daltonized` | `dark-ansi` | `light-ansi`.

### autoMemoryEnabled

`true` — CC автоматически дописывает в CLAUDE.md. `false` — только явные правки.

### includeCoAuthoredBy

Добавлять `Co-Authored-By: Claude …` к коммитам. По умолчанию `true`.

### cleanupPeriodDays

Сколько дней хранить историю чатов и временные файлы.

### enabledPlugins

См. `plugins.md`.

```json
"enabledPlugins": {
  "skill-creator@claude-plugins-official": true,
  "context7@claude-plugins-official": true
}
```

### MCP-флаги

- `enableAllProjectMcpServers` — разрешить все серверы из `.mcp.json` без подтверждения.
- `enabledMcpjsonServers` / `disabledMcpjsonServers` — точечное включение/выключение. См. `mcp.md`.

### apiKeyHelper

Путь к скрипту, возвращающему API-ключ. Полезно для корпоративных setup'ов с ротацией ключей.

### forceLoginMethod

`claudeai` | `console` — принудительный способ логина.

### skipDangerousModePermissionPrompt / skipAutoPermissionPrompt

Отключают подтверждения при включении dangerous / auto режимов. Ставь только если понимаешь риск.

## Типичные ошибки

- **Комментарии в JSON** — невалидно, CC молча не применит файл. Проверяй через `python -m json.tool`.
- **Trailing comma** — невалидно.
- **Неверные имена ключей** — CC игнорирует неизвестные ключи без предупреждения. Сверяйся с этим reference.
- **`env` числа/bool без кавычек** — все значения должны быть строками.
- **Путь с `~` в permissions/hooks** — обычно не раскрывается, используй `$HOME` или абсолютный путь.
