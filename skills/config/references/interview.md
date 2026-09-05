# The config interview — six questions, three calls, 21 of 25 keys

> **Reference-only.** Read by [`../SKILL.md`](../SKILL.md) steps 3 and 5. Every question here is
> phrased per [`../../_shared/ask-style.md`](../../_shared/ask-style.md): Ukrainian, action-form
> labels, every technical term glossed inline, the trade-off spelled out in the description.
> Hosts without a native `AskUserQuestion` ask the same questions as **numbered plain text, one at
> a time, stop and wait** — same shape, same glosses, nothing skipped.

## Three standing rules

- **On a repeat run the current value is the first option, marked «(Recommended)»** — so re-running
  `/sdd:config` shows what the project is set to today and changes nothing by accident.
- **Group by decision, not by key.** A person tunes «how strict are the gates», not `gate_vet`.
  One answer therefore writes several keys, and the `old → new` output names each one.
- **When the current state matches no option exactly** — the normal case after a host clamp, or
  after someone hand-edited one key of a bundle — do **not** force it into the nearest option.
  Prepend a «Лишити як є» option that spells out the actual current values of that group,
  mark it «(Recommended)», and say in the question text which key is the odd one out. Silently
  re-bundling a hand-edited value back into a preset is the way this skill loses a user's edit.

## Question → keys map

| # | Call | Question (the decision) | Keys it writes |
|---|---|---|---|
| 0 | opening | Stay on defaults, or tune? | none — the fork |
| 1 | 1 | Which tool is this session running in? | none directly; **clamps** `team_mode` · `workflow_mode` · `max_parallel_agents` on a non-Claude host |
| 2 | 1 | Which model tier should the agents run at? | `judgment_model` · `model_test_author` · `model_implementer` · `model_reviewer` · `effort_test_author` · `effort_implementer` · `effort_reviewer` |
| 3 | 2 | How strict should the tests and gates be? | `tdd` · `stop_on_red` · `max_red_retries` · `gate_lint` · `gate_vet` · `require_integration` |
| 4 | 2 | How should tasks execute and commit? | `team_mode` · `workflow_mode` · `max_parallel_agents` · `isolation` · `auto_commit` · `branch_strategy` |
| 5 | 3 | How deeply should the pipeline interview you? | `interview_depth` |
| 6 | 3 | Which language are the documents written in? | `artifact_language` |

**21 keys.** The remaining four — `cmd_test_unit`, `cmd_test_integration`, `cmd_lint`, `cmd_vet` —
are **never asked**. Empty means the command-detection cascade reads the repo's own Makefile,
package scripts and language manifests, which is a better answer than a command pinned once and
left to rot. They stay in the derived list of the step-6 output, named as «left empty for
autodetect».

---

## Q0 — the fork (step 3, before anything is asked)

> **CONTEXT.** `.claude/sdd.local.md` is already on disk with documented defaults, so the pipeline
> works right now — medium-depth interviews, English documents, TDD on, opus-tier judgment agents,
> a commit per task. The question is only whether we walk through the settings together and change
> some of them. **WHY IT MATTERS.** Nothing here is irreversible: every key can be changed later by
> running `/sdd:config` again, and each one carries its meaning inline in the file itself, so you
> can also just open it in an editor. The cost of tuning now is about six questions.
> **READ OPTIONS.**

- **«Лишити дефолти» (Recommended)** — Нічого не міняю. Файл `.claude/sdd.local.md` уже лежить у репозиторії з задокументованими значеннями, і кожен ключ у ньому має коментар із поясненням. Пайплайн одразу робочий: питання середньої глибини, документи англійською, TDD увімкнений, коміт після кожної задачі. Повернутись і покрутити можна будь-коли тим самим `/sdd:config`.
- **«Пройти шість питань»** — Ставлю шість згрупованих питань і після кожної твоєї відповіді патчу відповідні ключі, показуючи `було → стало`. Групи: підтвердження інструмента, рівень моделей, суворість тестів і воріт, режим виконання і комітів, глибина опитувань, мова документів. Твої коментарі й невідомі ключі у файлі лишаються недоторканими. Займає кілька хвилин.

---

## Call 1 — the ground the rest stands on

### Q1 — host confirmation

