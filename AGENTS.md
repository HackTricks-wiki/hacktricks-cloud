# AGENTS.md

Інструкції для майбутніх агентів, які працюють у цьому репозиторії.

## Контекст репозиторію

Це mdBook-репозиторій HackTricks Cloud. Пов’язана основна книга розташована за адресою:

`/Users/carlospolop/git/hacktricks`

Зміни до спільної поведінки theme/search часто потрібно застосовувати в обох репозиторіях.

## Контракт завантаження пошукового індексу

Користувацький інтерфейс пошуку розташований у:

`theme/ht_searcher.js`

Також може існувати згенерована копія за адресою:

`book/theme/ht_searcher.js`

Якщо production розгортає вже зібраний каталог `book/`, оновіть обидві копії або перебудуйте
книгу перед розгортанням.

Порядок завантаження пошукового індексу є важливим і чутливим до витрат:

1. Завантажуйте кожен мовний і резервний пошуковий індекс із GitHub repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Лише якщо всі кандидати, розміщені на GitHub, не працюють, використовуйте резервний варіант із
того самого джерела mdBook.

Не розміщуйте локальний `/searchindex.js` fallback перед будь-яким fallback, розміщеним на GitHub,
наприклад `searchindex-cloud-en.js.gz`. Обслуговування `searchindex.js` із `cloud.hacktricks.wiki`
у production є дорогим.

Для цього репозиторію очікуваним локальним fallback є:

`/searchindex.js`

Fallback основної книги для цього репозиторію:

`/searchindex-book.js`

Цей файл є лише fallback. Основним джерелом мають залишатися віддалені файли
`searchindex-<lang>.js.gz` і `searchindex-cloud-<lang>.js.gz` у
`HackTricks-wiki/hacktricks-searchindex`.

## Публікація пошукового індексу

Workflow, які публікують зашифровані стиснені пошукові індекси до
`HackTricks-wiki/hacktricks-searchindex`:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Згенерований вихідний файл: `book/searchindex.js`. Назви опублікованих віддалених артефактів:

- `searchindex-cloud-v2-en.json.gz` (бажаний компактний індекс)
- `searchindex-cloud-v2-<lang>.json.gz` (бажаний компактний індекс)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader надає перевагу компактному артефакту v2 і зберігає артефакт `.js.gz` як legacy
fallback. Обидва є XOR-зашифрованими gzip payload із використанням ключа, визначеного в
`theme/ht_searcher.js`.

Loader має залишатися lazy: звичайна навігація сторінками не повинна створювати search worker або
завантажувати індекс, доки відвідувач не відкриє або не використає пошук. Віддалені стиснені
відповіді зберігаються в Cache Storage протягом 24 годин для кожного origin, щоб наступні сторінки
могли повторно їх використовувати. Зберігайте fallback для застарілого кешу, якщо оновлення
простроченого запису не вдається.

## Збірка та перевірка

Поширені локальні перевірки:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Якщо `mdbook build` завершується помилкою, перевірте:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Примітки щодо редагування

- Для пошуку надавайте перевагу `rg`.
- Не додавайте згенерований вміст `book/` до commit, якщо це прямо не запитано. Виправлення search
  loader є винятком, якщо вже зібрані сторінки потрібно негайно виправити.
- Якщо змінюєте поведінку спільної theme, порівняйте та оновіть відповідний файл у
`/Users/carlospolop/git/hacktricks`.
- Не скасовуйте сторонні локальні зміни.
