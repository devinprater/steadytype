

def test_the_caret_is_a_real_insertion_point_where_the_student_is():
    """What a magnifier follows is the insertion point, not a drawn rectangle."""
    import pytest

    wx = pytest.importorskip("wx")
    from steadytype_client.ui.surface import LessonSurface

    app = wx.App(False) if wx.GetApp() is None else wx.GetApp()
    frame = wx.Frame(None)
    surface = LessonSurface(frame)
    surface.show("the quick brown fox", 10)
    assert surface.GetInsertionPoint() == 10
    surface.show("the quick brown fox", 3)
    assert surface.GetInsertionPoint() == 3
    frame.Destroy()
