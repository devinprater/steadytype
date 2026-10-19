from steadytype_client.sounds import NullPlayer, WinsoundPlayer


def test_player_resolves_manifest_entries(tmp_path):
    (tmp_path / "synth").mkdir()
    (tmp_path / "synth" / "correct.wav").write_bytes(b"RIFF")
    (tmp_path / "manifest.json").write_text('{"correct": {"synth": "synth/correct.wav"}}')
    player = WinsoundPlayer(tmp_path, play=lambda path: None)
    assert player.path_for("correct") == tmp_path / "synth" / "correct.wav"
    assert player.path_for("missing") is None


def test_null_player_records_names():
    player = NullPlayer()
    player.play("wrong")
    assert player.played == ["wrong"]
