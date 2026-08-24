# Hooks

Hooks — shell-команды, которые CC запускает автоматически на определённых событиях. Используй hooks, когда пользователь просит «автоматически когда X», «каждый раз X», «перед/после X», «всегда делай Y при Z».

## Структура

```json
"hooks": {
  "<EventName>": [
    {
      "matcher": "<tool-name-regex>",
      "hooks": [
        {
          "type": "command",
          "command": "<shell-command>",
          "timeout": 30
        }
      ]
    }
  ]
}
```

`matcher` — регулярное выражение по имени tool (для `PreToolUse`/`PostToolUse`). Для событий без tool (Stop, UserPromptSubmit и т.д.) `matcher` можно опустить.

## События

| Событие | Когда срабатывает | Может блокировать? |
|---|---|---|
| `PreToolUse` | Перед выполнением tool | Да (exit 2 или `{"decision": "block"}`) |
| `PostToolUse` | После tool | Нет (но может инжектить сообщение) |
| `UserPromptSubmit` | Когда пользователь отправил сообщение | Да |
| `Stop` | Когда Claude закончил ответ | Да (может заставить продолжить) |
| `SubagentStop` | Когда subagent закончил | Да |
| `Notification` | При уведомлении (idle/permission) | Нет |
| `PreCompact` | Перед компакцией контекста | Нет |
| `SessionStart` | Старт сессии | Нет |
| `SessionEnd` | Конец сессии | Нет |

## Переменные окружения в hook

Хук получает через stdin JSON с полным контекстом события. Также доступны:

- `CLAUDE_PROJECT_DIR` — корень проекта (для project-уровня)
- `CLAUDE_TOOL_INPUT_<param>` — поля входа tool (для PreToolUse/PostToolUse)
- `CLAUDE_TOOL_OUTPUT` — результат tool (для PostToolUse)

Пример stdin для `PostToolUse(Edit)`:

```json
{
  "session_id": "...",
  "transcript_path": "...",
  "cwd": "/path/to/project",
  "hook_event_name": "PostToolUse",
  "tool_name": "Edit",
  "tool_input": {"file_path": "/path/to/file.ts", "old_string": "...", "new_string": "..."},
  "tool_response": {"success": true}
}
```

Читай stdin через `jq` или `python -c "import json,sys; d=json.load(sys.stdin); ..."`.

## Коды возврата и JSON-ответы

- **exit 0** — успех, продолжай.
- **exit 1** — ошибка, показать пользователю (не блокирует).
- **exit 2** — блокировать действие (для PreToolUse/UserPromptSubmit/Stop). stderr покажется как причина.

Расширенный формат — вернуть JSON в stdout:

```json
{
  "decision": "block",
  "reason": "файл слишком большой"
}
```

или

```json
{
  "decision": "approve"
}
```

## Примеры

### Форматировать после каждого Edit/Write

```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "f=\"$CLAUDE_TOOL_INPUT_file_path\"; case \"$f\" in *.ts|*.tsx|*.js|*.jsx) npx prettier --write \"$f\" 2>/dev/null ;; *.py) ruff format \"$f\" 2>/dev/null ;; esac"
      }]
    }
  ]
}
```

### Блокировать `git push --force` в main

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE 'git push.*(--force|-f)'; then branch=$(git symbolic-ref --short HEAD); if [ \"$branch\" = \"main\" ] || [ \"$branch\" = \"master\" ]; then echo 'force push в main запрещён' >&2; exit 2; fi; fi"
      }]
    }
  ]
}
```

### Уведомление когда Claude закончил

```json
"hooks": {
  "Stop": [
    {
      "hooks": [{
        "type": "command",
        "command": "osascript -e 'display notification \"Claude закончил\" with title \"Claude Code\"'"
      }]
    }
  ]
}
```

### Инжектить контекст при старте сессии

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [{
        "type": "command",
        "command": "echo 'Текущая ветка: '$(git branch --show-current 2>/dev/null)"
      }]
    }
  ]
}
```

Stdout из SessionStart попадает в контекст сессии.

### Запрет редактировать .env

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "f=$(jq -r '.tool_input.file_path'); if echo \"$f\" | grep -qE '\\.env($|\\.)'; then echo '.env файлы трогать нельзя' >&2; exit 2; fi"
      }]
    }
  ]
}
```

## Выбор уровня

- **User** — личные привычки (уведомление при Stop, форматирование своим любимым форматтером).
- **Project** — командные инварианты (запрет force-push, обязательный линтер перед коммитом).
- **Local** — личные правки внутри проекта.

## Выбор между hook и правилом в CLAUDE.md

- **Hook** — когда нужно ГАРАНТИРОВАННОЕ выполнение. Исполняется харнессом, не зависит от модели.
- **CLAUDE.md** — когда это предпочтение стиля или знание о проекте. Модель может нарушить (редко, но может).

Правило-триггер: если фраза содержит «автоматически», «каждый раз», «всегда», «перед», «после», «гарантированно» — это hook.

## Skill для hooks

В системе есть skill `hookify` (плагин) — помогает генерировать hook'и. Также `update-config` умеет править `settings.json`.

## Антипаттерны

- **Hook без matcher на PreToolUse/PostToolUse.** Сработает на любой tool. Всегда указывай matcher.
- **Hook с огромным timeout.** По умолчанию 60 сек, увеличивай только если действительно надо.
- **Hook, пишущий в tool_input.** PreToolUse может влиять на tool только через exit code / JSON decision, не может модифицировать input.
- **Hook с интерактивным промптом.** Хук работает не-интерактивно, `read` повиснет.
- **Зависимость от PWD.** Всегда используй `$CLAUDE_PROJECT_DIR` или абсолютные пути, не предполагай рабочий каталог.
