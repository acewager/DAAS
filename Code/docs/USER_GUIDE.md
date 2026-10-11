# User Guide — Software Requests & Persistent Storage

Practical how-tos for the two features people most often ask about.

---

## 1. Requesting software installation

Users can ask an admin to install extra software into a **running** desktop.

### The flow

1. Open **Requests** in the top navigation
2. Click **New request**
3. Choose a **running** instance (software installs into running desktops only)
4. Enter the **software name** — the exact Ubuntu/Debian **apt package name**
5. Add a justification (helps the admin approve quickly) and submit
6. An admin approves → Celery installs it automatically → the status becomes
   **Installed** (or **Failed**, with the reason shown on the card)

Statuses: `Pending → Approved → Installing → Installed` or `Rejected` / `Failed`.

### ⚠️ Choosing a package name (why installs fail)

Installation runs `apt-get install <name>` inside the desktop's Ubuntu
container, so **only packages available in Ubuntu's apt repositories work**.

| Request | Result | Why |
|---|---|---|
| `htop`, `vim`, `curl`, `git`, `firefox` | ✅ Installed | In Ubuntu's repos |
| `office365` | ❌ Failed — *Unable to locate package* | Microsoft Office isn't in apt (proprietary, Windows/web only) |
| `joplin` | ❌ Failed — *Unable to locate package* | Not in Ubuntu's repos (installs via script/Flatpak/AppImage) |
| `htop; rm -rf /` | ❌ Rejected at submit | Names are strictly validated — no shell metacharacters |

**How to check before requesting:**

- Search <https://packages.ubuntu.com> for the exact package name
- From a terminal: `apt-cache policy <name>` (or ask the admin to check)
- If the software isn't in apt, request the closest available package — or an
  admin can install it another way (a future feature will support custom
  install commands)

> **Note for admins:** failed installs show the exact `apt-get` error in
> `GET /api/v1/admin/events/` (`SOFTWARE_INSTALL_FAILED` → `metadata.error`).

---

## 2. Persistent storage: retain, delete, and re-attach

Persistent desktops store `/home/user` in a dedicated Docker volume that
survives restarts and desktop deletion.

### When deleting a desktop

You'll be asked what to do with the data:

- **Keep my data (default)** — the volume is retained and *can be attached to
  a future desktop*
- **Delete my data permanently** — the volume is removed immediately

### Re-attaching retained data (the part that's easy to miss)

Keeping data alone doesn't attach it to anything — you attach it **while
creating the new desktop**:

1. Make sure **Persistent storage** is ticked in the order form
2. An **"Attach retained data (optional)"** selector appears when you have
   retained volumes
3. Pick the old desktop's storage (labelled with its name and the release
   date) — or leave it empty for fresh storage
4. Create — the new desktop boots **with your old files** in `/home/user`

> **Notes**
> - Retained storage lives on the server until it's attached to a new desktop
>   and later deleted — or until an admin prunes it
> - Attaching replaces the new desktop's empty data volume with your retained
>   one; there's no merging
> - If a retained volume shows as attachable but the desktop comes up empty,
>   the volume's data was already removed (e.g. by an admin cleanup) — ask
>   the admin to check `docker volume ls`

### For admins

- `GET /api/v1/volumes/` — a user's retained volumes (their own view)
- Deleting with `?delete_data=true` on `DELETE /api/v1/instances/{id}/`
  removes the volume as well as the container
- `docker volume ls | grep dcp-data` — all persistent volumes on the host
