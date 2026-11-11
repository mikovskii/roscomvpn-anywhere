<div align="center">

# 🛡️ RoscomVPN Routing для Anywhere

**Готовые и автоматически обновляемые правила маршрутизации для
[Anywhere](https://github.com/NodePassProject/Anywhere)**

[![CI](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/ci.yml/badge.svg)](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/ci.yml)
[![Update](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/update-configs.yml/badge.svg)](https://github.com/mikovskii/roscomvpn-anywhere/actions/workflows/update-configs.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-101310.svg)](LICENSE)

[🚀 Установка](#-установка) ·
[🚨 Настройки](#-важные-настройки) ·
[🔄 Обновление](#-обновление) ·
[❓ Вопросы](#-частые-вопросы)

</div>

---

## ✨ Возможности

- 🇷🇺 российские и белорусские ресурсы работают **напрямую**;
- 🔐 заблокированные и выбранные зарубежные сервисы идут **через VPN**;
- 🚫 реклама, телеметрия и торрент-трекеры **блокируются**;
- 🔄 правила автоматически собираются из RoscomVPN GeoIP и GeoSite;
- 🌐 поддерживаются домены, IPv4 и IPv6;
- ✅ каждая сборка проверяется перед публикацией.

Версии источников, количество правил и SHA256 файлов: [`stats.json`](stats.json).

## 🧭 Выбор профиля

| Профиль | Кому подходит | Что делает |
| --- | --- | --- |
| ⭐ **DEFAULT** | Большинству пользователей | RU/BY и доверенные сервисы напрямую, YouTube, Telegram, GitHub и др. через VPN, нежелательное блокируется |
| 🔒 **WHITELIST** | Нужен строгий белый список | Напрямую только ресурсы из белого списка, всё остальное через VPN |

> [!IMPORTANT]
> Устанавливайте **только один** профиль: DEFAULT или WHITELIST.

## 🚀 Установка

1. Включите в Anywhere режим **Rule**. В режимах Global и Direct правила не
   применяются.
2. Откройте **Settings → Routing Rules → Subscribe**.
3. Скопируйте ссылку из таблицы ниже (кнопка копирования справа от блока),
   вставьте в поле **Anywhere Routing Rule Set URL** и нажмите **Subscribe**.
4. Повторите для каждой ссылки профиля и проверьте назначенные действия.

> [!TIP]
> Используйте именно **Subscribe**, а не импорт файла: подписку можно
> обновлять одной кнопкой.

### ⭐ DEFAULT: три подписки

🟢 **DIRECT**: действие назначится автоматически

```text
https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/DIRECT.arrs
```

🔵 **PROXY**: назначьте ваш прокси или цепочку **вручную**

```text
https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/PROXY.arrs
```

🔴 **REJECT**: действие назначится автоматически

```text
https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/DEFAULT/REJECT.arrs
```

Должно получиться так:

```text
🟢 DIRECT  → DIRECT                      (автоматически)
🔵 PROXY   → ваш VPN-прокси или цепочка  (вручную!)
🔴 REJECT  → REJECT                      (автоматически)
```

### 🔒 WHITELIST: две подписки

🟢 **DIRECT**: действие назначится автоматически

```text
https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/WHITELIST/DIRECT.arrs
```

🔴 **REJECT**: действие назначится автоматически

```text
https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE/WHITELIST/REJECT.arrs
```

Маршрутом по умолчанию в Anywhere выберите ваш VPN-прокси или цепочку: через
него пойдёт всё, что не попало в белый список.

## 🚨 Важные настройки

Проверьте после установки:

- [ ] Режим **Rule** включён.
- [ ] **PROXY не оставлен на Default.** Назначьте ему прокси, цепочку или хотя
      бы действие **PROXY**. Набор на Default попадает в нижний уровень
      приоритета, и DIRECT перекрывает часть его правил: например, реклама
      Twitch (`ads.twitch.tv`) пойдёт напрямую, потому что `twitch.tv` в DIRECT.
- [ ] **Prevent DNS Leak выключен.** Большинство российских сайтов попадает в
      DIRECT по IP (GeoIP), а с этой опцией Anywhere не проверяет IP доменов.
      Такие сайты пойдут через VPN.
- [ ] **Встроенные сервисы Anywhere оставлены на Default.** Встроенный сервис с
      назначенным действием (например, YouTube на DIRECT) перекрывает
      подписки.
- [ ] **Country Bypass выключен.** Для RU он дублирует DIRECT.

## 🔄 Обновление

Репозиторий обновляет правила автоматически. Чтобы получить свежую версию в
приложении, откройте набор в **Routing Rules** и нажмите **Update**.
Назначенное действие при этом сохранится.

## ❓ Частые вопросы

<details>
<summary><b>Почему DEFAULT состоит из трёх ссылок?</b></summary>

<br>

Anywhere назначает одно действие сразу всему набору правил, поэтому DIRECT,
PROXY и REJECT хранятся в отдельных файлах.

</details>

<details>
<summary><b>Можно ли установить весь профиль одной ссылкой?</b></summary>

<br>

Нет. Один `.arrs` создаёт один набор с одним действием, а конкретный прокси
нельзя указать в файле. Модули Anywhere (`.amod`) тоже не подходят: модуль
синхронизируется одной записью размером до 900 КБ, а профиль DEFAULT
занимает около 1,5 МБ.

</details>

<details>
<summary><b>Российские сайты идут через VPN. Что делать?</b></summary>

<br>

Почти всегда причина во включённом **Prevent DNS Leak**. Большинство
российских ресурсов определяется по IP-диапазонам GeoIP, а с этой опцией
IP-правила применяются только к подключениям по IP-адресу, но не к доменам.
Выключите опцию, и такие сайты пойдут напрямую.

</details>

<details>
<summary><b>Почему правила не срабатывают для некоторых сервисов?</b></summary>

<br>

Anywhere проверяет уровни правил строго по порядку:

```text
ADBlock → встроенные сервисы → ваши наборы → наборы на Default → Country Bypass
```

Подписки из этого репозитория относятся к «вашим наборам». Встроенный ADBlock
или встроенный сервис с назначенным действием стоит выше и выигрывает.
Оставьте встроенные сервисы на Default.

</details>

<details>
<summary><b>Обновляются ли правила в приложении сами?</b></summary>

<br>

Файлы в репозитории обновляются автоматически, но в текущей версии Anywhere
подписанный набор обновляется кнопкой **Update**.

</details>

## ⚙️ Как это работает

Правила генерируются из
[RoscomVPN GeoIP](https://github.com/hydraponique/roscomvpn-geoip) и
[RoscomVPN GeoSite](https://github.com/hydraponique/roscomvpn-geosite) с теми
же категориями и порядком `block-proxy-direct`, что и оригинальные профили
RoscomVPN. Точные версии источников записаны в [`sources.json`](sources.json).

Каждые шесть часов GitHub Actions проверяет новые теги источников и при
обновлении:

1. 📥 загружает новые версии GeoIP и GeoSite;
2. 🏗️ генерирует `.arrs`;
3. 🔍 проверяет формат, CIDR, дубликаты, лимиты и приоритеты;
4. 🛑 останавливается, если число правил изменилось аномально;
5. 📤 публикует изменения от имени `github-actions[bot]`.

📦 [GitHub Release](https://github.com/mikovskii/roscomvpn-anywhere/releases)
с ZIP-архивами профилей и `SHA256SUMS` создаётся только при изменении
генератора. Обычные обновления данных попадают сразу в репозиторий, и
подписки получают их по ссылкам выше.

## 🛠️ Для разработчиков

<details>
<summary><b>Ручная генерация</b></summary>

<br>

```sh
python3 scripts/generate_anywhere.py \
  --geosite /path/to/roscomvpn-geosite \
  --geoip /path/to/roscomvpn-geoip

python3 scripts/validate_anywhere.py
python3 -m unittest discover -s tests -v
```

</details>

<details>
<summary><b>Преобразование правил</b></summary>

<br>

- Поддерживаются доменные суффиксы, ключевые слова, IPv4 и IPv6 CIDR.
- Записи GeoSite `full:` становятся суффиксами: в Anywhere нет типа для
  точного совпадения домена.
- Чтобы сохранить порядок Xray `block-proxy-direct`, правила, полностью
  покрытые более приоритетным суффиксом, ключевым словом или CIDR, удаляются.

</details>

<details>
<summary><b>Защита от плохих данных</b></summary>

<br>

- Валидатор отклоняет суффиксы из одной метки вне списка
  `ALLOWED_SINGLE_LABEL_SUFFIXES` (например, `com`) и публичные CIDR короче
  `/8` для IPv4 или `/16` для IPv6.
- Правила PROXY, вложенные в домены DIRECT, выводятся как предупреждения: они
  работают только при явном действии у набора PROXY.
- Генератор сравнивает число правил с текущим `stats.json` и прерывает сборку,
  если набор изменился больше чем на 15% и больше чем на 50 правил. Если
  изменение ожидаемо, запустите генератор с `--allow-large-change`.

</details>

<details>
<summary><b>Запуск workflow</b></summary>

<br>

[`update-configs.yml`](.github/workflows/update-configs.yml) запускается:

- по расписанию каждые шесть часов;
- при изменении скриптов или `sources.json` в `main`;
- вручную через `workflow_dispatch` с параметрами `allow_large_change` и
  `release`;
- событием `repository_dispatch` типа `update-anywhere-configs`.

</details>

## 🙏 Благодарности

Проект основан на правилах и идеях
[RoscomVPN Routing](https://github.com/hydraponique/roscomvpn-routing).
Спасибо авторам и участникам:

- [RoscomVPN Routing](https://github.com/hydraponique/roscomvpn-routing):
  оригинальные профили для Happ, INCY и Mihomo;
- [RoscomVPN GeoIP](https://github.com/hydraponique/roscomvpn-geoip):
  списки IP-диапазонов;
- [RoscomVPN GeoSite](https://github.com/hydraponique/roscomvpn-geosite):
  списки доменов;
- [Anywhere](https://github.com/NodePassProject/Anywhere): приложение и
  формат `.arrs`.

Все права на оригинальные проекты принадлежат их авторам.

## 📄 Лицензия

Скрипты, workflow и документация распространяются по [MIT License](LICENSE).

Файлы в `ANYWHERE/` содержат преобразованные данные сторонних проектов и
исключены из этой лицензии. Условия и источники перечислены в
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). На момент публикации
RoscomVPN GeoIP и RoscomVPN Routing не содержали явного файла лицензии.

Правила участия: [`CONTRIBUTING.md`](CONTRIBUTING.md) · безопасность:
[`SECURITY.md`](SECURITY.md)

---

<div align="center">

<sub>Проект не связан с разработчиками Anywhere. Используйте конфигурации на
свой риск и проверяйте назначения наборов после установки.</sub>

</div>
