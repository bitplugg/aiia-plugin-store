# AIIA Plugin Store

Магазин локальных плагинов для [AIIA](https://github.com/bitplugg/ail0l):
готовые `.aiip`-пакеты и `.dex`-файлы для hot reload.

[![plugins](https://img.shields.io/badge/plugins-20-10A37F)](catalog/catalog.json)
[![aiip](https://img.shields.io/badge/aiip-10-blueviolet)](releases/aiip)
[![dex](https://img.shields.io/badge/dex-10-orange)](releases/dex)
[![AIIA](https://img.shields.io/badge/AIIA-compatible-10A37F)](https://github.com/bitplugg/ail0l)

Репозиторий содержит **10 `.aiip` плагинов** и **10 `.dex` плагинов**.
Все инструменты работают локально и не требуют отдельного сервера.

> Устанавливайте только плагины, которым доверяете. `.dex` загружается в
> процесс приложения через `DexClassLoader` и не является отдельной security
> sandbox.

## Каталог

### `.aiip`-пакеты

| Плагин | Инструмент | Описание | Файл |
| --- | --- | --- | --- |
| Text Upper | `uppercase` | Перевод текста в верхний регистр | [text-upper.aiip](releases/aiip/text-upper.aiip) |
| Text Lower | `lowercase` | Перевод текста в нижний регистр | [text-lower.aiip](releases/aiip/text-lower.aiip) |
| Text Reverse | `reverse` | Разворот строки | [text-reverse.aiip](releases/aiip/text-reverse.aiip) |
| Word Count | `word_count` | Подсчёт слов | [word-count.aiip](releases/aiip/word-count.aiip) |
| JSON Summary | `json_summary` | Локальная сводка JSON-текста | [json-summary.aiip](releases/aiip/json-summary.aiip) |
| Base64 Codec | `base64_encode` | Кодирование UTF-8 в Base64 | [base64-codec.aiip](releases/aiip/base64-codec.aiip) |
| Hash Tool | `sha256` | Локальный SHA-256 | [hash-tool.aiip](releases/aiip/hash-tool.aiip) |
| URL Summary | `url_summary` | Схема, host, path и query URL | [url-summary.aiip](releases/aiip/url-summary.aiip) |
| Date Time | `datetime` | Unix milliseconds → UTC ISO-8601 | [datetime-tool.aiip](releases/aiip/datetime-tool.aiip) |
| Color Tool | `color_hex` | HEX → RGB | [color-tool.aiip](releases/aiip/color-tool.aiip) |

### `.dex` hot reload

| Плагин | Инструмент | Описание | Файл |
| --- | --- | --- | --- |
| Length Converter | `length` | Метры, километры, мили, футы | [length-converter.dex](releases/dex/length-converter.dex) |
| Weight Converter | `weight` | Килограммы, граммы, фунты | [weight-converter.dex](releases/dex/weight-converter.dex) |
| Temperature Converter | `temperature` | Celsius ↔ Fahrenheit | [temperature-converter.dex](releases/dex/temperature-converter.dex) |
| Number Stats | `number_stats` | Count, min, max, average | [number-stats.dex](releases/dex/number-stats.dex) |
| Password Generator | `password_generate` | Локальная генерация пароля | [password-generator.dex](releases/dex/password-generator.dex) |
| Slugify | `slugify` | Создание URL-safe slug | [slugify.dex](releases/dex/slugify.dex) |
| Markdown Cleaner | `markdown_clean` | Удаление простого Markdown-разметки | [markdown-cleaner.dex](releases/dex/markdown-cleaner.dex) |
| Random Choice | `random_choice` | Выбор из pipe-separated вариантов | [random-choice.dex](releases/dex/random-choice.dex) |
| Contact Mask | `contact_mask` | Маскирование email/phone-подобного значения | [contact-mask.dex](releases/dex/contact-mask.dex) |
| Text Profile | `text_profile` | Статистика букв, цифр и пробелов | [text-profile.dex](releases/dex/text-profile.dex) |

## Установка в AIIA

### `.aiip`

1. Откройте настройки плагинов в AIIA.
2. Выберите нужный файл из `releases/aiip`.
3. Проверьте `manifest.json` и permissions.
4. Подтвердите установку.

Каждый пакет содержит:

```text
plugin.aiip
├── manifest.json
├── plugin.dex
└── assets/
```

### `.dex`

1. Скопируйте `.dex` и его `.manifest.json` в `AIIA/plugins` на внешнем
   хранилище.
2. Перезапустите hot reload или приложение.
3. Подтвердите manifest в UI.

Имя sidecar-манифеста должно совпадать с именем DEX-файла:

```text
length-converter.dex
length-converter.manifest.json
```

Каталог также публикует `manifestSha256` для каждого `.dex`. AIIA скачивает
sidecar вместе с DEX и проверяет оба хеша до загрузки в sandbox.

## Аргументы инструментов

Большинство инструментов принимает JSON-объект `arguments`:

```json
{"text": "Привет, AIIA"}
```

Для конвертеров используются поля `value` и `unit`:

```json
{"value": 12.5, "unit": "km"}
```

Для генератора пароля:

```json
{"length": 20}
```

Если обязательное поле пустое, инструмент возвращает понятную строку с
ошибкой и не вызывает внешнюю сеть.

## Разработка

Исходники каждого плагина находятся в `src/aiip` и `src/dex`.
Общий runtime — `tools/common/src/aiia/plugin/common/PluginSupport.java`.

Требования:

- JDK 17;
- Python 3.10+;
- Android SDK Platform 35;
- Android Build Tools 35.0.0;
- доступ к локальному Gradle-кэшу Kotlin и kotlinx-serialization.

Пересобрать все артефакты:

```bash
python3 tools/generate_sources.py
python3 tools/build_artifacts.py
python3 scripts/validate_store.py
```

Сборка создаёт:

```text
releases/aiip/*.aiip       # 10 пакетов
releases/dex/*.dex         # 10 DEX-файлов
releases/dex/*.manifest.json
catalog/catalog.json
catalog/aiip.json
catalog/dex.json
```

`build_artifacts.py` использует D8 и включает `PluginSupport` в каждый
артефакт. API-классы приложения не помещаются в plugin DEX: они должны
загружаться родительским `DexClassLoader` из AIIA.

## Автоматизация

### Сборка и публикация

`.github/workflows/plugins.yml`:

- собирает все 20 артефактов на push и pull request;
- проверяет количество `.aiip`/`.dex`, manifest и DEX-сигнатуры;
- загружает собранные файлы как GitHub Actions artifact;
- на `main` автоматически коммитит изменения, если генератор изменил
  артефакты или каталог.

### PR Agent

`.github/workflows/pr-agent.yml` публикует безопасный чек-лист в pull request
и сообщает, какие проверки запущены. Он не получает секреты и не выполняет
код pull request с правами записи.

### GitHub Pages

`.github/workflows/pages.yml` публикует `index.html` и каталог как статический
storefront после push в `main`.

## Каталог для других клиентов

Машиночитаемые списки:

- [catalog/catalog.json](catalog/catalog.json)
- [catalog/aiip.json](catalog/aiip.json)
- [catalog/dex.json](catalog/dex.json)

Формат записи:

```json
{
  "id": "store.aiia.aiip.text-upper",
  "format": "aiip",
  "name": "Text Upper",
  "tool": "uppercase",
  "artifact": "releases/aiip/text-upper.aiip"
}
```

## Лицензия

Примеры и исходники магазина распространяются по AGPL-3.0, как и основной
проект AIIA. Upstream llama.cpp и его native binding сохраняют собственные
лицензии и атрибуцию.

## Ссылки

- [Основной AIIA](https://github.com/bitplugg/ail0l)
- [AIIA SDK/template](https://github.com/bitplugg/aiia-aiip-template)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Hugging Face](https://huggingface.co/)
