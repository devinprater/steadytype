"""Translate a wx key event into the engine's normalized event."""

from __future__ import annotations

import wx
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side

NAMED = {
    wx.WXK_RETURN: Key.ENTER, wx.WXK_TAB: Key.TAB, wx.WXK_ESCAPE: Key.ESCAPE,
    wx.WXK_BACK: Key.BACKSPACE, wx.WXK_DELETE: Key.DELETE, wx.WXK_INSERT: Key.INSERT,
    wx.WXK_HOME: Key.HOME, wx.WXK_END: Key.END, wx.WXK_PAGEUP: Key.PAGE_UP,
    wx.WXK_PAGEDOWN: Key.PAGE_DOWN, wx.WXK_LEFT: Key.LEFT, wx.WXK_UP: Key.UP,
    wx.WXK_RIGHT: Key.RIGHT, wx.WXK_DOWN: Key.DOWN, wx.WXK_SPACE: Key.SPACE,
}


def from_wx(event) -> KeyEvent | None:
    code = event.GetKeyCode()
    modifiers = set()
    if event.ShiftDown():
        modifiers.add(Modifier.SHIFT)
    if event.ControlDown():
        modifiers.add(Modifier.CONTROL)
    if event.AltDown():
        modifiers.add(Modifier.ALT)
    frozen = frozenset(modifiers)

    if wx.WXK_F1 <= code <= wx.WXK_F12:
        return KeyEvent("down", Key(f"f{code - wx.WXK_F1 + 1}"), None, frozen,
                        Side.NONE, False, 0, 0.0)
    if code in NAMED:
        key = NAMED[code]
        text = " " if key is Key.SPACE else None
        return KeyEvent("down", key, text, frozen, Side.NONE, False, 0, 0.0)

    unicode_key = event.GetUnicodeKey()
    if unicode_key and unicode_key >= 32:
        text = chr(unicode_key)
        lowered = text.lower()
        try:
            key = Key(lowered)
        except ValueError:
            key = Key.UNKNOWN
        return KeyEvent("down", key, text, frozen, Side.NONE, False, 0, 0.0)
    return None
