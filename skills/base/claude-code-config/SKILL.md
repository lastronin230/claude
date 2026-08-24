---
name: claude-code-config
description: Единая точка настройки Claude Code. Используй всегда, когда пользователь хочет изменить любое поведение Claude Code — permissions (разрешения Bash/Read/Write/WebFetch/MCP), hooks (PreToolUse/PostToolUse/UserPromptSubmit/Stop/SubagentStop/SessionStart/SessionEnd/Notification/PreCompact), переменные окружения, model/effortLevel, statusLine, тему, язык, автопамять, keybindings, slash-команды, subagents, output styles, skills, MCP-серверы, плагины, CLAUDE.md (память), импорты @file. Триггерится на фразы вроде «настрой Claude Code», «разреши команду», «запрети», «автоматически когда Х», «каждый раз Х», «добавь хук», «добавь команду /foo», «создай subagent», «подключи MCP», «поменяй модель», «переназначь клавишу», «отредактируй CLAUDE.md», «добавь правило», «добавь skill», «поменяй statusline», даже если пользователь не называет конкретный файл. Это единственный способ настраивать Claude Code — не редактируй settings.json, hooks, skills, agents, commands, keybindings, CLAUDE.md и MCP-конфиги в обход этого skill.
---

# Claude Code Config

Скилл покрывает все поверхности настройки Claude Code и описывает, какой файл править для какой задачи. Claude Code настраивается **только через этот skill** — при любом запросе на изменение поведения CC сначала определи целевую поверхность по таблице ниже, затем открой нужный reference для схемы и примеров.

## Принципы

1. **Не догадывайся — проверяй текущее состояние.** Перед любой правкой читай существующий конфиг (`~/.claude/settings.json`, `./.claude/settings.json`, `./.claude/settings.local.json` и т.д.), чтобы не сломать уже настроенное и понять стиль пользователя.
2. **Выбирай правильный уровень.** User-уровень (`~/.claude/…`) — личные предпочтения, применяются везде. Project-уровень (`./.claude/…`) — коммитится в репозиторий, распространяется на команду. Local-уровень (`./.claude/settings.local.json`) — личные настройки внутри проекта, не коммитятся. Родительские `.claude/` подхватываются автоматически при работе в подкаталоге.
3. **Правило «автоматически когда X» = hook, не память.** Если пользователь просит «каждый раз Х», «после Х», «перед Х», «автоматически», «всегда» — это hook в `settings.json`, а не правило в CLAUDE.md. Правило в памяти описывает предпочтения стиля; hook исполняется детерминированно харнессом.
4. **Разрешения — узкие.** Вместо `Bash(*)` давай конкретный паттерн: `Bash(git status:*)`, `Bash(npm test:*)`. Широкие разрешения оставляй пользователю, если он явно попросил.
5. **Не ломай совместимость незаметно.** Не удаляй чужие хуки/permissions/env при правке — делай точечные изменения.
6. **Формат — JSON с 2-пробельными отступами.** settings.json, keybindings.json, .mcp.json — валидный JSON без комментариев.

## Таблица маршрутизации

| Что хочет пользователь | Поверхность | Файл | Reference |
|---|---|---|---|
| Разрешить/запретить инструмент или команду | permissions | `settings.json` (любой уровень) | `references/permissions.md` |
| Изменить режим разрешений (auto/acceptEdits/plan/default) | permissions.defaultMode | `settings.json` | `references/settings.md` |
| Исполнять что-то автоматически на событие | hooks | `settings.json` (любой уровень) | `references/hooks.md` |
| Переменную окружения | env | `settings.json` | `references/settings.md` |
| Модель / уровень усилий / тему / язык / автопамять | корневые поля | `settings.json` | `references/settings.md` |
| Статусную строку | statusLine | `settings.json` + shell-скрипт | `references/settings.md` |
| Включить/выключить плагин | enabledPlugins | `~/.claude/settings.json` | `references/plugins.md` |
| Создать/изменить slash-команду | command | `.claude/commands/<name>.md` | `references/slash-commands.md` |
| Создать/изменить subagent | agent | `.claude/agents/<name>.md` | `references/subagents.md` |
| Создать/изменить output style | output style | `.claude/output-styles/<name>.md` | `references/output-styles.md` |
| Создать/изменить skill | skill | `.claude/skills/<name>/SKILL.md` (+ references/, scripts/, assets/) | see `skill-creator` skill |
| Подключить MCP-сервер | mcp | `.mcp.json` (project) или `~/.claude.json` (user, через `claude mcp add`) | `references/mcp.md` |
| Горячие клавиши | keybindings | `~/.claude/keybindings.json` | `references/keybindings.md` |
| Память / правила стиля / глоссарий | memory | `CLAUDE.md` (user/project/вложенные) | `references/memory.md` |
| Импорт файла в CLAUDE.md | import | `@path` в CLAUDE.md | `references/memory.md` |

## Единая процедура правки

1. **Определи поверхность** по таблице выше. Если запрос на грани двух (например, «запрети git push» = permissions, «после каждого коммита запускай линтер» = hook) — обоснуй выбор одной фразой.
2. **Определи уровень.** Если пользователь не сказал — спроси или выбери по умолчанию: личные предпочтения → user, общекомандные → project, секреты/токены → local.
3. **Открой соответствующий reference** из `references/`. Там схема, примеры и подводные камни.
4. **Прочитай текущий файл** (если существует) через Read.
5. **Внеси точечное изменение** через Edit, сохраняя чужие ключи. Если файла нет — создавай через Write с минимально необходимым JSON.
6. **Проверь валидность JSON** для json-конфигов (`python -m json.tool <file>` или `jq . <file>`).
7. **Сообщи пользователю, что изменилось и где.** Напомни, если нужно перезапустить сессию (некоторые изменения, например statusLine, подхватываются сразу; permissions/hooks — со следующего запуска tool-use).

