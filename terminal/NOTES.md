# Грабли со шрифтом

- `brew list --cask font-jetbrains-mono` может показывать "установлено", а `.ttf`
  при этом не попасть ни в `~/Library/Fonts`, ни в `/Library/Fonts` — бывает,
  если Homebrew на машине принадлежит другому macOS-аккаунту. Проверять файлы
  напрямую (`ls ~/Library/Fonts`, `system_profiler SPFontsDataType | grep -i jetbrains`),
  не доверять выводу brew. Фикс — скопировать `.ttf` из Caskroom прямо в
  `/Library/Fonts` через `sudo cp`.
- Уже запущенный Terminal.app не подхватывает новый шрифт "на лету" — открыть
  новую вкладку/окно недостаточно, нужен полный `quit` и повторный запуск
  процесса.
