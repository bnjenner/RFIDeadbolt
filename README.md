# RFIDeadbolt

Unlock your GNOME session by tapping an RFID tag on a USB serial reader.

A small Python daemon listens to a serial RFID reader, compares the scanned
tag against a stored SHA-256 hash, and — on a match — calls
`loginctl unlock-session` to unlock the active GNOME session. Runs as a
per-user `systemd` service so it starts with your desktop.

## Requirements

- Linux with GNOME / `systemd --user`
- Python 3 and `pyserial` (`pip install --user pyserial`)
- A USB serial RFID reader (e.g. an Arduino + RC522 presenting as `/dev/ttyACM0`)
- Your user in the `dialout` group for serial access:
  ```
  sudo usermod -aG dialout $USER   # log out/in afterwards
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
