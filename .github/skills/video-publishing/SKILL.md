---
name: video-publishing
description: 'Publish a physics-through-anim video (a lesson''s final stitched video, a named compilation, or a single scene clip) to YouTube via the youtube-uploader-mcp MCP server (github.com/anwerj/youtube-uploader-mcp). Use when the user asks to publish, upload, or post a video to YouTube. Covers the two-actor prepare/upload/complete workflow, the exact MCP tool names (authenticate, accesstoken, channels, refreshtoken, upload_video, update_video), one-time OAuth2 setup, the publications.toml registry, and mandatory visibility/confirmation safety rules before any upload.'
---

# Video Publishing (YouTube, via youtube-uploader-mcp)

Publishing uploads a video to an external, publicly-reachable platform --
this is a **hard-to-reverse, externally-visible action**. Never call an
upload tool without first showing the user exactly what will be uploaded
(file, title, description, tags, visibility) and getting explicit
confirmation, especially for `--visibility public`.

## 0. Why this is a two-actor workflow

`main.py`/`render.py` in this repo only run local subprocesses (manim,
ffmpeg) -- plain Python code cannot call an MCP tool, only the agent driving
the conversation can. So publishing is split:

1. **Prepare** (scriptable, this repo's code): resolve the source to an
   actual file, validate it exists, persist a `status = "pending"` record.
2. **Upload** (agent-mediated): the agent calls the YouTube MCP server's own
   tools directly, using the resolved file path and metadata from step 1.
3. **Complete** (scriptable): record the returned video id/URL, flip the
   record to `status = "published"`.

## 1. The MCP server: `youtube-uploader-mcp`

Repo: <https://github.com/anwerj/youtube-uploader-mcp>. It registers these
tools (use `tool_search` to confirm they're loaded before calling any of
them -- do not assume a fixed name without checking, per this environment's
deferred-tool convention):

| Tool | Purpose |
| --- | --- |
| `authenticate` | Generates an OAuth2 URL for the user to open and approve in a browser. |
| `accesstoken` | Exchanges the code from that URL for stored credentials + channel info. |
| `channels` | Lists the authenticated channel(s). |
| `refreshtoken` | Force-refreshes stored tokens. |
| `upload_video` | Uploads the file; sets title, description, tags, category, language, privacy status, made-for-kids flag, optional scheduled publish time. |
| `update_video` | Post-upload only: add to a playlist, set a custom thumbnail (<2MB), attach subtitles/captions. |

### One-time setup (never do this automatically without the user's go-ahead)

- The server is a downloaded binary registered in the user's MCP client
  config (VS Code/Cursor/Claude Desktop), not a pip/npm package.
- It needs a Google OAuth 2.0 `client_secret.json` from the Google Developer
  Console. **Never ask the user to paste its contents into chat, and never
  read/print that file yourself** -- it's a credential file; point the user
  to the server's own install script/docs instead:
  `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/anwerj/youtube-uploader-mcp/master/scripts/install.sh)"`
  (macOS/Linux) or the equivalent PowerShell one-liner for Windows.
- If `tool_search` finds no `upload_video`-like tool, tell the user the
  server isn't configured yet and point them at the install script above --
  do not attempt to install or register an MCP server yourself.
- First real use in a fresh setup: call `authenticate`, have the user open
  the returned URL and approve access, then call `accesstoken` with the code
  it gives back. `channels` confirms which channel is now authenticated
  before you upload anything to it.

## 2. Step 1 -- Prepare (this repo's CLI)

```bash
uv run python main.py publish-prepare <source> \
  --title "..." --description "..." \
  --tags "tag1,tag2,tag3" \
  --visibility unlisted \
  --category 27 \
  --slug my-video-slug
```

`<source>` accepts:
- `lesson:<lesson_name>` -- that lesson's final stitched video (`media/final/<lesson>_full.mp4`)
- `compilation:<name>` -- a named compilation from `.github/skills/video-compilation/SKILL.md`'s registry
- `scene:<lesson_name>:<scene_id>` -- one individual rendered scene clip
- a bare path to an existing `.mp4`

This **only** resolves the file and persists a `lessons/publications.toml`
record with `status = "pending"` — it does not contact YouTube. Read back the
printed file path; that's the exact path to hand to `upload_video`.

Defaults matter for safety: `--visibility` defaults to `unlisted`,
`--category` defaults to `27` (Education) since these are physics lessons,
`--made-for-kids` defaults to off. **Never pass `--visibility public` unless
the user explicitly said "public" or "publicly visible"** — "publish" alone
is not a request for public visibility.

## 3. Step 2 -- Upload (the agent calls the MCP tool)

Before calling `upload_video`, show the user a one-line confirmation summary
(file, title, visibility) and wait for them to confirm — do not chain
straight from `publish-prepare` into calling `upload_video` unprompted.

Call `upload_video` with the file path printed by `publish-prepare` and the
same metadata (title/description/tags/category/visibility/made_for_kids).
If the user also wants a playlist, thumbnail, or subtitles, call the
separate `update_video` tool afterward with the video id `upload_video`
returned — those are not part of `upload_video` itself.

## 4. Step 3 -- Complete (this repo's CLI)

```bash
uv run python main.py publish-complete <slug> --video-id <id> --url <url>
```

Use the exact `video_id`/URL returned by `upload_video` — never fabricate or
guess one. This flips the record to `status = "published"` in
`publications.toml` so `list-publications` shows an accurate history and a
future request to "publish X" can first check whether it already was.

```bash
uv run python main.py list-publications
```

## 5. Rules to follow every time

- **Always prepare before uploading** — never call `upload_video` with a
  path you haven't resolved through `publish-prepare` first, so there's
  always a persisted record even if the upload succeeds but `publish-complete`
  is forgotten.
- **Always confirm the file and metadata with the user before the actual
  `upload_video` call** — the prepare step is safe/reversible (it only
  writes a local TOML record), the upload step is not.
- **Default visibility is `unlisted`, never `public`, unless the user says so
  explicitly.**
- **Never read, print, or ask for the contents of `client_secret.json` or any
  OAuth token** — those stay inside the MCP server's own storage; only the
  MCP tool calls themselves (`authenticate`/`accesstoken`/`refreshtoken`)
  touch them.
- If `publish-prepare` reports the resolved file doesn't exist, render/stitch
  it first (see the `physics-animation-standards` or `video-compilation`
  skills) — don't upload a stale or missing file.
- A `source` can be prepared and published more than once under different
  `--slug`s (e.g. a private draft upload, then a public one later) — each
  `--slug` is an independent record in `publications.toml`, same pattern as
  `video-compilation`'s named, overlap-allowed compilations.