> **CONTEXT.** Два налаштування пайплайна працюють лише в Claude Code: `team_mode` (команда агентів
> через `TeamCreate`) і `workflow_mode` (динамічний `Workflow`, який паралелить незалежні задачі).
> У Codex CLI і Cursor цих механізмів немає, тому движок там завжди йде послідовно одним агентом.
> **WHY IT MATTERS.** Якщо записати їх увімкненими на хості, де їх немає, налаштування виглядатиме
> робочим, а поводитиметься інакше — і зрозуміє це людина аж на `implement`. Тому підтверджуємо
> інструмент явно. Ось що я побачив: `<перелічити сигнали з detection.md і на що вони вказують; при
> суперечливих слідах — назвати суперечність прямо>`. **READ OPTIONS.**

- **«Claude Code»** — Лишаю питання про режим виконання (Q4) повноцінним: доступні і команда агентів, і Workflow, і паралельність більша за 1. Нічого не затискаю.
- **«Codex CLI»** — Затискаю `team_mode: false`, `workflow_mode: off`, `max_parallel_agents: 1` і кажу про це окремим рядком у списку «виведено, а не запитано». Це не втрата: послідовний TDD одним агентом — документована база, до якої й так деградують обидва режими. Решта питань лишається без змін.
- **«Cursor»** — Те саме, що для Codex: ті самі три ключі затиснуті з тієї самої причини, решта питань без змін.

### Q2 — model tier

> **CONTEXT.** Пайплайн запускає два різні типи агентів. Виконавці (`test-author`, `implementer`)
> пишуть тести й код. Судді (`reviewer`, `critic`, `devils-advocate`, `strategist`, `analyst`)
> оцінюють: шукають дірки в специфікації, рецензують дифи, атакують ідею. Один ключ `judgment_model`
> задає рівень моделі одразу всім пʼятьом суддям, а `model_<роль>` — окремо кожному виконавцю.
> **WHY IT MATTERS.** Питаю прямо, бо сесія принципово не бачить списку моделей, доступних твоєму
> акаунту: підбір наосліп дав би налаштування, яке падає при першому ж диспатчі. Якщо обрана модель
> усе-таки недоступна, диспатч один раз повторюється на `inherit` (модель поточної сесії) і не
> блокує стадію. **READ OPTIONS.**

- **«Судді на opus, виконавці на sonnet» (Recommended)** — Дефолт: `judgment_model: opus`, `model_test_author` і `model_implementer` на `sonnet`, `model_reviewer` на `opus`. Логіка проста: судження окупає сильнішу модель, механічне написання тесту — ні. Зусилля (`effort_*`) лишаються `medium` для виконавців і `high` для рецензента, а на великих фічах (L/XL) движок сам піднімає виконавців до `high`. Дефолт `opus` тут це підлога, а не пін: якщо сесія працює на сильнішому рівні, судді підуть на `inherit` замість тихого зниження.
- **«Усе на sonnet»** — `judgment_model: sonnet` плюс усі три `model_*` на `sonnet`. Це підтримуваний шлях для акаунтів без доступу до Opus: пайплайн проходить повністю, рецензії стають трохи поверховішими. Дешевше й швидше. Якщо в тебе немає Opus, обирай саме це, а не дефолт, бо тоді ти бачиш реальний рівень одразу, а не через деградацію.
- **«Успадкувати модель сесії»** — `judgment_model` і всі три `model_*` стають `inherit`: кожен агент іде на тій моделі, на якій працює сесія. Ключі `effort_*` при цьому **не змінюються**: `inherit` не входить у їхній набір значень (`low | medium | high | xhigh | max` або число), тож вони лишаються як були — це буде названо в списку «виведено, а не запитано». Найпростіший варіант, коли не хочеш думати про рівні взагалі, і найпередбачуваніший за вартістю. Мінус: судді втрачають окремий важіль, тобто рецензія вже не може бути сильнішою за решту роботи.
- **«Судді на fable»** — `judgment_model: fable` піднімає всіх пʼятьох суддів на рівень Fable, виконавці лишаються на `sonnet`. Має сенс, коли болить саме якість рецензій і критики специфікацій. Потребує доступу до цього рівня в акаунта, інакше диспатч один раз відкотиться на `inherit`.

---

## Call 2 — how the work is actually done

