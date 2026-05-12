# HikVision-Access-Log-Export-over-API
Python HikVision ACS access log exporting API script.

```md
## Экспорт событий доступа Hikvision

Скрипт `hik_acsevent_export.py` выгружает события доступа с устройства Hikvision через ISAPI и сохраняет их в CSV. Опционально можно дополнительно создать XLSX-файл.

### Требования

- Python 3
- `curl`
- Для экспорта в XLSX:

```bash
pip install openpyxl
```

### Пример использования

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user <username> \
  --password <user_password> \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Экспорт в CSV и XLSX

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user <username> \
  --password <user_password> \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv \
  --xlsx events.xlsx
```

### Запрос пароля вручную

Чтобы не передавать пароль в командной строке, используйте `-`:

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user <username> \
  --password - \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Полезные параметры

| Параметр | Описание |
|---|---|
| `--ip` | IP-адрес устройства |
| `--user` | Пользователь, по умолчанию `admin` |
| `--password` | Пароль или `-` для ручного ввода |
| `--start` | Начало периода выгрузки |
| `--end` | Конец периода выгрузки |
| `--out` | Путь к CSV-файлу |
| `--xlsx` | Путь к XLSX-файлу, опционально |
| `--only-card` | Выгружать только события по картам |
| `--max` | Размер страницы запроса, по умолчанию `200` |
| `--minor` | Код события `minor`, по умолчанию `0` |

### Пример только для событий по картам

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password VeryStrongPassword \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out card_events.csv \
  --only-card
```

### Таймзона в скрипте и на устройстве

Параметры `--start` и `--end` передаются в устройство как строки времени в формате ISO 8601, например:

```bash
--start "2025-12-01T00:00:00+03:00"
--end "2026-01-30T23:59:59+03:00"
```

Таймзона в `--start` и `--end` должна соответствовать времени, в котором устройство хранит и возвращает события. Если на устройстве настроена другая таймзона, период выгрузки может сместиться.

Рекомендуется сначала проверить текущую таймзону устройства, а затем использовать такой же UTC offset в параметрах `--start` и `--end`.

### Проверка текущей таймзоны устройства через curl

Быстрый вывод только строк с параметрами времени:

```bash
curl -sS --digest \
  -u <username>:<user_password> \
  "http://192.168.1.50/ISAPI/System/time" | grep -E "localTime|timeZone|timeMode"
```

Проверьте значение `localTime`. Суффикс в конце времени, например `+03:00`, показывает текущий UTC offset устройства.

Если устройство возвращает `+03:00`, используйте `+03:00` в `--start` и `--end`. Если устройство настроено на `+02:00`, используйте `+02:00`.

---

## Hikvision Access Events Export

The `hik_acsevent_export.py` script exports access events from a Hikvision device via ISAPI and saves them to a CSV file. Optionally, an XLSX file can also be created.

### Requirements

- Python 3
- `curl`
- For XLSX export:

```bash
pip install openpyxl
```

### Usage

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user <username> \
  --password <user_password> \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Export to CSV and XLSX

```bash
python3 hik_acsevent_export.py \
 --ip 192.168.1.50 \
  --user <username> \
  --password <user_password> \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv \
  --xlsx events.xlsx
```

### Manual password prompt

To avoid passing the password in the command line, use `-`:

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user <username> \
  --password - \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Useful parameters

| Parameter | Description |
|---|---|
| `--ip` | Device IP address |
| `--user` | Username, default is `admin` |
| `--password` | Password or `-` for manual input |
| `--start` | Export period start |
| `--end` | Export period end |
| `--out` | Path to the CSV file |
| `--xlsx` | Path to the XLSX file, optional |
| `--only-card` | Export only card events |
| `--max` | Request page size, default is `200` |
| `--minor` | Event `minor` code, default is `0` |

### Example for card events only

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password - \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out card_events.csv \
  --only-card
```

### Time zone in the script and on the device

The `--start` and `--end` parameters are passed to the device as ISO 8601 time strings, for example:

```bash
--start "2025-12-01T00:00:00+03:00"
--end "2026-01-30T23:59:59+03:00"
```

The time zone in `--start` and `--end` should match the time zone in which the device stores and returns events. If the device uses a different time zone, the exported period may be shifted.

It is recommended to check the current device time zone first and then use the same UTC offset in the `--start` and `--end` parameters.

### Checking the current device time zone with curl

Quick output of only the time-related lines:

```bash
curl -sS --digest \
  -u <username>:<user_password> \
  "http://192.168.1.50/ISAPI/System/time" | grep -E "localTime|timeZone|timeMode"
```

Check the `localTime` value. The suffix at the end of the time value, for example `+03:00`, shows the current UTC offset of the device.

If the device returns `+03:00`, use `+03:00` in `--start` and `--end`. If the device is configured with `+02:00`, use `+02:00`.
```

