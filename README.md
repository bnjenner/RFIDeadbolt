# RFIDeadbolt

Unlock your GNOME session by tapping an RFID tag on a USB serial reader.

A small Python daemon listens to a serial RFID reader, compares the scanned
tag against a stored SHA-256 hash, and — on a match — calls
`loginctl unlock-session` to unlock the active GNOME session. Runs as a
per-user `systemd` service so it starts with your desktop.

## Requirements

- Linux with GNOME / `systemd --user`
- Python 3 and `pyserial` (`pip install --user pyserial`)
- A USB serial RFID reader — an Arduino Micro + RFID-RC522 presenting as
  `/dev/ttyACM0`; firmware lives in `sketch/` (see [Hardware](#hardware))
- Your user in the `dialout` group for serial access:
  ```
  sudo usermod -aG dialout $USER   # log out/in afterwards
  ```

## Hardware

The reader side is an **Arduino Micro** (ATmega32U4) driving an **RFID-RC522**
(MFRC522, 13.56 MHz) over SPI. The Micro enumerates as a USB CDC serial device
(`/dev/ttyACM0`), so no extra USB-serial adapter is needed.

### Wiring

| RC522 | Arduino Micro | Notes                                    |
| ----- | ------------- | ---------------------------------------- |
| SDA   | D10           | chip select (`RFID_PIN_SDA`)             |
| SCK   | D7            | `RFID_PIN_SCK`                           |
| MOSI  | D8            | `RFID_PIN_MOSI`                          |
| MISO  | D9            | `RFID_PIN_MISO`                          |
| IRQ   | —             | unused, leave disconnected               |
| GND   | GND           |                                          |
| RST   | D2            | reset (`RFID_PIN_RST`)                   |
| 3.3V  | 3.3V          | **3.3V only** — 5V will damage the RC522 |

The ATmega32U4 brings *hardware* SPI out only on the ICSP header — unlike the
Uno, D11/D12/D13 are ordinary I/O with no SPI behind them, so Uno-based RC522
tutorials do not apply. Rather than wire into the ICSP block, the bundled driver
bit-bangs SPI, which frees the bus to live on any digital pins.

All five assignments are `#define`s at the top of `sketch/rfid_sketch.ino` and
can be moved to any free pins. Avoid D0/D1 (serial) and D13 (tied to the onboard
LED, which you especially do not want on the MISO input). Feeding the RC522's
3.3V MISO output into the 5V Micro is fine — the input threshold is ~3.0V.

Power the module from the board's **3.3V** pin, not ICSP-2 — that pin sits in
the ICSP block next to MISO and carries 5V.

## Firmware (`sketch/`)

```
sketch/
  rfid_sketch.ino              the sketch — init the reader, print tags
  RFID.h                       MFRC522 driver (public domain, Miguel Balboa),
  RFID.cpp                     with hardware SPI replaced by a bit-banged bus
  RFID_license.txt             attribution for the driver
```

The sketch opens the serial port at **115200 baud**, prints `start` once the
host has opened the port, then polls for tags. Each detected tag's serial
number is printed as one hex string per line — exactly what the daemon's
`SerialRFID.listen()` reads. Nothing is printed when no tag is present, or when
a card is detected but its serial cannot be read (the driver's `None` sentinel,
which the daemon also ignores if it ever reaches the host).

### Flashing

1. Copy `sketch/` somewhere as a sketch folder named `rfid_sketch` (the Arduino
   IDE requires the folder name to match the `.ino`), or open
   `sketch/rfid_sketch.ino` and let the IDE offer to create that folder — the
   `RFID.h`/`RFID.cpp` files sit alongside the `.ino` and need no library
   install.
2. Select **Tools → Board → Arduino Micro** and the matching port. Check this if
   you use the IDE for other boards — the pin numbers above are specific to the
   Micro, and mean entirely different GPIOs elsewhere.
3. Upload, then confirm with the Serial Monitor at 115200 baud: you should see
   `start`, and a hex string each time you tap a tag.
4. Close the Serial Monitor before starting the daemon — only one process can
   hold the serial port at a time.

The baud rate here must match `baudrate` in `~/.config/rfideadbolt/config.json`.

The IDE builds the folder in your sketchbook, not this repo, so a copy goes
stale as soon as the driver changes here — which surfaces as
`no matching function for call to 'RFID::RFID(int, int, int, int, int)'` when a
new `.ino` meets an old `RFID.h`. Symlinking instead of copying avoids it:

```
SKETCHBOOK=~/Arduino/rfid_sketch          # snap IDE: ~/snap/arduino/current/Arduino/rfid_sketch
mkdir -p "$SKETCHBOOK"
ln -sf "$PWD"/sketch/{rfid_sketch.ino,RFID.h,RFID.cpp} "$SKETCHBOOK"/
```

## Install

From the repo root:

```
./install.sh
```

This will:

- copy the Python modules to `~/.local/share/rfideadbolt/`
- generate `~/.config/rfideadbolt/config.json` from `config_template.json`
- install a `rfideadbolt-create-key` helper to `~/.local/bin/`
- install a user systemd unit at `~/.config/systemd/user/rfideadbolt.service`

If `~/.config/rfideadbolt/config.json` already exists, it is left alone.

## First-time setup

1. Edit `~/.config/rfideadbolt/config.json` if needed (device path, baud rate).
2. Enroll a tag — run the helper and tap the tag on the reader:
   ```
   rfideadbolt-create-key
   ```
   The tag's SHA-256 hash is written to `~/.config/rfideadbolt/rfideadbolt.hash`
   with `0600` permissions.
3. Start the service:
   ```
   systemctl --user enable --now rfideadbolt.service
   ```
4. Tail logs:
   ```
   journalctl --user -u rfideadbolt.service -f
   ```

## Configuration

`config.json` fields:

| Field            | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| `device`         | Serial device path, e.g. `/dev/ttyACM0`                       |
| `baudrate`       | Baud rate of the reader (e.g. `115200`)                       |
| `hash_file`      | Absolute path to the stored tag hash                          |
| `session_query`  | Command that prints `true`/`false` for screensaver-active     |
| `session_unlock` | Command that unlocks the session (default: `loginctl unlock-session`) |

## Repo layout

```
install.sh                     install script (user-scoped)
RFIDeadbolt/
  SerialRFID.py                thin wrapper around pyserial
  utils.py                     hash save/check helpers
  create_key.py                enroll a tag
  gnome_unlock.py              the daemon
  config_template.json         template — __HASH_FILE__ is filled in at install
sketch/
  rfid_sketch.ino              Arduino Micro firmware for the RC522 reader
  RFID.h / RFID.cpp            MFRC522 driver used by the sketch
  RFID_license.txt             driver attribution
```

## Uninstall

```
systemctl --user disable --now rfideadbolt.service
rm -rf ~/.local/share/rfideadbolt
rm -f  ~/.local/bin/rfideadbolt-create-key
rm -f  ~/.config/systemd/user/rfideadbolt.service
# keep or remove your config + hash:
# rm -rf ~/.config/rfideadbolt
systemctl --user daemon-reload
```

## Security notes

- Only a SHA-256 hash of the tag ID is stored; the raw ID is never written to disk.
- `rfideadbolt.hash` is written with `0600` permissions.
- The service is a *user* unit and only operates on your own session — it does
  not run as root and cannot unlock other users' sessions.
- Process terminates after 3 tailed authorization attempts.
