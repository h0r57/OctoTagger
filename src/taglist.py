#!/usr/bin/python
# -*- coding: utf-8 --

import wx
import tagging
import output
import expression
import re

TagListCheckEvent, EVT_TAGLIST_CHECK = wx.lib.newevent.NewCommandEvent()
TagListUpdateEvent, EVT_TAGLIST_UPDATE = wx.lib.newevent.NewCommandEvent()

# TODO: Find workaround for appearance of undetermined state in some GTK themes
# OPTIONAL: Improve order of tags in list


class TagList(wx.ScrolledWindow):

    def __init__(self, parent, id, pos, size, tags):
        super(TagList, self).__init__(
            parent,
            style=wx.VSCROLL,
            id=id,
            pos=pos,
            size=size,
        )

        self.SetBackgroundColour("#FFFFFF")
        self.checkboxes = []
        self.tags = tags
        self.checked = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetScrollRate(10, 10)
        self.edit_tag = None

        for tag in self.tags:
            self.Insert(tag)

    def Insert(self, tag):
        checkbox = wx.CheckBox(
            self,
            label=tag.replace("_", " "),
            style=wx.CHK_3STATE,
        )
        self.sizer.Add(checkbox, 0, flag=wx.ALL, border=2)
        self.checkboxes.append(checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        checkbox.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)

    def OnCheck(self, e):
        wx.PostEvent(self, TagListCheckEvent(self.GetId()))

    def GetChecked(self):
        checked_cb = []

        for cb in self.GetItems():
            if cb.Get3StateValue() == wx.CHK_CHECKED:
                checked_cb.append(cb)
        return checked_cb

    def GetUndetermined(self):
        checked_cb = []

        for cb in self.GetItems():
            if cb.Get3StateValue() == wx.CHK_UNDETERMINED:
                checked_cb.append(cb)
        return checked_cb

    def GetCheckedStrings(self):
        checked_strings = []

        for cb in self.GetChecked():
            checked_strings.append(cb.GetLabelText().replace(" ", "_"))

        return checked_strings

    def GetItems(self):
        return self.checkboxes

    def GetStrings(self):
        items = self.GetItems()
        item_strings = []

        for item in items:
            item_strings.append(item.GetLabelText().replace(" ", "_"))

        return item_strings

    def SetCheckedStrings(self, strings, only=False):
        items = self.GetItems()

        for item in items:
            if item.GetLabelText().replace(" ", "_") in strings:
                item.Set3StateValue(wx.CHK_CHECKED)
            elif only:
                item.Set3StateValue(wx.CHK_UNCHECKED)

    def SetCheckedAll(self, checked=True):
        items = self.GetItems()

        if checked:
            state = wx.CHK_CHECKED
        else:
            state = wx.CHK_UNCHECKED

        for item in items:
            item.Set3StateValue(state)

    def GetUndeterminedStrings(self):
        undetermined_strings = []

        for cb in self.GetUndetermined():
            undetermined_strings.append(cb.GetLabelText().replace(" ", "_"))

        return undetermined_strings

    def SetUndeterminedStrings(self, strings):
        items = self.GetItems()

        for item in items:
            if item.GetLabelText().replace(" ", "_") in strings:
                item.Set3StateValue(wx.CHK_UNDETERMINED)

    def EnableAll(self, enable):
        items = self.GetItems()

        for item in items:
            item.Enable(enable)

    def Check(self, checkbox, state):
        checkbox.Set3StateValue(state)

    def CheckAll(self, state):
        for cb in self.GetItems():
            cb.Set3StateValue(state)

    def OnMouseRight(self, event):
        if not event.GetEventObject().IsEnabled():
            return

        item = event.GetEventObject().GetLabelText().replace(" ", "_")
        self.edit_tag = item

        menu = wx.Menu()
        item_rename = menu.Append(
            wx.ID_ANY,
            "Rename",
            "Rename this tag.",
        )
        item_remove = menu.Append(
            wx.ID_ANY,
            "Remove",
            "Remove this tag from the database.",
        )

        self.Bind(wx.EVT_MENU, self.RemoveTag, item_remove)
        self.Bind(wx.EVT_MENU, self.RenameTag, item_rename)
        self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))

    def RenameTag(self, event):

        self.checked = self.GetCheckedStrings()
        self.EnableAll(False)

        for child in self.GetItems():
            if child.GetLabelText().replace(" ", "_") == self.edit_tag:
                cb = child
                break

        text = wx.TextCtrl(
            self,
            wx.ID_ANY,
            self.edit_tag,
            style=wx.TE_PROCESS_ENTER,
        )
        text.SetFocus()
        text.SelectAll()

        self.Bind(
            wx.EVT_TEXT_ENTER,
            self.OnNewName,
            text,
        )

        self.sizer.Replace(
            cb,
            text,
        )
        cb.Show(False)
        self.Layout()

    def OnNewName(self, event):

        tag_id = tagging.tag_name_to_id(self.edit_tag)
        text = event.GetEventObject()
        new_name = text.GetValue()

        for tag_name in tagging.get_all_tags():
            if tagging.tag_name_to_id(tag_name) == tag_id:
                continue

            if tag_name.lower() == new_name.lower():
                wx.MessageBox(
                    ("Tag name already in use! Two tags can't have the same "
                     "name, regardless of case."),
                    "Error",
                    wx.OK,
                )
                return

        if not re.match('^' + expression.REG_TAG_NAME + '$', new_name):
            wx.MessageBox(
                ("Invalid input! Tag names can only contain letters, "
                 "numbers and underscores (which will be displayed "
                 "as a sapce). They must start with a letter."),
                "Error",
                wx.OK,
            )
            return

        output.rename_tag(tag_id, new_name)

        if self.edit_tag in self.checked:
            self.checked.append(new_name)

        event = TagListUpdateEvent(
            self.GetId(),
            checked=self.checked
        )
        wx.PostEvent(self, event)

    def RemoveTag(self, event):
        tag_id = tagging.tag_name_to_id(self.edit_tag)

        event = TagListUpdateEvent(
            self.GetId(),
            checked=self.GetCheckedStrings()
        )

        output.delete_tag(tag_id)
        tagging.delete_tag(tag_id)

        wx.PostEvent(self, event)
