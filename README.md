<div align="center">

# RoscomVPN Routing для Anywhere

Готовые и автоматически обновляемые правила маршрутизации для  
[Anywhere](https://github.com/Anywhere-Network/Anywhere)

[![CI](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/ci.yml/badge.svg)](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/ci.yml)
[![Update](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/update-configs.yml/badge.svg)](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/update-configs.yml)
[![Pages](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/pages.yml/badge.svg)](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/pages.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-101310.svg)](LICENSE)

**[Открыть страницу быстрой установки](https://mikovskii.github.io/roscomvpn-anywhere/)**

[Установка](#установка) · [Профили](#выбор-профиля) ·
[Обновление](#обновление-правил) · [Вопросы](#частые-вопросы)

</div>

---

## Возможности

- российские и белорусские ресурсы работают напрямую;
- заблокированные и выбранные зарубежные сервисы направляются через VPN;
- рекламные, телеметрические и другие нежелательные домены блокируются;
- правила обновляются из проектов RoscomVPN GeoIP и GeoSite;
- поддерживаются домены, IPv4 и IPv6;
- конфигурации проверяются перед каждой автоматической публикацией.

Текущие версии источников, количество правил и SHA256 каждого файла доступны
в [`stats.json`](stats.json).

## Выбор профиля

| Профиль | Кому подходит | Маршрутизация |
| --- | --- | --- |
| **DEFAULT** | Рекомендуется большинству пользователей | RU/BY и доверенные сервисы напрямую, выбранные сервисы через VPN, нежелательные домены блокируются |
| **WHITELIST** | Нужен строгий белый список | Только ресурсы из белого списка напрямую, всё остальное через маршрут по умолчанию |

> [!IMPORTANT]
> Не устанавливайте DEFAULT и WHITELIST одновременно. Выберите один профиль.

## Установка

### 1. Откройте добавление подписки

В приложении Anywhere перейдите:

**Settings → Routing Rules → Subscribe**

### 2. Добавьте ссылки выбранного профиля

Скопируйте адрес нужной ссылки, вставьте его в поле
**Anywhere Routing Rule Set URL** и нажмите **Subscribe**.

Каждая ссылка добавляется отдельно. После добавления откройте набор и
назначьте действие, указанное в таблице.

> [!TIP]
> Используйте **Subscribe**, а не импорт локального файла. Подписку можно
> обновлять без повторного добавления.

### DEFAULT

Для установки полного профиля добавьте все семь подписок:

| Набор | Назначить действие | Ссылка |
| --- | --- | --- |
| DIRECT Domains | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT_DOMAINS.arrs) |
| DIRECT IP 1 | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT_IP_1.arrs) |
| DIRECT IP 2 | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT_IP_2.arrs) |
| DIRECT IP 3 | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT_IP_3.arrs) |
| DIRECT IP 4 | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT_IP_4.arrs) |
| PROXY | ваш прокси или цепочка | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/PROXY.arrs) |
| REJECT | **REJECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/REJECT.arrs) |

Проверьте назначения после установки:

```text
DIRECT Domains  → DIRECT
DIRECT IP 1     → DIRECT
DIRECT IP 2     → DIRECT
DIRECT IP 3     → DIRECT
DIRECT IP 4     → DIRECT
PROXY           → ваш VPN-прокси или цепочка
REJECT          → REJECT
```

### WHITELIST

Для установки профиля белого списка добавьте две подписки:

| Набор | Назначить действие | Ссылка |
| --- | --- | --- |
| DIRECT | **DIRECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/WHITELIST/DIRECT.arrs) |
| REJECT | **REJECT** | [Открыть RAW](https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/WHITELIST/REJECT.arrs) |

В качестве маршрута по умолчанию в Anywhere выберите нужный VPN-прокси или
цепочку.

## Обновление правил

Откройте нужный набор в разделе **Routing Rules** и нажмите **Update**.
Anywhere повторно загрузит актуальный `.arrs` по сохранённой GitHub Raw ссылке.

Назначенное набору действие при обновлении сохраняется.

