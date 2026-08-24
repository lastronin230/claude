# Плагины

Плагины упаковывают вместе skills, slash-команды, subagents, hooks, MCP-серверы и output styles. Дистрибутируются через маркетплейсы.

## Включение/выключение

`~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "skill-creator@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "some-other@plugin-marketplace": false
  }
}
```

Формат имени: `<plugin-name>@<marketplace-name>`.

## CLI

```bash
claude plugin list                           # все установленные
claude plugin install <name>@<marketplace>   # установить
claude plugin enable <name>@<marketplace>    # включить
claude plugin disable <name>@<marketplace>   # выключить
claude plugin remove <name>@<marketplace>    # удалить
```

## Маркетплейсы

Маркетплейс — источник плагинов. Официальный: `claude-plugins-official`. Можно подключать сторонние.

```bash
claude marketplace list
claude marketplace add <name> <url-or-path>
claude marketplace remove <name>
```

Структура маркетплейса — обычно git-репозиторий с `plugins/<name>/` папками.

## Что обычно ставят

- `skill-creator@claude-plugins-official` — создание/улучшение skills.
- `context7@claude-plugins-official` — актуальная документация библиотек через MCP.
- `claude-code-setup@claude-plugins-official` — анализ кодбезы и рекомендации по настройке.
- `claude-md-management@claude-plugins-official` — управление CLAUDE.md.
- `hookify@claude-plugins-official` — помощник по hook'ам.
- `commit-commands@claude-plugins-official` — команды для коммитов.
- `code-review@claude-plugins-official` — ревью кода.
- LSP-плагины (`typescript-lsp`, `pyright-lsp`, `kotlin-lsp`, и т.д.) — интеграция с Language Server Protocol.

## Структура плагина

```
<plugin-name>/
  .claude-plugin/
    plugin.json          # name, version, description, author
  skills/<name>/         # skills
    SKILL.md
  commands/<name>.md     # slash-команды
  agents/<name>.md       # subagents
  hooks/                 # hook-обработчики
  output-styles/<name>.md
```

## Локальный плагин для разработки

Плагин можно разрабатывать локально и ссылаться на него как на directory marketplace:

```bash
claude marketplace add my-local ~/my-plugins
claude plugin install my-plugin@my-local
```

## Антипаттерны

- **Установка всего подряд.** Каждый плагин добавляет skills в available-list и тратит контекст на их описания. Ставь только то, что реально нужно.
- **Конфликтующие плагины.** Если два плагина дают skill с одинаковым именем — один переопределит другой. Проверяй.
- **Правка файлов плагина напрямую.** Они в кэше `~/.claude/plugins/cache/…` — при обновлении переписываются. Форкни плагин или делай свой.