### Q3 — strictness and gates

> **CONTEXT.** Після кожної задачі движок проганяє ворота: юніт-тести, інтеграційні (якщо
> відповідає Docker-демон), lint (перевірка стилю) і vet (статичний аналіз, який ловить підозрілі
> конструкції без запуску коду). Плюс сам цикл TDD: спершу червоний тест, потім мінімальний код,
> щоб він позеленів. **WHY IT MATTERS.** Суворіші ворота ловлять більше, але кожен зайвий тир
> додає часу на задачу і може блокувати роботу в репозиторії, де lint ще не налаштований. Ворота,
> для яких команда не знайшлася, пропускаються самі, без падіння. **READ OPTIONS.**

- **«Повні ворота, зупинка на червоному» (Recommended)** — `tdd: true`, `stop_on_red: true`, `max_red_retries: 3`, `gate_lint: true`, `gate_vet: true`, `require_integration: auto`. Тест пишеться першим; якщо після трьох спроб він лишається червоним, прогін зупиняється і ти бачиш проблему одразу. Інтеграційні тести запускаються, коли Docker відповідає, і мовчки пропускаються, коли ні. Це дефолт, і в більшості репозиторіїв його нема сенсу міняти.
- **«Не зупинятись на червоному»** — Те саме, але `stop_on_red: false`. Задача, яка лишилась червоною, відкидається, її залежні автоматично блокуються, а решта гілок DAG продовжує їхати. Корисно на довгому нічному прогоні, де краще зробити 8 задач із 10, ніж стати на другій. Мінус: у кінці треба уважно читати звіт, бо частина роботи не зроблена.
- **«Легкі ворота»** — `gate_lint: false`, `gate_vet: false`, `require_integration: never`, решта як у дефолті. Лишаються тільки юніт-тести. Має сенс у репозиторії, де lint і статичний аналіз ще не заведені, і кожен прогін інакше сипав би шумом. Ціна очевидна: стиль і статичні помилки ловитиме вже рецензія, а не ворота.
- **«Без TDD»** — `tdd: false`: движок пише код одразу, без червоного тесту попереду. Швидше, але ти втрачаєш сітку безпеки — саме червоний тест доводить, що тест справді перевіряє те, що треба, а не проходить випадково. Я щоразу попереджатиму про це в банері. Обирай, тільки якщо тести в цьому репозиторії пишуться інакше.

### Q4 — execution and commits

> **CONTEXT.** `implement` бере `tasks.json`, будує граф залежностей і виконує задачі. Він може йти
> послідовно одним агентом, командою агентів (`team_mode`) або динамічним Workflow, який паралелить
> незалежні гілки. Паралельні агенти працюють кожен у своєму git worktree — це окрема робоча копія
> репозиторію, щоб двоє не правили ті самі файли. **WHY IT MATTERS.** Паралельність економить час
> на широкому графі й нічого не дає на вузькому, зате завжди ускладнює читання логу. Гранулярність
> комітів вирішує, наскільки дрібно ти зможеш відкотити роботу потім.
> `<на не-Claude хості: два перші варіанти недоступні — кажу про це прямо і роблю «Строго
> послідовно, один потік» першим варіантом із поміткою «(Recommended)», бо це і є фактичний стан
> після клампу>` **READ OPTIONS.**

- **«Хай движок вирішує сам, коміт на задачу» (Recommended)** — `team_mode: false`, `workflow_mode: auto`, `max_parallel_agents: 3`, `isolation: worktree`, `auto_commit: per_task`, `branch_strategy: feature`. Це дефолт, і назва тут буквальна: режим обирається за формою графа. Вузький ланцюжок задач піде послідовно, а от **широкий незалежний граф піде Workflow і справді підніме до трьох агентів одночасно**, кожного у своєму worktree під `.worktrees/`. Якщо хочеш гарантовано один потік, це наступний варіант, а не цей. Кожна задача закривається окремим комітом із трейлерами `SDD-Task` і `SDD-AC`, робота йде на окремій feature-гілці.
- **«Команда агентів»** — `team_mode: true`: `test-author` → `implementer` → `reviewer` над графом, координація через спільний список задач, по одному worktree на агента. Найшвидший режим на великій фічі з багатьма незалежними задачами. Мінус: лог стає складнішим для читання, а на вузькому графі виграшу немає взагалі. Працює лише в Claude Code.
- **«Строго послідовно, один потік»** — `team_mode: false`, `workflow_mode: off`, `max_parallel_agents: 1`, `isolation: inplace`: одна робоча копія, жодних worktree, задачі одна за одною, без винятків. Найпростіше для читання і налагодження, повільніше на широкому графі. Це також те, у що затискається не-Claude хост, тому на Codex і Cursor цей варіант описує реальну поведінку, а не вибір. Обирай, коли хочеш бачити рівно один потік роботи.
- **«Коміти лишити мені»** — `auto_commit: off` плюс дефолти решти: движок пише код і ганяє ворота, але не комітить нічого. Ти сам вирішуєш, що і як закомітити в кінці. Мінус: пропадають трейлери `SDD-Task` / `SDD-AC`, за якими потім будується трасування «критерій приймання → коміт».

