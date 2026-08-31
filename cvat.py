"""
CVAT + SF6 frame-data pipeline.

Usage:
    1. Set CVAT_URL / CVAT_USER / CVAT_PASS below (or as env vars).
    2. python cvat_sf6_pipeline.py labels Ryu
       -> prints/creates a CVAT label list for one character
    3. python cvat_sf6_pipeline.py preannotate <task_id> <moveId> <frame_offset> <recording_fps>
       -> pushes a rough track annotation onto an existing CVAT task,
          computed from that move's startup/active/recovery frame counts

Requires: pip install requests --break-system-packages
"""

import os
import re
import sqlite3
import sys

from dotenv import load_dotenv

load_dotenv()  # This searches for and loads the .env file
import requests

DB_PATH = "data/data.db"
CVAT_URL = os.environ.get("CVAT_URL", "http://localhost:8080")
CVAT_USER = os.environ.get("CVAT_USER", "admin")
CVAT_PASS = os.environ.get("CVAT_PASS", "changeme")


def db():
    return sqlite3.connect(DB_PATH)


def cvat_session():
    s = requests.Session()
    r = s.post(f"{CVAT_URL}/api/auth/login", json={"username": CVAT_USER, "password": CVAT_PASS})
    r.raise_for_status()
    key = r.json().get("key")
    if not key:
        raise RuntimeError(
            "Login succeeded but no auth token was returned - check CVAT_USER/CVAT_PASS."
        )
    # Use token auth (not just the session cookie) so POST/PATCH requests
    # aren't blocked by CSRF protection, which is what a 403 on /api/projects
    # usually means.
    s.headers.update({"Authorization": f"Token {key}"})
    return s


def first_number(field):
    """SF6 frame-data fields are messy strings like '3(14)9' or '54' or '116~121 total'.
    Pull the first plain integer out as a usable frame count."""
    if not field:
        return None
    match = re.search(r"\d+", field)
    return int(match.group()) if match else None


def get_all_characters():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT chara FROM sf6_chara ORDER BY chara")
    charas = [row[0] for row in cur.fetchall()]
    conn.close()
    return charas


def get_moves_for_character(chara):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT moveId, name, moveType, startup, active, recovery, total "
        "FROM sf6_frame_data WHERE chara = ?",
        (chara,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def build_cvat_labels(chara):
    """Build a CVAT-format label list for one character's project."""
    moves = get_moves_for_character(chara)
    labels = []
    for moveId, name, moveType, *_ in moves:
        labels.append({
            "name": moveId,          # use moveId as the canonical label (unique, matches DB)
            "attributes": [
                {"name": "display_name", "mutable": False, "input_type": "text", "default_value": name, "values": []},
                {"name": "move_type", "mutable": False, "input_type": "text", "default_value": moveType or "", "values": []},
            ],
        })
    labels.append({"name": "neutral", "attributes": []})
    return labels


def create_cvat_project(session, chara, labels):
    resp = session.post(
        f"{CVAT_URL}/api/projects",
        json={"name": f"SF6 - {chara} move detection", "labels": labels},
    )
    resp.raise_for_status()
    project = resp.json()
    print(f"Created project id={project['id']} for {chara}")
    return project["id"]


def get_move_frame_data(moveId):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, startup, active, recovery, total FROM sf6_frame_data WHERE moveId = ?",
        (moveId,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"moveId {moveId} not found")
    return row


def compute_frame_windows(moveId, frame_offset, recording_fps, game_fps=60):
    """
    frame_offset: the frame number in YOUR recording where the input was pressed.
    Converts game-internal frame counts (always 60fps in SF6) to your recording's fps.
    """
    name, startup, active, recovery, total = get_move_frame_data(moveId)
    startup_f = first_number(startup) or 0
    active_f = first_number(active) or 0
    recovery_f = first_number(recovery) or 0

    scale = recording_fps / game_fps

    active_start = frame_offset + round(startup_f * scale)
    active_end = active_start + round(active_f * scale)
    recovery_end = active_end + round(recovery_f * scale)

    return {
        "move_name": name,
        "startup_start": frame_offset,
        "active_start": active_start,
        "active_end": active_end,
        "recovery_end": recovery_end,
    }


def push_track_annotation(session, task_id, label_name, frame_start, frame_stop):
    """
    Pushes a single track (a labeled range across frames) to a CVAT task.
    NOTE: this creates a point/track shape as a rough placeholder in time;
    annotators still need to open the task and adjust/draw the actual box
    if you're doing bounding boxes too. This just saves them from having
    to guess *when* the move happens.
    """
    # Look up the numeric label id CVAT assigned when the project was created
    labels_resp = session.get(f"{CVAT_URL}/api/tasks/{task_id}")
    labels_resp.raise_for_status()
    task = labels_resp.json()
    project_id = task["project_id"]

    proj_resp = session.get(f"{CVAT_URL}/api/projects/{project_id}")
    proj_resp.raise_for_status()
    labels = proj_resp.json()["labels"]
    label_id = next(l["id"] for l in labels if l["name"] == label_name)

    annotation = {
        "tracks": [{
            "label_id": label_id,
            "frame": frame_start,
            "shapes": [
                {"type": "rectangle", "frame": frame_start, "points": [0, 0, 100, 100], "outside": False},
                {"type": "rectangle", "frame": frame_stop, "points": [0, 0, 100, 100], "outside": True},
            ],
            "attributes": [],
        }]
    }
    resp = session.patch(
        f"{CVAT_URL}/api/tasks/{task_id}/annotations?action=create",
        json=annotation,
    )
    resp.raise_for_status()
    print(f"Pushed track for '{label_name}' frames {frame_start}-{frame_stop}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None

    if cmd == "labels":
        chara = sys.argv[2]
        labels = build_cvat_labels(chara)
        print(f"{len(labels)} labels for {chara}:")
        for l in labels[:10]:
            print(" -", l["name"])
        # Uncomment to actually create the project in CVAT:
        # session = cvat_session()
        # create_cvat_project(session, chara, labels)

    elif cmd == "labels-all":
        # Preview only, no CVAT calls - useful to sanity check before creating anything
        for chara in get_all_characters():
            labels = build_cvat_labels(chara)
            print(f"{chara}: {len(labels)} labels")

    elif cmd == "create-all":
        # Creates one CVAT project per character. Safe to re-run individual
        # characters later if one fails partway - CVAT project names don't
        # need to be unique, so check the CVAT UI afterward for duplicates
        # if you re-run this after a partial failure.
        session = cvat_session()
        charas = get_all_characters()
        print(f"Creating {len(charas)} projects...")
        failed = []
        for chara in charas:
            try:
                labels = build_cvat_labels(chara)
                create_cvat_project(session, chara, labels)
            except requests.exceptions.HTTPError as e:
                print(f"  FAILED for {chara}: {e}")
                print(f"    -> response body: {e.response.text}")
                failed.append(chara)
        if failed:
            print(f"\n{len(failed)} characters failed: {failed}")
        else:
            print("\nAll projects created successfully.")

    elif cmd == "preannotate":
        task_id, moveId, frame_offset, fps = sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
        windows = compute_frame_windows(moveId, frame_offset, fps)
        print(windows)
        session = cvat_session()
        push_track_annotation(session, int(task_id), moveId, windows["active_start"], windows["active_end"])

    else:
        print(__doc__)
