# AGENTS.md

Інструкції для майбутніх agents, які працюють у цьому repository.

## Контекст repository

Це mdBook repository HackTricks Cloud. Пов’язана основна book розташована за адресою:

`/Users/carlospolop/git/hacktricks`

Зміни до спільної поведінки theme/search часто потрібно застосовувати в обох repositories.

## Контракт завантаження search index

Користувацький search UI розташований у:

`theme/ht_searcher.js`

Також може існувати згенерована копія:

`book/theme/ht_searcher.js`

Якщо production розгортає вже зібрану директорію `book/`, оновіть обидві копії або перебудуйте
book перед deployment.

Порядок завантаження search index є важливим і чутливим до витрат:

1. Завантажуйте кожен language-specific і fallback search index із GitHub repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Лише якщо всі розміщені на GitHub candidates не завантажилися, використовуйте fallback з mdBook output того самого origin.

Не розміщуйте локальний `/searchindex.js` fallback перед будь-яким GitHub-hosted fallback, наприклад
`searchindex-cloud-en.js.gz`. Розміщення `searchindex.js` з `cloud.hacktricks.wiki` у production є дорогим.

Для цього repo очікуваний локальний fallback:

`/searchindex.js`

Fallback основної book для цього repo:

`/searchindex-book.js`

Цей файл є лише fallback. Основним source мають залишатися віддалені файли
`searchindex-<lang>.js.gz` і `searchindex-cloud-<lang>.js.gz` у
`HackTricks-wiki/hacktricks-searchindex`.

## Публікація search index

Workflows, які публікують зашифровані стиснені search indexes у
`HackTricks-wiki/hacktricks-searchindex`:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Згенерований source file: `book/searchindex.js`. Назви опублікованих remote artifacts:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader надає перевагу compact v2 artifact і зберігає artifact `.js.gz` як legacy
fallback. Обидва є XOR-encrypted gzip payloads і використовують key, визначений у `theme/ht_searcher.js`.

## Build і validation

Поширені локальні checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Якщо `mdbook build` завершується з помилкою, перевірте:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Нотатки щодо редагування

- Для пошуку надавайте перевагу `rg`.
- Не додавайте згенерований output `book/` до commits, якщо це прямо не запитано. Виправлення search loader
є винятком, коли вже зібрані pages потрібно негайно виправити.
- Якщо змінюєте поведінку спільної theme, порівняйте та оновіть відповідний file у
`/Users/carlospolop/git/hacktricks`.
- Не скасовуйте сторонні локальні зміни.
