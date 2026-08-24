# Keybindings

Горячие клавиши Claude Code. Настраиваются ТОЛЬКО на user-уровне через `~/.claude/keybindings.json`.

## Формат

```json
{
  "bindings": [
    {
      "key": "ctrl+s",
      "command": "submit",
      "when": "input.focused"
    },
    {
      "key": "ctrl+k ctrl+b",
      "command": "toggle.sidebar"
    }
  ]
}
```

### Поля

- `key` — клавиша или чорд. Чорд — последовательность через пробел: `ctrl+k ctrl+s`.
- `command` — имя команды CC.
- `when` — опциональное условие контекста (`input.focused`, `sidebar.visible` и т.п.).

### Модификаторы

- `ctrl+`, `shift+`, `alt+`, `cmd+` (meta на mac).
- Комбинации через `+`: `ctrl+shift+p`.
- Специальные клавиши: `enter`, `tab`, `escape`, `backspace`, `space`, `up`, `down`, `left`, `right`, `f1`..`f12`.

## Основные команды CC

| Команда | Что делает |
|---|---|
| `submit` | Отправить сообщение |
| `newline` | Перенос строки в инпуте |
| `abort` | Прервать текущий ответ |
| `clear` | Очистить экран / сессию |
| `history.prev` / `history.next` | История промптов |
| `toggle.planMode` | Включить/выключить plan mode |
| `toggle.autoMode` | Включить/выключить auto mode |
| `approve.all` | Одобрить все запросы на подтверждение |
| `deny` | Отклонить запрос |
| `fast` | Переключить fast mode |
| `compact` | Принудительная компакция контекста |

Полный список — в документации CC или через `/help`.

## Примеры

### Отправка на `ctrl+enter` вместо `enter`

```json
{
  "bindings": [
    {"key": "enter", "command": "newline", "when": "input.focused"},
    {"key": "ctrl+enter", "command": "submit", "when": "input.focused"}
  ]
}
```

### Быстрое переключение plan/auto

```json
{
  "bindings": [
    {"key": "ctrl+k p", "command": "toggle.planMode"},
    {"key": "ctrl+k a", "command": "toggle.autoMode"}
  ]
}
```

### Shift+Enter для переноса строки

На некоторых терминалах Shift+Enter не работает из коробки. В iTerm2/WezTerm/Ghostty нужно настроить escape-последовательность. Для CC:

```json
{
  "bindings": [
    {"key": "shift+enter", "command": "newline", "when": "input.focused"}
  ]
}
```

Терминал должен отправлять `\x1b\r` или `\x1b\n` на Shift+Enter — настраивается в preferences терминала.

## Skill для keybindings

В системе есть skill `keybindings-help` — помогает с ребиндом клавиш. Используй его, если пользователь явно говорит «настрой горячие клавиши».

## Антипаттерны

- **Keybindings в project settings.** Не поддерживается — только user-уровень.
- **Ребинд базовых клавиш без `when`.** `enter` без `when: input.focused` может перехватить Enter в других контекстах.
- **Конфликт с чордом.** Если забиндил `ctrl+k` на команду и `ctrl+k ctrl+s` на другую — короткая сработает первой.
