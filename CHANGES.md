# Changes on top of the base project

This project started from an existing base (originally built with a senior).
Below is what I added / fixed myself.

## Added: working Search History feature

The frontend (`Gallery.jsx`, shown on the Home page) already called
`GET /history/all`, but that endpoint did not exist anywhere in the backend -
every history request was silently failing. Separately, the code that was
meant to write a search result to the `historys` table was commented out in
`utils/imagegen.py`, so even if the endpoint had existed, there would have
been nothing to show.

I implemented the feature end to end:

- **`backend/routes/history.py`** (new) - `GET /history/all` returns the
  logged-in user's past searches, most recent first, scoped to that user via
  the JWT. Also added `DELETE /history/{id}` so a user can remove an entry.
- **`backend/utils/imagegen.py`** - `generate_images_from_json` now accepts
  an optional `db`/`user` and actually persists each generated result to the
  `historys` table. Also fixed a bug where a single `Historys()` instance was
  being reused across every item in a loop instead of creating one row per
  item.
- **`backend/routes/textdetect.py`, `imagedetect.py`, `videodetect.py`,
  `ytvideodetect.py`** - wired `Depends(get_db)` and
  `Depends(JWTBearer())` through so every search type (text, image, video,
  YouTube) now saves to history, not just some of them.
- **Bug fix:** `videodetect.py` and `ytvideodetect.py` both registered a
  route at `POST /video`, silently shadowing one another. Moved the YouTube
  route to `POST /video/youtube`.
- **`frontend/src/components/gallery/Gallery.jsx`** - fixed a broken
  `.map()` call (was reading the wrong argument for the item name), added
  loading/empty states, and added a delete button wired to the new
  `DELETE /history/{id}` endpoint.

## Why this was worth doing

It's a small, self-contained example of finding a real gap between frontend
and backend (a component quietly failing against a 404), tracing it to a
disabled write path, and shipping the fix across both the API and the UI.
