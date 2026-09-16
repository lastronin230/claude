# Статьи: тема → ресерч → сборка

Как из темы получается готовая html-статья: что делается на каждом шаге и из каких
готовых деталей верстается текст.

## Флоу

1. **Вход** — тема статьи от пользователя.
2. **Ресерч** — глубокий. В первую очередь официальная документация, дальше — код,
   эксперименты, другие источники. Не пересказ по памяти.
3. **Сборка** — статья делится на части. У части только заголовок, без подписи под ним
   (`.part`). Внутри части — сплошной текст (`.prose`), и в него по ходу вставляется
   только то, что уже зафиксировано ниже.
4. **Ограничение** — новых стилей по ходу написания не изобретать. Не хватает
   инструмента для куска материала — остановиться и осознанно дополнить набор в этом
   файле, и только потом продолжать статью.

## Как излагать теорию

Пример — не отдельный блок в конце части, а продолжение абзаца, который он
иллюстрирует. Объяснил мысль — сразу показал код или пример использования на ней же, и
только после этого переходишь к следующей мысли. Теория и код чередуются внутри одного
потока, а не разбиты на «сначала все объяснения, потом все примеры».

## Планка простоты

Зафиксированный набор — не декорация по минимуму, а инструмент, которым стоит
пользоваться почаще: там, где абзац станет понятнее с выделением, `.callout` или
`.code-card`, — использовать их, а не оставлять сплошным текстом. Единственное
ограничение — техническое качество не должно падать: читаемость улучшается не за счет
упрощений или потерянных деталей.

## Зафиксированный набор

| Класс | Назначение |
|---|---|
| `.part` | заголовок части: номерной значок слева, без подписи под заголовком |
| `.prose` | сплошной текст части, свои абзацы внутри |
| `.term` | подводка/термин в начале мысли — жирный, без цвета |
| `.mark` | фраза-суть — желтая заливка-чип, громче всего |
| `.quiet` | второстепенное — тише базовой линии, взгляд пропускает |
| `.code-card` | код, команда — карточка с шапкой под имя файла/язык |
| `.tok-kw` / `.tok-fn` / `.tok-com` | подсветка внутри кода: ключевые слова / вызовы функций / комментарии |
| `.callout` + `.pos` / `.neg` / `.neu` | выноска-акцент: плюс / минус / нейтральная заметка |
| `.table-card` | табличные данные — карточка с залитой шапкой |

### `.part` — заголовок части

```html
<div class="part">
  <span class="k">5</span>
  <h2>getLocationAvailability — «датчики сейчас вообще работают?»</h2>
</div>
```

### `.prose` + пул выделений

```html
<div class="prose">
  <p><span class="term">Что это.</span> Устройство не всегда способно понять, где оно
    находится: <span class="quiet">геолокация выключена в настройках, включен режим
    полета, человек в подземном паркинге без спутников</span>. Метод отвечает ровно на
    это — <span class="mark">есть ли у системы прямо сейчас рабочие источники
    локации</span>.</p>
</div>
```

### `.code-card` — код, команда

```html
<div class="code-card">
  <div class="bar">LocationRepository.kt</div>
  <pre><code><span class="tok-com">// опрос вместо подписки на updates</span>
<span class="tok-kw">fun</span> <span class="tok-fn">onAppResumed</span>() {
    scope.<span class="tok-fn">launch</span> { ... }
}</code></pre>
</div>
```

### `.callout` — выноска-акцент

```html
<div class="callout pos"><span class="tag">Плюс</span><p>Кеш на 5 минут — меньше повторных сетевых вызовов.</p></div>
<div class="callout neg"><span class="tag">Минус</span><p>Без таймаута опроса батарея садится быстрее обычного.</p></div>
<div class="callout neu"><span class="tag">Заметка</span><p>Интервал хранится в миллисекундах, не в секундах.</p></div>
```

### `.table-card` — таблица

```html
<div class="table-card"><table>
  <thead><tr><th>Метод</th><th>Точность</th></tr></thead>
  <tbody>
    <tr><td>GPS</td><td>Высокая</td></tr>
  </tbody>
</table></div>
```

## CSS зафиксированного набора

Копируется целиком в `<style>` страницы. Правки вносятся здесь, а не на лету в
конкретной статье — так изменение достается сразу всем текстам.

