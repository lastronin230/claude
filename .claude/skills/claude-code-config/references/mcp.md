# MCP-серверы

Model Context Protocol — серверы, дающие Claude Code дополнительные инструменты (доступ к браузеру, дизайн-тулу, базе данных, Jira, и т.д.).

## Уровни конфигурации

- **User-уровень** — `~/.claude.json` (управляется через `claude mcp add -s user …`). Сервер доступен во всех проектах.
- **Project-уровень** — `./.mcp.json` (коммитится в репозиторий). Настройка общая для команды.
- **Local-уровень** — `./.claude/settings.local.json` (через `enabledMcpjsonServers` и т.п.). Не коммитится.

## CLI: `claude mcp`

```bash
claude mcp list                              # список всех серверов
claude mcp get <name>                        # детали сервера
claude mcp add <name> -- <command> [args]    # добавить (по умолчанию project)
claude mcp add <name> -s user -- <cmd>       # добавить на user-уровень
claude mcp add <name> -s local -- <cmd>      # локально в проекте
claude mcp remove <name>                     # удалить
claude mcp add-json <name> '<json>'          # добавить из JSON
```

## Формат `.mcp.json`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./mcp-server.js"],
      "env": {
        "API_KEY": "..."
      }
    },
    "remote-server": {
      "type": "sse",
      "url": "https://example.com/mcp",
      "headers": {
        "Authorization": "Bearer ..."
      }
    }
  }
}
```

### Поля сервера

- `command` — путь к бинарнику (для stdio-серверов).
- `args` — аргументы команды.
- `env` — переменные окружения для процесса сервера.
- `type` — `stdio` (по умолчанию), `sse`, `http`.
- `url` — URL (для sse/http).
- `headers` — HTTP-заголовки.

## Настройка доверия к project MCP

`.mcp.json` коммитится в репозиторий, поэтому CC по умолчанию спрашивает подтверждение перед запуском его серверов. Управление через `settings.json`:

```json
{
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": ["paper", "mobile"],
  "disabledMcpjsonServers": ["something-untrusted"]
}
```

## Использование инструментов MCP

Инструменты сервера доступны под именами `mcp__<server>__<tool>`. Примеры: `mcp__paper__get_basic_info`, `mcp__mobile__device_list`.

В permissions:

```json
{
  "permissions": {
    "allow": ["mcp__paper__*", "mcp__mobile__ui_tree"]
  }
}
```

## Инструкции MCP-серверов

Некоторые серверы предоставляют свои инструкции — они автоматически появляются в system prompt сессии. Например, сервер `paper` требует сначала вызвать `get_guide({topic: "paper-mcp-instructions"})`. Эти инструкции — часть контракта сервера, не трогай их.

## Популярные MCP-серверы

- `context7` — актуальная документация библиотек (плагин `context7@claude-plugins-official`).
- `paper` — дизайн-тул для UI (локальный).
- `mobile` — автоматизация мобилы/десктопа/браузера + store management.
- `claude_ai_Gmail` / `claude_ai_Google_Drive` / `claude_ai_Google_Calendar` — Google-сервисы.

## Отладка

- `claude mcp list` — покажет статус (running / error).
- Логи MCP-сервера — обычно в stderr процесса, CC показывает их при ошибке.
- Если сервер не отвечает — проверь, что `command` существует в PATH.
- Если tool не вызывается — проверь permissions: `mcp__<server>__<tool>` должен быть разрешён.

## Антипаттерны

- **Секреты в project `.mcp.json`.** Файл коммитится. Токены и API-ключи клади в user-уровень (`~/.claude.json`) или через `env` с подстановкой из системных переменных.
- **Дублирующиеся имена серверов.** Одно имя = один сервер в данной сессии.
- **MCP-сервер, запускающийся с root-правами.** Никогда не нужно.
- **MCP-сервер на неподтверждённом коде.** CC предупредит, но сам по себе запуск небезопасного сервера — риск exec-уязвимости.
