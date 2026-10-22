import visionpipe


def test_version_is_available() -> None:
    assert isinstance(visionpipe.__version__, str)
    assert visionpipe.__version__


def test_public_names_are_importable() -> None:
    for name in visionpipe.__all__:
        assert hasattr(visionpipe, name), name


def test_lazy_subpackages_are_available() -> None:
    import visionpipe as vp

    assert callable(vp.video.extract_video_frames)
    assert callable(vp.video.get_video_meta)
    assert callable(vp.image.rewrite_img)
    assert callable(vp.dataset.Dataset)
    assert callable(vp.file.calc_hash)