## Расположение конфигов

```
~/.claude/
  settings.json              # user-уровень, применяется везде
  keybindings.json           # горячие клавиши (только user)
  CLAUDE.md                  # глобальная память
  commands/<name>.md         # глобальные slash-команды
  agents/<name>.md           # глобальные subagents
  output-styles/<name>.md    # глобальные output styles
  skills/<name>/SKILL.md     # глобальные skills
  statusline.sh              # скрипт statusline (если используется)

<project>/.claude/
  settings.json              # project-уровень, коммитится
  settings.local.json        # личные правки внутри проекта, НЕ коммитятся
  commands/<name>.md         # команды проекта
  agents/<name>.md           # subagents проекта
  output-styles/<name>.md    # output styles проекта
  skills/<name>/SKILL.md     # skills проекта

<project>/
  CLAUDE.md                  # память проекта (коммитится)
  .mcp.json                  # MCP-серверы проекта (коммитится)
```

Вложенные `CLAUDE.md` (например, `docs/tasks/CLAUDE.md`) автоматически подгружаются при работе с файлами внутри соответствующего каталога.

Приоритет settings (от высшего к низшему): enterprise → CLI args → `./.claude/settings.local.json` → `./.claude/settings.json` → `~/.claude/settings.json` → defaults. Вышестоящий уровень переопределяет нижестоящий.

## Чтение текущего состояния

Перед любой правкой полезно понять, что уже настроено:

- `cat ~/.claude/settings.json` — user-настройки
- `cat ./.claude/settings.json` — project-настройки (если есть)
- `cat ./.claude/settings.local.json` — локальные настройки (если есть)
- `ls ~/.claude/commands/ ./.claude/commands/` — слэш-команды
- `ls ~/.claude/agents/ ./.claude/agents/` — subagents
- `ls ~/.claude/skills/ ./.claude/skills/` — skills
- `cat .mcp.json` — MCP-серверы проекта
- `cat CLAUDE.md ~/.claude/CLAUDE.md` — память

## Частые задачи (быстрые шаблоны)

### Разрешить конкретную bash-команду (user-уровень)

```json
{
  "permissions": {
    "allow": ["Bash(npm test:*)"]
  }
}
```

Подробности и паттерны — `references/permissions.md`.

### Хук «после каждого редактирования файла форматируй»

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "prettier --write \"$CLAUDE_TOOL_INPUT_file_path\""}]
      }
    ]
  }
}
```

Подробности — `references/hooks.md`.

### Slash-команда `/review`

Файл `.claude/commands/review.md`:

```markdown
---
description: Ревью текущей ветки
argument-hint: "[base-branch]"
allowed-tools: Bash(git:*), Read, Grep
---

Сделай ревью изменений на этой ветке относительно $1 (по умолчанию main).
```

Подробности — `references/slash-commands.md`.

### Subagent `code-reviewer`

Файл `.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Независимое ревью кода. Используй когда нужен второй взгляд на изменения.
tools: Read, Grep, Glob, Bash
---

Ты опытный ревьюер. Анализируй код на корректность, безопасность, производительность…
```

Подробности — `references/subagents.md`.

### MCP-сервер

```bash
claude mcp add <name> -- <command> [args...]
```

или руками в `.mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {"command": "node", "args": ["./mcp-server.js"]}
  }
}
```

Подробности — `references/mcp.md`.

### Память (правило стиля)

Добавь раздел в `CLAUDE.md`:

```markdown
## Редакция
В пользовательских текстах используем «е» вместо «ё».
```

Для разделения на файлы — используй импорты `@.claude/rules/<name>.md`. Подробности — `references/memory.md`.

## Антипаттерны

- **Правило «каждый раз X» записано в CLAUDE.md.** Память не исполняет — её читает только модель. Нужен hook.
- **Разрешение `Bash(*)` в project settings.** Слишком широко для коммита в репозиторий — используй конкретные паттерны.
- **Секреты в `.claude/settings.json` (project).** Этот файл коммитится. Токены и приватные env клади в `settings.local.json`.
- **Hook без matcher на PreToolUse/PostToolUse.** Без matcher сработает на любой tool — почти всегда не то, что хотел пользователь.
- **CLAUDE.md > 500 строк.** Раздели на файлы через `@import` и вложенные `.claude/CLAUDE.md`.
- **Slash-команда, которая дублирует skill.** Если логика с триггером «на контексте» — это skill. Если по явному вызову `/name` — команда.
- **Разные MCP-серверы с одинаковым name.** Уникальность имени обязательна.

## Куда дальше

- Подробная схема `settings.json` — `references/settings.md`
- Система разрешений — `references/permissions.md`
- Все hook-события, matcher'ы, переменные окружения — `references/hooks.md`
- Slash-команды (frontmatter, аргументы, `$1..$9`, allowed-tools) — `references/slash-commands.md`
- Subagents (frontmatter, isolation, модель) — `references/subagents.md`
- Output styles — `references/output-styles.md`
- MCP-серверы — `references/mcp.md`
- Keybindings (формат, чорды, список команд) — `references/keybindings.md`
- Память, импорты, вложенные CLAUDE.md — `references/memory.md`
- Плагины (enabledPlugins, маркетплейсы) — `references/plugins.md`