---

## Call 3 — the two keys people change most often

### Q5 — interview depth

> **CONTEXT.** Дилер глибини вирішує, скільки питань ставлять `specify`, `clarify` і `design`, і
> скільки вони вирішують самі. На `easy` скіл бере розумні дефолти й записує їх у відомість
> припущень, яку ти ветуєш одним рухом; на `hard` він проходить кожне рішення й щоразу показує
> компроміс. **WHY IT MATTERS.** Це найпомітніше налаштування в щоденній роботі, і воно нічого не
> прибирає з покриття: усі критерії приймання лишаються обовʼязковими на кожному рівні, міняється
> тільки кількість питань. Значення тут — це дефолт, який щоразу можна перебити на місці аргументом
> `--depth=`. **READ OPTIONS.**

- **«Середня» (Recommended)** — `interview_depth: medium`. Скіл проходить кожне справжнє рішення, але не розжовує очевидне: типово 3-5 питань на етап. Ідеологічні розвилки питає, конвенційні дефолти бере сам і називає їх. Це баланс, з яким працює більшість.
- **«Легка»** — `interview_depth: easy`. Питаю тільки те, чого не можна вивести з контексту; решту вирішую сам і складаю у відомість припущень, яку ти переглядаєш одним блоком у кінці. Найшвидший прохід. Ризик очевидний: припущення, яке ти не помітив у списку, поїде далі в специфікацію.
- **«Глибока»** — `interview_depth: hard`. Проходжу кожне рішення, щоразу виношу компроміс на поверхню, на `specify` запускаю повний набір ідеаційних агентів (дослідник ринку, стратег, аналітик, адвокат диявола). Найповніший результат і найдовший діалог. Має сенс на фічі, ціна помилки в якій висока.

### Q6 — document language

> **CONTEXT.** `artifact_language` задає мову, якою пишеться **проза** документів пайплайна:
> специфікації, архітектурного документа, ADR, моделі даних, задач, тест-плану, рецензій,
> чейнджлогу. Структура при цьому завжди лишається англійською — заголовки секцій, ключі
> frontmatter, вердикти, стани трекера, ключові слова Mermaid, машинні поля `tasks.json` і
> `openapi.yaml`. **WHY IT MATTERS.** Це вибір для людей, які читатимуть ці документи, а не для
> інструментів. Правило перебивання просте: мова наявного файла завжди виграє над налаштуванням, а
> новий файл підлаштовується під сусідів у своїй теці фічі — уже написане ніколи не перекладається
> заднім числом. **READ OPTIONS.**

- **«Англійська» (Recommended)** — `artifact_language: en`. Уся проза англійською. Дефолт, і правильний вибір, якщо документи читатиме хтось поза українськомовною командою або якщо репозиторій уже англомовний.
- **«Українська»** — `artifact_language: uk`. Проза українською: абзаци, комірки таблиць, підписи на діаграмах, текстові поля `tasks.json`. Заголовки секцій, машинні токени й ключі лишаються англійськими, тому все, що читають скіли й валідатори, працює без змін. Обирай, коли специфікації читає українськомовна команда.
- **«Інша мова»** — Ключ приймає будь-який мовний тег, не тільки `en` і `uk`. Скажи, який саме, і я запишу його. Правила ті самі: перемикається проза, структура лишається англійською.