Готовые ZIP-архивы профилей и файл `SHA256SUMS` также публикуются в разделе
[GitHub Releases](https://github.com/mikovskii/roscomvpn-anywhere/releases).

## Частые вопросы

### Почему профиль DEFAULT состоит из семи ссылок?

Anywhere назначает одно действие всему набору правил. Поэтому DIRECT, PROXY и
REJECT должны храниться отдельно.

Кроме того, Anywhere разрешает не более 10 000 правил в одном пользовательском
наборе. Список DIRECT превышает этот лимит и разделён на домены и четыре части
IP-диапазонов.

### Можно ли установить весь профиль одной ссылкой?

Нет. Текущая версия Anywhere не поддерживает пакетный манифест, вложенные
`RULE-SET` или действие внутри `.arrs`. Одна ссылка создаёт один набор с одним
назначаемым действием.

### Почему нельзя объединить DIRECT, PROXY и REJECT?

Формат `.arrs` содержит только имя набора и правила совпадения. Действие
выбирается отдельно в интерфейсе Anywhere и применяется сразу ко всему набору.

### Будут ли правила обновляться автоматически в приложении?

Репозиторий обновляет файлы автоматически. В текущей версии Anywhere
обновление подписанного набора запускается кнопкой **Update**.

## Источники и обновления

Правила генерируются из:

- [RoscomVPN GeoIP](https://github.com/hydraponique/roscomvpn-geoip)
- [RoscomVPN GeoSite](https://github.com/hydraponique/roscomvpn-geosite)

Точные версии источников записаны в [`sources.json`](sources.json).

GitHub Actions каждые шесть часов проверяет новые 12-значные теги обоих
проектов. При обнаружении обновления workflow:

1. загружает новые версии источников;
2. генерирует `.arrs`;
3. проверяет формат, CIDR, дубликаты, лимиты и приоритеты;
4. обновляет `sources.json`;
5. публикует изменения от имени `github-actions[bot]`.

Каждая успешная сборка с изменениями также создаёт GitHub Release с отдельными
архивами DEFAULT и WHITELIST.

## Для разработчиков

### Ручная генерация

```sh
python3 scripts/generate_anywhere.py \
  --geosite /path/to/roscomvpn-geosite \
  --geoip /path/to/roscomvpn-geoip

python3 scripts/validate_anywhere.py
```

Генератор поддерживает доменные суффиксы, ключевые слова, IPv4 CIDR и IPv6
CIDR. Записи GeoSite `full:` преобразуются в суффиксы, поскольку Anywhere не
имеет типа для точного совпадения домена.

Для сохранения порядка Xray `block-proxy-direct` низкоприоритетные правила,
полностью покрытые более приоритетным суффиксом, ключевым словом или CIDR,
удаляются при генерации.

### Запуск workflow

Workflow [update-configs.yml](.github/workflows/update-configs.yml) запускается:

- автоматически каждые шесть часов;
- вручную через `workflow_dispatch`;
- событием `repository_dispatch` типа `update-anywhere-configs`.

## Благодарности

Этот проект основан на правилах и идеях оригинального
[RoscomVPN Routing](https://github.com/hydraponique/roscomvpn-routing).

Спасибо авторам и участникам проектов:

- [RoscomVPN Routing](https://github.com/hydraponique/roscomvpn-routing) —
  оригинальные профили маршрутизации для Happ, INCY и Mihomo;
- [RoscomVPN GeoIP](https://github.com/hydraponique/roscomvpn-geoip) —
  актуальные списки IP-диапазонов;
- [RoscomVPN GeoSite](https://github.com/hydraponique/roscomvpn-geosite) —
  актуальные списки доменов;
- [Anywhere](https://github.com/Anywhere-Network/Anywhere) — приложение и
  формат правил `.arrs`.

Все права на оригинальные проекты принадлежат их авторам.

## Лицензия

Собственные скрипты, workflow, сайт и документация распространяются по
[MIT License](LICENSE).

Сгенерированные файлы в `ANYWHERE/` содержат преобразованные данные сторонних
проектов и исключены из этой лицензии. Условия и источники перечислены в
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). На момент публикации
RoscomVPN GeoIP и RoscomVPN Routing не содержали явного файла лицензии.

Правила участия описаны в [`CONTRIBUTING.md`](CONTRIBUTING.md), политика
безопасности — в [`SECURITY.md`](SECURITY.md).

---

> Проект не связан с разработчиками Anywhere. Используйте конфигурации на свой
> риск и проверяйте назначения наборов после установки.
