#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import edit_output_folder
import create_output_folder
import bulk_create_output_folders
import settings
import about
import itemview
import database
import tagging
import new_database
import import_files
import expression
import taglist
import taggingview
import os

#import create_folders

# TODO: Scale images in taggingview when maximized
# TODO: Optimize switching between ItemView and TaggingView

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 720))
        
        #create_folders.create_folders()
        
        # Modes: overview, tagging, import, folder
        self.mode = "overview"

        # A StatusBar in the bottom of the window
        self.CreateStatusBar()

        # Setting icon
        self.SetIcon(wx.Icon("icons/logo.ico", wx.BITMAP_TYPE_ICO))

        # Setting up the menus.
        self.filemenu = wx.Menu()
        toolmenu = wx.Menu()
        viewmenu = wx.Menu()
        helpmenu = wx.Menu()
        menu_open_database = self.get_gallery_menu()

        # FILEMENU
        fileNewDatabase = self.filemenu.Append(
            1,
            "&New database",
            " Create a new database"
        )
        self.filemenu.AppendMenu(wx.ID_ANY,
                                 "&Open gallery", menu_open_database)

        self.filemenu.AppendSeparator()
        fileImportFiles = self.filemenu.Append(
            3,
            "&Import Files",
            "Import files and folders into the program"
        )
        item_create_bulk_output_folders = self.filemenu.Append(
            wx.ID_ANY,
            "&Create output folders",
            "Automatically create an output folder for each tag"
        )
        item_create_output_folder = self.filemenu.Append(
            wx.ID_ANY,
            "&Create advanced output folder",
            "Dialog for editing a specific output folder"
        )
        self.filemenu.AppendSeparator()
        item_settings = self.filemenu.Append(
            wx.ID_ANY,
            "&Settings",
            "OctoTagger settings."
        )
        fileExit = self.filemenu.Append(
            wx.ID_EXIT, "&Exit", " Terminate the program")

        # TOOLMENU
        toolStartTaggingMode = toolmenu.Append(
            7,
            "&Start tagging mode",
            "Enter the tagging mode"
        )
        toolmenu.AppendSeparator()
        toolIntegrityCheck = toolmenu.Append(
            8,
            "&Integrity check",
            "Execute an Integrity check"
        )
        toolmenu.AppendSeparator()
        toolResetCurrentDatabase = toolmenu.Append(
            9,
            "&Reset current database",
            "Reset the current database"
        )
        tool_delete_database = toolmenu.Append(
            wx.ID_ANY,
            "&Delete current database",
            "Completely removes the current database."
        )
        toolExportDatabase = toolmenu.Append(
            10,
            "&Export database",
            " Exports the current database"
        )
        toolmenu.AppendSeparator()
        toolRestoreAllFiles = toolmenu.Append(
            11,
            "&Restore all files",
            " Restores all Files"
        )

        # VIEWMENU
        viewShowAllFiles = viewmenu.Append(
            12,
            "&Show all files",
            " Shows every file"
        )
        viewShowTaggedFiles = viewmenu.Append(
            13,
            "&Show tagged files",
            " Shows the tagged files only"
        )
        viewShowUntaggedFiles = viewmenu.Append(
            14,
            "&Show untagged files",
            " Shows the untagged files only"
        )
        viewmenu.AppendSeparator()
        viewShowOutputFolders = viewmenu.Append(
            15,
            "&Show output folders",
            " Shows the output folders"
        )

        # HELPMENU
        helpManual = helpmenu.Append(
            6, "&User Manual", " How to use this program")
        item_about = helpmenu.Append(wx.ID_ANY, "&About", "About OctoTagger")

        # Creating the menubar
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(self.filemenu, "&File")
        # Adding the "toolmenu" to the MenuBar
        menuBar.Append(toolmenu, "&Tools")
        # Adding the "viewmenu" to the MenuBar
        menuBar.Append(viewmenu, "&View")
        # Adding the "helpmenu" to the MenuBar
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events
        self.Bind(wx.EVT_MENU, self.on_start_folder_mode, viewShowOutputFolders)
        self.Bind(wx.EVT_MENU, self.start_overview, viewShowAllFiles)
        self.Bind(wx.EVT_MENU, self.on_show_tagged, viewShowTaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_show_untagged, viewShowUntaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_new_database, fileNewDatabase)
        self.Bind(wx.EVT_MENU, self.on_reset, toolResetCurrentDatabase)
        self.Bind(wx.EVT_MENU, self.on_delete, tool_delete_database)
        self.Bind(wx.EVT_MENU, self.on_import, fileImportFiles)
        self.Bind(wx.EVT_MENU, self.OnManual, helpManual)
        self.Bind(wx.EVT_MENU, self.OnExit, fileExit)
        self.Bind(wx.EVT_MENU, self.OnCreateOutputFolder,
                  item_create_output_folder)
        self.Bind(wx.EVT_MENU, self.OnBulkCreate,
                  item_create_bulk_output_folders)
        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        self.Bind(
            wx.EVT_MENU,
            self.start_tagging_mode,
            toolStartTaggingMode,
        )

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)
        #self.Bind(wx.EVT_CHAR, self.OnChar)

        self.Bind(
            itemview.EVT_SELECTION_CHANGE,
            self.on_selection_change)

        # Tag and Context Pane

        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)

        self.main_box = wx.BoxSizer(wx.HORIZONTAL)
        left_panel = wx.Panel(self, size=(300, -1))
        left_panel_sz = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_panel_sz)

        tag_panel = wx.Panel(self)
        tag_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_panel.SetSizer(tag_panel_sz)

        query_field_panel = wx.Panel(self, size=(-1, 50))
        query_field_panel_sz = wx.BoxSizer(wx.HORIZONTAL)
        query_field_panel.SetSizer(query_field_panel_sz)

        tag_list_panel = wx.Panel(self)
        tag_list_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_list_panel.SetSizer(tag_list_panel_sz)

        tag_panel_sz.Add(query_field_panel, 0, wx.EXPAND | wx.ALIGN_CENTER)
        tag_panel_sz.Add(tag_list_panel, 1, wx.EXPAND)

        self.query_field = wx.TextCtrl(
            query_field_panel,
            -1,
            "",
            style=wx.TE_PROCESS_ENTER)

        self.Bind(
            wx.EVT_TEXT,
            self.on_query_text,
            self.query_field)

        self.Bind(
            wx.EVT_MAXIMIZE,
            self.OnMaximize,
        )

        self.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_query_text_enter,
            self.query_field)

        query_field_panel_sz.Add(
            self.query_field,
            1,
            wx.LEFT | wx.RIGHT | wx.UP,
            20)

        context_panel = wx.Panel(self, size=(-1, 150))

        left_panel_sz.Add(tag_panel, 1, wx.EXPAND)
        left_panel_sz.Add(context_panel, 0, wx.EXPAND)

        self.main_box.Add(left_panel, 0, wx.EXPAND)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        # Tag Pane

        self.lb_pan = tag_list_panel
        self.lb_sz = tag_list_panel_sz
        self.update_tag_list()

        self.SetSizer(self.main_box)
        self.Layout()
        self.Show(True)

        self.start_overview()

    # Define events

    def on_start_folder_mode(self, e=None):
        self.mode = "folder"

        # Set items to all current database items
        # Get gallery connection

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_folders = "SELECT pk_id, location, name FROM folder"
        cursor.execute(query_folders)
        result = cursor.fetchall()

        folders = []

        for folder in result:
            path = os.path.join(folder[1], folder[2])
            folders.append(path.encode('utf-8'))

        self.update_gallery_menu()
        self.lb.EnableAll(False)

        # Set items
        self.mainPan.SetItems(folders)
        self.Refresh()
        self.Layout()


    def on_show_tagged(self, e):
        self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file " 
                        "WHERE pk_id IN "
                        "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()       

    def on_show_untagged(self, e):
        self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file " 
                        "WHERE pk_id NOT IN "
                        "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def start_tagging_mode(self, e=None, start_file=None):
        self.mode = "tagging"

        self.items = self.mainPan.GetItems()
        self.selected_items = self.mainPan.GetSelectedItems()

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()

        if start_file:
            self.mainPan = taggingview.TaggingView(self, self.items, start_file)
        elif self.selected_items:
            start_file = self.selected_items[0]
            self.mainPan = taggingview.TaggingView(self, self.items, start_file)
        else:
            self.mainPan = taggingview.TaggingView(self, self.items)

        self.Bind(
            taggingview.EVT_EXIT_TAGGING_VIEW, 
            self.on_resume_overview_mode,
        )
        self.Bind(
            taggingview.EVT_ITEM_CHANGE,
            self.on_selection_change,
        )

        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        self.Layout()
        self.Refresh()
        self.mainPan.ReSize()

    def on_resume_overview_mode(self, e):
        self.mode = "overview"

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()
        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)
        self.start_overview()

        #self.mainPan.SetItems(self.items)
        #self.mainPan.SetSelectedItems(self.selected_items)

        self.update_tag_list()

    def on_query_text(self, e):
        if self.mode == "overview":
            if self.mainPan.GetSelectedItems():
                return

            # TODO: Check if input is a valid expression!
            query_input = e.GetEventObject().GetValue()

            if query_input == "":
                self.start_overview()

            else:
                try:
                    query_files = ("SELECT pk_id FROM file WHERE %s" %
                                   (expression.parse(query_input)))

                    # Get file list
                    cursor = database.get_current_gallery("connection").cursor()
                    cursor.execute(query_files)
                    result = cursor.fetchall()

                    items = []

                    for item in result:
                        items.append(item[0])

                    self.mainPan.SetItems(items)
                    self.Layout()

                except:
                    print "Invalid expression!"

    def on_query_text_enter(self, e):
        if self.mode == "overview":
            items = self.mainPan.GetSelectedItems()
        elif self.mode == "tagging":
            items = [self.mainPan.GetCurrentItem()]
        elif self.mode == "folder":
            return

        query = e.GetEventObject().GetValue()

        # TODO: Check if input is a valid tag name!
        tag = query

        if not (items and tag):
            return

        for item in items:
            tagging.tag_file(item, tag)

        self.update_tag_list()
        self.select_tags()
        e.GetEventObject().Clear()

    def start_overview(self, e=None):
        # Set items to all current database items
        # Get gallery connection

        self.lb.EnableAll(True)
        self.mode = "overview"

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = "SELECT pk_id FROM file"
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def on_selection_change(self, e):
        self.select_tags()

    def select_tags(self):
        if self.mode == "overview":
            items = self.mainPan.GetSelectedItems()
        elif self.mode == "tagging":
            items = [self.mainPan.GetCurrentItem()]
        elif self.mode == "folder":
            return

        self.lb.CheckAll(wx.CHK_UNCHECKED)

        checked = []
        undetermined = []
        # checkboxes = self.lb.GetStrings()

        for item in items:

            tags = []
            for tag in tagging.get_tags(item):
                tags.append(tagging.tag_id_to_name(tag))

            if not checked:
                for tag in tags:
                    checked.append(tag)

            else:
                scrapbook = []
                for tag in checked:
                    scrapbook.append(tag)

                for checked_tag in scrapbook:
                    if checked_tag not in tags:
                        checked.remove(checked_tag)
                        undetermined.append(checked_tag)

                for tag in tags:
                    if tag not in checked:
                        undetermined.append(tag)

        self.lb.SetCheckedStrings(checked)
        self.lb.SetUndeterminedStrings(undetermined)

    def on_tag_selected(self, e):
        if self.mode == "overview":
            items = self.mainPan.GetSelectedItems()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()
            undetermined_tags = self.lb.GetUndeterminedStrings()

            if items:
                # Files are selected -> tag them
                for item in items:
                    item_tags = tagging.get_tag_names(item)
                    for tag in tags:
                        if(tag not in item_tags and tag in checked_tags):
                            tagging.tag_file(item, tag)

                        elif(tag in item_tags and
                             tag not in checked_tags and
                                tag not in undetermined_tags):
                            tagging.untag_file(item, tag)
            else:
                # No files are selected -> filter them
                query_input = " ".join(checked_tags)
                self.query_field.SetValue(query_input)

        elif self.mode == "tagging":
            item = self.mainPan.GetCurrentItem()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()

            item_tags = tagging.get_tag_names(item)
            for tag in tags:
                if(tag not in item_tags and tag in checked_tags):
                    tagging.tag_file(item, tag)

                elif(tag in item_tags and tag not in checked_tags):
                    tagging.untag_file(item, tag)


    def update_tag_list(self, event=None):

        # Remove previous list
        self.lb_pan.DestroyChildren()

        tags = tagging.get_all_tags()

        self.lb = taglist.TagList(
            self.lb_pan,
            id=wx.ID_ANY,
            pos=(0, 0),
            size=(-1, -1),
            tags=tags,
        )

        self.lb_sz.Add(
            self.lb,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )

        self.Bind(taglist.EVT_TAGLIST_CHECK, self.on_tag_selected, self.lb)
        self.Bind(taglist.EVT_TAGLIST_UPDATE, self.update_tag_list, self.lb)
        self.Layout()

    def get_gallery_menu(self):
        menu = wx.Menu()

        # Create list of galleries
        gallery_list = []

        # Get system connection

        sys_conn = database.get_sys_db()
        cursor = sys_conn.cursor()

        # Select galleries
        query_galleries = "SELECT pk_id, name FROM gallery"
        cursor.execute(query_galleries)
        result = cursor.fetchall()
        for gallery in result:
            gallery_list.append(gallery)

        # Open Database menu
        for gallery in gallery_list:
            item = wx.MenuItem(
                id=100 + gallery[0],
                text=gallery[1],
                help="Switch to database: " + gallery[1],
                kind=wx.ITEM_RADIO
            )
            menu.AppendItem(item)

        return menu

    def update_gallery_menu(self):

        menu_open_database = self.filemenu.FindItemByPosition(1)

        self.filemenu.DeleteItem(menu_open_database)
        menu_open_database = self.filemenu.InsertMenu(
            1,
            wx.ID_ANY,
            "Open gallery",
            self.get_gallery_menu(),
            "")

        # Check current gallery

        current_gallery = database.get_current_gallery("id")
        for gallery in menu_open_database.GetSubMenu().GetMenuItems():
            self.Bind(wx.EVT_MENU, self.on_switch_gallery, gallery)
            if gallery.GetId() - 100 == current_gallery:
                gallery.Check()

    def on_switch_gallery(self, e):
        gallery_id = e.GetId() - 100
        database.switch_gallery(gallery_id)
        self.start_overview()
        self.update_tag_list()

    def on_new_database(self, e):
        dlg = new_database.NewDatabase(self)
        dlg.ShowModal()
        self.start_overview()
        self.update_gallery_menu()
        self.update_tag_list()

    def on_reset(self, e):
        dlg_export = wx.MessageBox(
            (
                'This will remove all tags and output folders '
                'from the database \"%s\". Your files will remain. '
                'Do you want to continue?'
                % (database.get_current_gallery("name"))
            ),
            'Warning',
            wx.CANCEL | wx.OK | wx.CANCEL_DEFAULT | wx.ICON_WARNING
        )
        print dlg_export
        if dlg_export == 4:
            database.reset_gallery(database.get_current_gallery("id"))
            self.update_tag_list()

        elif dlg_export == 16:
            print "Canceled."

    def on_delete(self, e):
        dlg_clear = wx.MessageBox(
            (
                'Are you sure you want to remove the database \"%s\"? '
                'This will remove all data associated with the database.'
                % (database.get_current_gallery("name"))
            ),
            'Information',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
        )
        # If the user continues, ask if he wants to export his files.
        if dlg_clear == 2:
            dlg_export = wx.MessageBox(
                (
                    'Do you want to export your saved files? '
                    'Click "Yes" if you want to keep your files, '
                    'and "No" if you want to delete them. '
                    '\n\nWARNING: You will not be able to retrieve '
                    'your files again if you select "No"!'
                ),
                'Export saved files?',
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dlg_export == 2:
                print "Export files now"
                # TODO: Export files!

            # Delete everything now!
            database.delete_gallery(database.get_current_gallery("id"))

        else:
            print "Aborted clearing of files"

        self.update_gallery_menu()

    def on_import(self, e):
        dlg_import = wx.FileDialog(self, "Import files", "", "",
                                   "All files (*.*)|*.*",
                                   wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import aborted."
        else:
            import_files.import_files(dlg_import.GetPaths())
            self.start_overview()

    def OnManual(self, e):
        dlg = wx.MessageDialog(
            self,
            "Octotagger is the best program and doesn't need any explanation!",
            "User Manual",
            wx.OK
        )
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def OnCreateOutputFolder(self, e):
        dlg = create_output_folder.CreateOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.mode == "folder":
            self.on_start_folder_mode()

    def OnBulkCreate(self, e):
        dlg = bulk_create_output_folders.BulkCreateOutputFolders(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSettings(self, e):
        dlg = settings.Settings(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMaximize(self, e):
        self.Layout()
        self.Refresh()

        if self.mode == "tagging":
            self.mainPan.Layout()
            self.mainPan.Refresh()
            print self.mainPan.GetSize()
            self.mainPan.ReSize()

        print self.mainPan.GetSize()

    def OnAbout(self, e):
        wx.AboutBox(about.getInfo())

    # Key events

    def OnKey(self, e):
        if self.mode == "tagging":
            if e.GetKeyCode() == wx.WXK_RIGHT:
                self.mainPan.DisplayNext()
            elif e.GetKeyCode() == wx.WXK_LEFT:
                self.mainPan.DisplayPrev()
            elif e.GetKeyCode() == wx.WXK_ESCAPE:
                self.mainPan.OnExit()
            elif e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()
        elif self.mode == "overview":
            try:
                char = chr(e.GetKeyCode())
            except:
                char = None

            if char:
                if char == "A" and e.ControlDown():
                    if not self.mainPan.IsSelectedAll():
                        self.mainPan.SetSelectedAll(True)
                    else:
                        self.mainPan.SetSelectedAll(False)

                    self.select_tags()

            if e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()

        elif self.mode == "folder":
            if e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()

        e.Skip()

    def on_double_click_item(self, e):
        item = e.GetId()
        self.start_tagging_mode(item)

    def on_right_click_item(self, e):

        menu = wx.Menu()

        if self.mode == "folder":

            if e.item:
                self.mainPan.OnRightMouseUp(e.item, e.modifiers)

            items = self.mainPan.GetSelectedItems()

            if len(items) == 0:
                item_add = menu.Append(
                    wx.ID_ANY,
                    "Add folder",
                    "Create a new folder."
                )
                self.Bind(wx.EVT_MENU, self.OnCreateOutputFolder, item_add)

            elif len(items) == 1:

                item_edit = menu.Append(
                    wx.ID_ANY,
                    "Edit",
                    "Edit this folder."
                )
                self.Bind(wx.EVT_MENU, self.EditFolder, item_edit)
                # OPTIONAL
                '''
                item_open = menu.Append(
                    wx.ID_ANY,
                    "Open in file explorer",
                    "Open this folder in your file explorer."
                )
                '''
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    "Remove this folder from the database (files remain untouched)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

            elif len(items) > 1:
                
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    "Remove the selected folders from the database (files remain untouched)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

        elif self.mode == "overview":

            if e.item:
                # Clicked an item

                self.mainPan.OnRightMouseUp(e.item, e.modifiers)
                items = self.mainPan.GetSelectedItems()

                if len(items) == 1:
                    item_rename = menu.Append(
                            wx.ID_ANY,
                            "Rename",
                            "Rename this files."
                    )

                item_remove = menu.Append(
                        wx.ID_ANY,
                        "Delete",
                        "Delete the selected files (this can not be undone)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)
                # TODO: Bind to and make function
                item_restore = menu.Append(
                        wx.ID_ANY,
                        "Restore",
                        "Remove the selected files from the database and move them to the desired location."
                )
                # TODO: Bind to and make function
            else:
                # Clicked into the background
                return

        elif self.mode == "tagging":

            item_rename = menu.Append(
                    wx.ID_ANY,
                    "Rename",
                    "Rename this file."
            )
            item_remove = menu.Append(
                    wx.ID_ANY,
                    "Delete",
                    "Delete this file (this can not be undone)."
            )
            self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)
            # TODO: Bind to and make function
            item_restore = menu.Append(
                    wx.ID_ANY,
                    "Restore",
                    "Remove this file from the database and move it to the desired location."
            )
            # TODO: Bind to and make function
      
          
        self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))

    def EditFolder(self, e):
        if not self.mode == "folder":
            return

        items = self.mainPan.GetSelectedItems()
        if len(items) != 1:
            print "Can not edit more than one folder at once."

        folder = tagging.path_to_id(items[0])
        dlg = edit_output_folder.EditOutputFolder(self, folder)
        dlg.ShowModal()
        dlg.Destroy()

        self.on_start_folder_mode()

    def RemoveItem(self, e=None):
        if self.mode == "folder":
            items = self.mainPan.GetSelectedItems()
            ids = []

            for item in items:
                ids.append(str(tagging.path_to_id(item)))

            # Delete folders

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_folders = (
                "DELETE FROM folder WHERE pk_id IN (%s)"
                % ", ".join(ids)
            )
            cursor.execute(query_folders)
            gallery.commit()

            self.on_start_folder_mode()

        elif self.mode == "overview":
            
            items = self.mainPan.GetSelectedItems()
            ids = []

            for item in items:
                ids.append(str(item))

            # TODO: Confirmation?
            # Delete files

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id IN (%s)"
                % ", ".join(ids)
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id IN (%s)"
                % ", ".join(ids)
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

            self.select_tags()
            self.start_overview()

        elif self.mode == "tagging":

            item = self.mainPan.GetCurrentItem()

            # TODO: Confirmation?
            # Delete files

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id = %d"
                % item
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id = %d"
                % item
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

            self.mainPan.DisplayNext()


app = wx.App(False)
frame = MainWindow(None, "OctoTagger")
app.MainLoop()
