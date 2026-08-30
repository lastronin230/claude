# Terminal.app

## Warm Light.terminal

Профиль macOS Terminal.app.

| Параметр | Значение |
|---|---|
| Шрифт | JetBrains Mono Regular, 14 pt |
| Размер окна | 120 x 30 |
| Antialias | вкл |

Шрифт в профиль не входит — на новой машине поставить отдельно:

```sh
brew install --cask font-jetbrains-mono
```

Без него Terminal молча подставит системный моноширинный.

## Установка

```sh
open "terminal/Warm Light.terminal"
```

Terminal откроет новое окно с этим профилем и добавит его в Settings -> Profiles.
Дальше — выбрать профиль в списке и нажать **Default**, чтобы он применялся к новым окнам.

Либо без GUI:

```sh
defaults write com.apple.Terminal "Default Window Settings" -string "Warm Light"
defaults write com.apple.Terminal "Startup Window Settings" -string "Warm Light"
```

## Обновить снимок профиля

После правки настроек в GUI:

```sh
defaults export com.apple.Terminal /tmp/term.plist
/usr/libexec/PlistBuddy -x -c "Print :'Window Settings':'Warm Light'" /tmp/term.plist \
  > "terminal/Warm Light.terminal"
```
