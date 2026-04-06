from pathlib import Path

from apps.av_tools.move_by_actor.app import service
from apps.av_tools.move_by_actor.app.config import Config
from apps.av_tools.move_by_actor.app.models import MovieInfo
from apps.av_tools.move_by_actor.app.scanner import ScanItem


def test_move_videos_by_actor_reuses_api_cache(
    tmp_path: Path, monkeypatch
) -> None:
    source_a = tmp_path / "ABC-123.mp4"
    source_b = tmp_path / "ABC123-copy.mkv"
    source_a.write_text("x", encoding="utf-8")
    source_b.write_text("x", encoding="utf-8")

    items = [
        ScanItem(path=source_a, is_dir=False, code_hint="ABC-123"),
        ScanItem(path=source_b, is_dir=False, code_hint="ABC-123"),
    ]
    monkeypatch.setattr(service, "scan_items_for_move", lambda *_args, **_kwargs: items)

    calls: list[str] = []

    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        calls.append(code)
        return MovieInfo(movie_id=code, title="", actors=["Alice"])

    monkeypatch.setattr(service, "get_movie_info", fake_get_movie_info)

    scanned, moved, interrupted = service.move_videos_by_actor(
        input_dir=tmp_path,
        dest_root=tmp_path,
        apply_changes=False,
        recursive=False,
        cfg=Config(),
    )

    assert scanned == 2
    assert moved == 2
    assert interrupted is False
    assert calls == ["ABC-123"]


def test_move_videos_by_actor_apply_handles_skip_and_collision(
    tmp_path: Path, monkeypatch
) -> None:
    no_code = tmp_path / "untitled.mp4"
    api_error = tmp_path / "ERR-200.mp4"
    multi_actor = tmp_path / "MUL-300.mp4"
    success = tmp_path / "OK-100.mp4"
    for file_path in (no_code, api_error, multi_actor, success):
        file_path.write_text("x", encoding="utf-8")

    items = [
        ScanItem(path=no_code, is_dir=False, code_hint=None),
        ScanItem(path=api_error, is_dir=False, code_hint="ERR-200"),
        ScanItem(path=multi_actor, is_dir=False, code_hint="MUL-300"),
        ScanItem(path=success, is_dir=False, code_hint="OK-100"),
    ]
    monkeypatch.setattr(service, "scan_items_for_move", lambda *_args, **_kwargs: items)

    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        if code == "ERR-200":
            raise RuntimeError("api failed")
        if code == "MUL-300":
            return MovieInfo(movie_id=code, title="", actors=["A", "B"])
        return MovieInfo(movie_id=code, title="", actors=["A"])

    monkeypatch.setattr(service, "get_movie_info", fake_get_movie_info)

    existing_target = tmp_path / "A" / success.name
    existing_target.parent.mkdir(parents=True, exist_ok=True)
    existing_target.write_text("occupied", encoding="utf-8")

    scanned, moved, interrupted = service.move_videos_by_actor(
        input_dir=tmp_path,
        dest_root=tmp_path,
        apply_changes=True,
        recursive=False,
        cfg=Config(),
    )

    assert scanned == 4
    assert moved == 1
    assert interrupted is False
    assert no_code.exists()
    assert api_error.exists()
    assert multi_actor.exists()
    assert not success.exists()
    assert (tmp_path / "A" / "OK-100-1.mp4").exists()


def test_move_videos_by_actor_returns_interrupted_on_keyboard_interrupt(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "ONE-100.mp4"
    source.write_text("x", encoding="utf-8")

    def interrupted_items():
        yield ScanItem(path=source, is_dir=False, code_hint="ONE-100")
        raise KeyboardInterrupt

    monkeypatch.setattr(
        service,
        "scan_items_for_move",
        lambda *_args, **_kwargs: interrupted_items(),
    )
    monkeypatch.setattr(
        service,
        "get_movie_info",
        lambda code, cfg: MovieInfo(movie_id=code, title="", actors=["Only"]),
    )

    scanned, moved, interrupted = service.move_videos_by_actor(
        input_dir=tmp_path,
        dest_root=tmp_path,
        apply_changes=False,
        recursive=False,
        cfg=Config(),
    )

    assert scanned == 1
    assert moved == 1
    assert interrupted is True