```css
:root{
  --bg:#FBF8EE; --panel:#FFFFFF; --ink:#3C3836; --muted:#6F675E; --line:#EBE3D2;
  --code:#F5F0E2;
  --red:#9E3626;    --red-bg:#F8E9E3;
  --green:#276E36;  --green-bg:#E9F2E5;
  --yellow:#7E5A11; --yellow-bg:#F7EED8;
  --blue:#1B537D;   --blue-bg:#E4EDF4;
  --magenta:#7E3790;--magenta-bg:#F1E7F3;
  --cyan:#12656E;   --cyan-bg:#E3F0EF;
  --mono:"JetBrains Mono","SF Mono",ui-monospace,monospace;
  /* Шкала размеров шрифта - 5 шагов на весь шаблон, новых значений не заводить */
  --fs-micro:11.5px;  /* моно-подписи капсом: бар кода, тег выноски, шапка таблицы */
  --fs-sm:13.5px;     /* второстепенный/код: тело code-card, номер в .part */
  --fs-base:16px;     /* базовый текст: абзацы, подзаголовок, why, таблица, лейбл секции */
  --fs-md:17px;       /* h3, подзаголовок внутри текста */
  --fs-lg:20px;       /* h2 части (.part) */
  --fs-xl:24px;       /* h1 */
}

.tok-kw{color:var(--blue);font-weight:600}
.tok-fn{color:var(--cyan)}
.tok-com{color:var(--muted);font-style:italic}

/* Код, команда: карточка с шапкой (имя файла/язык), рамка со всех сторон */
.code-card{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--panel)}
.code-card .bar{padding:8px 14px;border-bottom:1px solid var(--line);font-family:var(--mono);
  font-size:var(--fs-micro);color:var(--muted);letter-spacing:.04em}
.code-card pre{margin:0;padding:14px;background:var(--code);font-family:var(--mono);font-size:var(--fs-sm);
  line-height:1.6;overflow-x:auto}

/* Выноски: карточка - рамка + полоса слева + метка сверху */
.callout{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--muted);
  border-radius:0 8px 8px 0;padding:12px 16px;margin:0 0 10px;max-width:68ch}
.callout .tag{font-family:var(--mono);font-size:var(--fs-micro);letter-spacing:.06em;text-transform:uppercase;
  display:block;margin-bottom:4px}
.callout p{margin:0}
.callout.pos{border-left-color:var(--green)} .callout.pos .tag{color:var(--green)}
.callout.neg{border-left-color:var(--red)}   .callout.neg .tag{color:var(--red)}
.callout.neu{border-left-color:var(--blue)}  .callout.neu .tag{color:var(--blue)}

/* Таблица: карточка - рамка со всех сторон, шапка залита */
.table-card{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.table-card table{border-collapse:collapse;width:100%;font-size:var(--fs-base)}
.table-card th{text-align:left;font-weight:600;font-size:var(--fs-micro);text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);padding:10px 14px;background:var(--code);border-bottom:1px solid var(--line)}
.table-card td{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.table-card tbody tr:last-child td{border-bottom:none}

.prose{max-width:68ch}
.prose p{margin:0 0 16px}

/* Часть статьи: номерной значок слева от заголовка, без панели */
.part{margin:48px 0 18px;display:flex;align-items:center;gap:14px}
.part .k{flex:none;width:36px;height:36px;border-radius:50%;background:var(--cyan-bg);
  color:var(--cyan);font-family:var(--mono);font-size:var(--fs-sm);font-weight:600;
  display:flex;align-items:center;justify-content:center}
.part h2{margin:0;font-size:var(--fs-lg);font-weight:600;color:var(--ink)}

/* Пул выделений: одна теплая нота (--yellow, как в имени темы Warm Light) громче базовой
   линии, плюс заметно более тихая ступень ниже нее - контраст между ними, а не несколько
   разных техник враскидку. */
.quiet{color:var(--muted);opacity:.5}                               /* заметно тише - второстепенное */
.term{font-weight:600}                                              /* структурная подводка, без цвета */
.mark{background:var(--yellow-bg);color:var(--yellow);padding:1px 5px;border-radius:4px} /* фраза-суть, громче всего */
```
