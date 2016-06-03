# -*- coding: utf-8 -*-
__author__ = 'Jacky Yu <jacky325@qq.com>'

import wx,os,gettext,re,sys,shutil,base64
import wx.lib.mixins.inspection
import wx.aui
from datetime import *

import Config as CFG
import Images as IMG

#---------------------------------------------------------------------------
def GetConfig():
    if not os.path.exists(GetDataDir()):
        os.makedirs(GetDataDir())

    config = wx.FileConfig(
        localFilename = os.path.join(GetDataDir(), "options"))
    return config

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def opj(path):
    """Convert paths to the platform-specific separator"""
    st = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def FileGetContents(path):
    fp = open(path, 'r')
    content = fp.read()
    fp.close()
    try:
        data = content.decode("utf-8")
    except:
        data = content
    return data

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def FilePutContents(path, content, mode = 'w'):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    try:
        data = content.decode("utf-8")
    except:
        data = content
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    fp  = file(path, mode)
    if path[-4:] == '.hhc' or path[-4:] == '.hhk':
        fp.write(data.encode('gbk'))
    else:
        fp.write(data)
    fp.close()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------


def GetDataDir():
    """
    Return the standard location on this platform for application data
    """
    sp = wx.StandardPaths.Get()
    return sp.GetUserDataDir()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def GetAppPath():
    #get current path
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def ExpandTree(tree, item = None):
    if item == None:
        item = tree.GetRootItem()
    child, cookie = tree.GetFirstChild(item)
    while child.IsOk():
        tree.Expand(child)
        tree.ExpandAllChildren(child)
        child, cookie = tree.GetNextChild(item, cookie)

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def CopyTree(tree, fr, to):
    frChild, cookie = tree.GetFirstChild(fr)
    while frChild.IsOk():
        datas   = tree.GetDataDict(frChild)
        image   = tree.GetItemImage(frChild)
        toChild = tree.AppendItem(to, datas["name"], image, data=wx.TreeItemData(datas))
        tree.SetItemImage(toChild, image+1, wx.TreeItemIcon_Selected)
        if tree.ItemHasChildren(frChild):
            CopyTree(tree, frChild, toChild)
        frChild, cookie = tree.GetNextChild(fr, cookie)

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def SetTextctrlValue(textctrl, content):
    try:
        textctrl.SetValue(content)
    except:
        textctrl.SetValue(content.decode("utf-8"))

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def ConvertTreeToDatas(tree, parent = None):
    if parent == None:
        parent = tree.GetRootItem()
    child, cookie = tree.GetFirstChild(parent)
    datas = []
    while child.IsOk():
        data = tree.GetDataDict(child)
        if tree.ItemHasChildren(child):
            data["children"] = ConvertTreeToDatas(tree, child)
        datas.append(data)
        child, cookie = tree.GetNextChild(parent, cookie)
    
    return datas

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

class SunnyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):

        self.locale = wx.Locale(CFG.Language)
        if self.locale.IsOk():
            self.locale.AddCatalog(CFG.AppName)
        else:
            self.locale = None

        self.InitInspection()  # for the InspectionMixin base class

        # For debugging
        if CFG.Debug:
            self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG|wx.PYAPP_ASSERT_EXCEPTION)

        wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)
        self.SetAppName(CFG.AppName)
                
        #show the splash screen.
        SunnySplashScreen()

        return True

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

class SunnySplashScreen(wx.SplashScreen):
    def __init__(self):
        if CFG.ShowSplash:
            wx.SplashScreen.__init__(self, IMG.Splash.GetBitmap(),
                                     wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                     60000, None, -1)
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            self.fc = wx.FutureCall(1800, self.ShowMain)
        else:
            self.ShowMain()

    def OnClose(self, evt):
        # Make sure the default handler runs too so this window gets destroyed
        evt.Skip()
        self.Hide()
        
        # if the timer is still running then go ahead and show the main frame now
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()

    def ShowMain(self):
        frame = SunnyFrame(None, CFG.AppName + ' ' + CFG.Version)
        frame.Show()
        if CFG.ShowSplash:
            if self.fc.IsRunning():
                self.Raise()
            self.Hide()
        if CFG.ShowTip:
            wx.CallAfter(frame.ShowTip)

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

class SunnyPanel(wx.Panel):
    """
    Just a simple derived panel where we override Freeze and Thaw so they are
    only used on wxMSW.    
    """
    def Freeze(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(SunnyPanel, self).Freeze()
                         
    def Thaw(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(SunnyPanel, self).Thaw()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

class SunnyTree(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, pos = (30, -1), style = wx.TR_DEFAULT_STYLE|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.TR_HIDE_ROOT)
        self.SetInitialSize((100,80))

    def GetDataDict(self, itemId):
        datas = wx.TreeCtrl.GetItemData(self, itemId).GetData()
        dict  = {}
        for key in datas:
            dict[key] = datas[key]
        return dict

    def Freeze(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(SunnyTree, self).Freeze()
                         
    def Thaw(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(SunnyTree, self).Thaw()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

class SunnyFrame(wx.Frame):
    wildcard = "HTML Help project (*.hhp)|*.hhp|"     \
               "Compiled Python (*.html)|*.html|" \
               "SPAM files (*.htm)|*.htm|"    \
               "所有文件(*.*)|*.*".decode("utf-8")
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size = (970, 720),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetMinSize((640,480))
        self.Centre(wx.BOTH)
        self.SetIcon(IMG.Logo.GetIcon())
        self.Maximize(True)
        
        self._init_hh_env()
        self._init_attr_val()
        
        self._init_menu_bar()
        self._init_tool_bar()
        self._init_main_panel()
        
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

    def _init_hh_env(self):
        syspath = os.popen("echo %windir%").readlines()[0].strip("\n")
        dirname = "SysWOW64" if os.path.isdir(syspath + "/SysWOW64") else "System32"
        itircl  = GetAppPath() + '/ext/itircl.dll'
        itcc    = GetAppPath() + '/ext/itcc.dll'
        if not os.path.isfile(syspath + "/" + dirname + "/itircl.dll"):
            shutil.copy2(itircl, syspath + "/" + dirname + "/itircl.dll")
            os.popen("regsvr32 " + syspath + "/" + dirname + "/itircl.dll /s")
        if not os.path.isfile(syspath + "/" + dirname + "/itcc.dll"):
            shutil.copy2(itcc, syspath + "/" + dirname + "/itcc.dll")
            os.popen("regsvr32 " + syspath + "/" + dirname + "/itcc.dll /s")

    def _init_attr_val(self):
        self.dlg_find = None
        self.dlg_find_data = wx.FindReplaceData()
        self.dlg_find_data.SetFlags(wx.FR_DOWN)

        self._init_notebook_right_val()
        
    def _init_notebook_right_val(self):
        self.IsTreeToContents = False
        self.panel_hhp = None
        self.panel_hhc = None
        self.panel_hhk = None
        self.text_hhp  = None
        self.text_hhc  = None
        self.text_hhk  = None

        if hasattr(self, "file_hhp"):
            delattr(self, "file_hhp")

        if hasattr(self, "file_hhc"):
            delattr(self, "file_hhc")

        if hasattr(self, "file_hhk"):
            delattr(self, "file_hhk")

    def _recreate_tree(self, tree, content, type):
        if content == None:
            return
        else :
            content = content.decode("utf-8")
        pattern = re.compile(r'<ul>|<\/ul>|<li>.*?<\/object>', re.M|re.I|re.S)
        matched = re.findall(pattern, content)

        item_pat = re.compile(r'<param name="([a-z]+)" value="([^\"]*)">', re.M|re.I|re.S)
        parents  = []
        treelev  = -1

        tree.Freeze()
        tree.DeleteAllItems()
        #recreate it
        root_menu = tree.AddRoot("HiddenRoot")
        lastmenu = root_menu
        basepath = os.path.dirname(self.file_hhp) if hasattr(self, "file_hhp") else None
        for str in matched:
            if str.lower() == '<ul>':
                treelev += 1
                if len(parents) <= treelev:
                    parents.append(lastmenu)
                else:
                    parents[treelev] = lastmenu
            elif str.lower() == '</ul>':
                treelev -= 1
            else:
                items = re.findall(item_pat, str)
                datas = {"name":"", "local":"", "imagenumber":""}
                for item in items:
                    if datas.has_key(item[0].lower()):
                        datas[item[0].lower()] = item[1]
                image = 2
                if basepath != None and os.path.isfile((basepath + "/" + datas["local"]).replace("/.", "")):
                    image = 0
                lastmenu = tree.AppendItem(parents[treelev], datas["name"], image, data=wx.TreeItemData(datas))
                tree.SetItemImage(lastmenu, image+1, wx.TreeItemIcon_Selected)
        tree.Thaw()

    def _init_menu_bar(self):
        menuBar   = wx.MenuBar()
        menu_file = wx.Menu()
        menu_tool = wx.Menu()
        menu_help = wx.Menu()

        menuBar.Append(menu_file, _("File").decode('utf-8'))
        menuBar.Append(menu_tool, _('Tool').decode('utf-8'))
        menuBar.Append(menu_help, _('Help').decode('utf-8'))

        item_new = wx.MenuItem(menu_file, wx.ID_NEW, _('&New\tCtrl-N').decode('utf-8'))
        item_new.SetBitmap(wx.Bitmap('img/add.png'))

        item_open = wx.MenuItem(menu_file, wx.ID_OPEN, _('&Open\tCtrl-O').decode('utf-8'))
        item_open.SetBitmap(wx.Bitmap('img/open.png'))

        item_save = wx.MenuItem(menu_file, wx.ID_SAVE, _('&Save\tCtrl-S').decode('utf-8'))
        item_save.SetBitmap(wx.Bitmap('img/save.png'))

        item_quit = wx.MenuItem(menu_file, wx.ID_EXIT, _('E&xit\tCtrl-Q').decode('utf-8'))
        item_quit.SetBitmap(wx.Bitmap('img/quit.png'))

        menu_file.AppendItem(item_new)
        menu_file.AppendItem(item_open)
        menu_file.AppendItem(item_save)
        menu_file.AppendSeparator()
        menu_file.AppendItem(item_quit)

        item_find = wx.MenuItem(menu_tool, wx.ID_FIND, _('&Find\tCtrl-F').decode('utf-8'))
        item_find.SetBitmap(wx.Bitmap('img/find.png'))
        item_complie = wx.MenuItem(menu_tool, wx.ID_EXECUTE, _('Compile\tCtrl-R').decode('utf-8'))
        item_complie.SetBitmap(wx.Bitmap('img/complie.png'))
        
        menu_tool.AppendItem(item_find)
        menu_tool.AppendItem(item_complie)
        
        item_help = wx.MenuItem(menu_help, wx.ID_HELP, _('Help').decode('utf-8').decode('utf-8'))
        item_help.SetBitmap(wx.Bitmap('img/help.png'))
        item_donate = wx.MenuItem(menu_help, wx.ID_ANY, _('Donate').decode('utf-8').decode('utf-8'))
        item_donate.SetBitmap(wx.Bitmap('img/dollar.png'))
        item_about = wx.MenuItem(menu_help, wx.ID_ABOUT, _('About').decode('utf-8').decode('utf-8'))
        item_about.SetBitmap(wx.Bitmap('img/about.png'))
        
        menu_help.AppendItem(item_help)
        menu_help.AppendItem(item_donate)
        menu_help.AppendItem(item_about)

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnNew,     item_new)
        self.Bind(wx.EVT_MENU, self.OnOpen,    item_open)
        self.Bind(wx.EVT_MENU, self.OnSave,    item_save)
        self.Bind(wx.EVT_MENU, self.OnComplie, item_complie)
        self.Bind(wx.EVT_MENU, self.OnHelp,    item_help)
        self.Bind(wx.EVT_MENU, self.OnDonate,  item_donate)
        
        self.Bind(wx.EVT_MENU, self.OnShowFind, item_find)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnFindReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFindReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        self.Bind(wx.EVT_UPDATE_UI, self.OnFindUpdate, item_find)

        self.Bind(wx.EVT_MENU, self.OnAbout,   item_about)
        self.Bind(wx.EVT_MENU, self.OnQuit,    item_quit)


    def _init_tool_bar(self):
        tool_bar = self.CreateToolBar(style=wx.TB_FLAT | wx.TB_TEXT | wx.TB_HORZ_LAYOUT)
        tool_bar.AddLabelTool(wx.ID_NEW,  _('New').decode('utf-8'),  wx.Bitmap('img/add.png'))
        tool_bar.AddLabelTool(wx.ID_OPEN, _('Open').decode('utf-8'), wx.Bitmap('img/open.png'))
        tool_bar.AddLabelTool(wx.ID_SAVE, _('Save').decode('utf-8'), wx.Bitmap('img/save.png'))
        tool_bar.AddSeparator()
        tool_bar.AddLabelTool(wx.ID_EXECUTE, _('Compile').decode('utf-8'), wx.Bitmap('img/complie.png'))
        tool_bar.AddSeparator()
        tool_bar.AddLabelTool(wx.ID_EXIT, _('Quit').decode('utf-8'), wx.Bitmap('img/quit.png'))
        tool_bar.Realize()


    def _init_main_panel(self):
        self.panel_main     = panel_main = SunnyPanel(self)
        self.notebook_left  = wx.Notebook(panel_main, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
        self.notebook_right = wx.Notebook(panel_main, style=wx.CLIP_CHILDREN)
        self.SetNotebookImageList(self.notebook_right)
        self.log            = wx.TextCtrl(panel_main, -1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        wx.Log_SetActiveTarget(wx.LogTextCtrl(self.log)) # Set the wxWindows log target to be this textctrl

        #----------------------------------------------------------------------------
        #Menu panel
        panel_menu     = wx.Panel(self.notebook_left, -1, style=wx.CLIP_CHILDREN)
        self.notebook_left.AddPage(panel_menu, _('Contents').decode('utf-8'), imageId=0)
        panel_menu_btn = wx.Panel(panel_menu, -1, size = (30, -1), style=wx.CLIP_CHILDREN)
        bmpnames = ['add', 'left', 'right', 'up', 'down', 'del']
        height = 0
        for bmpname in bmpnames:
            bmp = wx.Image(opj("img/"+bmpname+".png")).ConvertToBitmap()
            btn = wx.BitmapButton(panel_menu_btn, -1, bmp, (-1, height), (bmp.GetWidth()+10, bmp.GetHeight()+10))
            self.Bind(wx.EVT_BUTTON, lambda evt,obj=bmpname,type='menu':self.OnTreeButtonClick(evt,obj,type), btn)
            height +=  bmp.GetHeight() + 15
        self.tree_menu = SunnyTree(panel_menu)
        self.SetTreeImageList(self.tree_menu)
        box_menu = wx.BoxSizer(wx.HORIZONTAL)
        box_menu.Add(panel_menu_btn, 0)
        box_menu.Add(self.tree_menu, 1, wx.EXPAND)
        if 'wxMac' in wx.PlatformInfo:
            box_menu.Add((5,5))  # Make sure there is room for the focus ring
        panel_menu.SetSizer(box_menu)

        #-----------------------------------------------------------------------
        #Index panel
        panel_index = wx.Panel(self.notebook_left, -1, style=wx.CLIP_CHILDREN)
        self.notebook_left.AddPage(panel_index, _('Index').decode('utf-8'), imageId=0)
        
        panel_index_btn = wx.Panel(panel_index, -1, size = (30, -1), style=wx.CLIP_CHILDREN)
        bmpnames = ['add', 'left', 'right', 'up', 'down', 'del']
        height = 0
        for bmpname in bmpnames:
            bmp = wx.Image(opj("img/"+bmpname+".png")).ConvertToBitmap()
            btn = wx.BitmapButton(panel_index_btn, -1, bmp, (-1, height), (bmp.GetWidth()+10, bmp.GetHeight()+10))
            self.Bind(wx.EVT_BUTTON, lambda evt,obj=bmpname,type='index':self.OnTreeButtonClick(evt,obj,type), btn)
            height +=  bmp.GetHeight()+15

        self.tree_index = tree_index = SunnyTree(panel_index)
        self.SetTreeImageList(self.tree_index)
        root_index = self.tree_index.AddRoot("IndexRoot")
        
        box_index = wx.BoxSizer(wx.HORIZONTAL)
        box_index.Add(panel_index_btn, 0)
        box_index.Add(self.tree_index, 1, wx.EXPAND)
        if 'wxMac' in wx.PlatformInfo:
            box_index.Add((5,5))  # Make sure there is room for the focus ring
        panel_index.SetSizer(box_index)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged, self.notebook_left)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged, self.notebook_right)

        # Use the aui manager to set up everything
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(panel_main)
        self.mgr.AddPane(self.notebook_right, wx.aui.AuiPaneInfo().CenterPane().Name("DocumentWindow"))
        self.mgr.AddPane(self.notebook_left,
                         wx.aui.AuiPaneInfo().
                         Left().Layer(2).BestSize((280, -1)).
                         MinSize((280, -1)).
                         CaptionVisible(False).
                         Name("MenuIndexWindow"))
        self.mgr.AddPane(self.log,
                         wx.aui.AuiPaneInfo().
                         Bottom().BestSize((-1, 150)).
                         MinSize((-1, 140)).
                         Floatable(CFG.AllowAuiFloating).FloatingSize((500, 160)).
                         Caption(_("System Logs").decode("utf-8")).
                         #CloseButton(False).
                         Name("LogWindow"))

        self.mgr.Update()
        self.mgr.SetFlags(self.mgr.GetFlags() ^ wx.aui.AUI_MGR_TRANSPARENT_DRAG)

    def _load_page_hhp(self, content, imageId = 1):
        self.panel_hhp, self.text_hhp = self._load_page(self.notebook_right, 
                                                        self.panel_hhp, self.text_hhp, _('Project file').decode('utf-8'), content, 'hhp', imageId)

    def _load_page_hhc(self, content, imageId = 1):
        self.panel_hhc, self.text_hhc = self._load_page(self.notebook_right,  
                                                        self.panel_hhc, self.text_hhc, _('Contents file').decode('utf-8'), content, 'hhc', imageId)

    def _load_page_hhk(self, content, imageId = 1):
        self.panel_hhk, self.text_hhk = self._load_page(self.notebook_right,  
                                                        self.panel_hhk, self.text_hhk, _('Index file').decode('utf-8'), content, 'hhk', imageId)

    def _load_page(self, notebook, panel, textctrl, title, content, type, imageId):
        if content == None:
            return panel, textctrl

        if panel == None:
            panel = wx.Panel(notebook, -1, style=wx.CLIP_CHILDREN)
            textctrl = wx.TextCtrl(panel, -1, style =
                             wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH2 | wx.TE_NOHIDESEL)
            self.Bind(wx.EVT_TEXT, lambda evt,textctrl=textctrl,type=type:self.OnContentsChange(evt,textctrl,type, 1), textctrl)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(textctrl, 1, wx.EXPAND)
            panel.SetSizer(sizer)
        else:
            pass
        SetTextctrlValue(textctrl, content)
        notebook.AddPage(panel, title, imageId=imageId)
        return panel, textctrl

    def SetHhpFileName(self, path):
        self.file_hhp = path
        return self.file_hhp

    def SetHhcFileName(self, content):
        pattern = re.compile(r'Contents\s+file\=(.*?\.hhc)', re.M|re.I)
        matched = re.findall(pattern, content)
        self.file_hhc = matched[0]
        return self.file_hhc

    def SetHhkFileName(self, content):
        pattern  = re.compile(r'Index\s+file\=(.*?\.hhk)', re.M|re.I)
        matched = re.findall(pattern, content)
        self.file_hhk = matched[0]
        return self.file_hhk

    def GetAllFiles(self, content):
        pattern  = re.compile(r'\n([^\=\n]*?\.(?:html|htm))', re.M|re.I)
        file_all = re.findall(pattern, content)
        return file_all
        
    def SetTreeImageList(self, tree):
        imgList = wx.ImageList(16, 16)
        for png in ['help', 'flag', 'unlink', 'redflag']:
            imgList.Add(wx.Image(opj("img/"+png+".png")).ConvertToBitmap())
        tree.AssignImageList(imgList)

    def SetNotebookImageList(self, notebook):
        imgList = wx.ImageList(16, 16)
        for png in ['save', 'edit']:
            imgList.Add(wx.Image(opj("img/"+png+".png")).ConvertToBitmap())
        notebook.AssignImageList(imgList)

    def ShowTip(self):
        config = GetConfig()
        showTipText = config.Read("tips")
        showTip, index = eval(showTipText) if showTipText else (1, 0)

        if showTip:
            tp = wx.CreateFileTipProvider(opj("data/tips.txt"), index)
            showTip = wx.ShowTip(self, tp)
            index = tp.GetCurrentTip()
            config.Write("tips", str( (showTip, index) ))
            config.Flush()

    def ShowMsg(self, msg = "Message", title = "Tips", style = wx.OK | wx.ICON_INFORMATION):
        dlg = wx.MessageDialog(self, msg, title, style)
        result = dlg.ShowModal()
        dlg.Destroy()
        return result

    def IsSaved(self):
        pageCount = self.notebook_right.GetPageCount()
        if pageCount > 0:
            for i in range(pageCount):
                if self.notebook_right.GetPageImage(i) == 1:
                    return False
        return True
        
    def RemoveNotebookRightAllPages(self):
        self.RemoveAllPages(self.notebook_right)
        self._init_notebook_right_val()
        self.log.SetValue('')

    def RemoveAllPages(self, notebook):
        notebook.DeleteAllPages()

    def CreateHhpContents(self, files = ["sunny.html"]):
        filelist = ''
        _addlist = []
        for file in files:
            if file in _addlist:
                continue
            filelist += file + "\n"
            _addlist.append(file)
        if hasattr(self, "file_hhp"): #append file
            content_hhp = self.text_hhp.GetValue()
            existFiles  = self.GetAllFiles(content_hhp)
            existlist   = ''
            for file in existFiles:
                if file in _addlist:
                    continue
                existlist += file + "\n"
                _addlist.append(file)

            content_hhp = re.sub(r'\n([^\=\n]*?\.(?:html|htm))', "\n" + existlist + filelist, content_hhp, re.M|re.I)
        else:
            content_hhp = CFG.template_hhp.decode("utf-8")
            content_hhp = content_hhp.replace('{__compiled_file__}', "sunny.chm")\
                                     .replace('{__contents_file__}', "sunny.hhc")\
                                     .replace('{__default_topic__}', "sunny.html")\
                                     .replace('{__index_file__}', "sunny.hhk")\
                                     .replace('{__filelist__}', filelist)
        return content_hhp

    def ConvertDatasToHTML(self, datas, unit, tabs = ''):
        html = ''
        for data in datas:
            _unit = unit.replace("{__name__}", data['name']).replace("{__local__}", data['local']).replace("{__imagenumber__}", data['imagenumber'])
            html += tabs + re.sub(r'\n', lambda m,t=tabs:m.group(0)+t, _unit, 0).rstrip("\t")
            if data.has_key("children"):
                html += '\n' + tabs + '<UL>' + self.ConvertDatasToHTML(data['children'], unit, tabs + '\t') + tabs + '</UL>\n'
        return html
        
    def CreateHhcContents(self, files = ["sunny.html"], datas = None):
        unit_hhc = CFG.template_hhc_unit.decode("utf-8")
        if datas == None:
            datas = []
            for file in files:
                datas.append({"name":file.replace(".html", "").replace(".htm", ""), "local":"./" + file, "imagenumber":"1"})
        hhc_list = self.ConvertDatasToHTML(datas, unit_hhc)

        content_hhc = CFG.template_hhc.decode("utf-8")
        content_hhc = content_hhc.replace('{__image_type__}', "Folder")\
                                 .replace('{__hhc_list__}', hhc_list)
        return content_hhc

    def CreateHhkContents(self, files = ["sunny.html"], datas = None):
        hhk_list = ''
        unit_hhk = CFG.template_hhk_unit.decode("utf-8")
        if datas == None:
            datas = []
            for file in files:
                datas.append({"name":file.replace(".html", "").replace(".htm", ""), "local":"./" + file, "imagenumber":"1"})
        hhk_list = self.ConvertDatasToHTML(datas, unit_hhk)

        content_hhk = CFG.template_hhk.decode("utf-8")
        content_hhk = content_hhk.replace('{__image_type__}', "Folder")\
                                 .replace('{__hhk_list__}', hhk_list)
        return content_hhk

    def MoveItemToLeft(self, tree, selItem):
        parent = tree.GetItemParent(selItem)
        if not tree.IsVisible(parent): #root item
            return
        datas    = tree.GetDataDict(selItem)
        image    = tree.GetItemImage(selItem)
        newItem  = tree.InsertItem(tree.GetItemParent(parent), parent, datas["name"], image, data=wx.TreeItemData(datas))
        tree.SetItemImage(newItem, image+1, wx.TreeItemIcon_Selected)
        nextItem = tree.GetNextSibling(selItem)
        while nextItem:
            nextNextItem = tree.GetNextSibling(nextItem)
            datas        = tree.GetDataDict(nextItem)
            image        = tree.GetItemImage(nextItem)
            subItem      = tree.AppendItem(newItem, datas["name"], image, data=wx.TreeItemData(datas))
            tree.SetItemImage(subItem, image+1, wx.TreeItemIcon_Selected)
            CopyTree(tree, nextItem, subItem)
            tree.Delete(nextItem)
            nextItem = nextNextItem

        tree.Delete(selItem)
        tree.SelectItem(newItem)
        tree.ExpandAllChildren(newItem)
        tree.EnsureVisible(newItem)

    def MoveItemToRight(self, tree, selItem):
        parent = tree.GetPrevSibling(selItem)
        if not parent:
            return
        datas   = tree.GetDataDict(selItem)
        image   = tree.GetItemImage(selItem)
        newItem = tree.AppendItem(parent, datas["name"], image, data=wx.TreeItemData(datas))
        tree.SetItemImage(newItem, image+1, wx.TreeItemIcon_Selected)
        CopyTree(tree, selItem, newItem)

        tree.Delete(selItem)
        tree.SelectItem(newItem)
        tree.ExpandAllChildren(newItem)
        tree.EnsureVisible(newItem)

    def MoveItemToUp(self, tree, selItem):
        prvItem = tree.GetPrevSibling(selItem)
        if not prvItem:
            return
        datas   = tree.GetDataDict(prvItem)
        image   = tree.GetItemImage(prvItem)
        newItem = tree.InsertItem(tree.GetItemParent(selItem), selItem, datas["name"], image, data=wx.TreeItemData(datas))
        tree.SetItemImage(newItem, image+1, wx.TreeItemIcon_Selected)
        CopyTree(tree, prvItem, newItem)
        tree.Delete(prvItem)
        tree.EnsureVisible(selItem)

    def MoveItemToDown(self, tree, selItem):
        nxtItem = tree.GetNextSibling(selItem)
        if not nxtItem:
            return
        datas   = tree.GetDataDict(selItem)
        image   = tree.GetItemImage(selItem)
        newItem = tree.InsertItem(tree.GetItemParent(nxtItem), nxtItem, datas["name"], image, data=wx.TreeItemData(datas))
        tree.SetItemImage(newItem, image+1, wx.TreeItemIcon_Selected)
        CopyTree(tree, selItem, newItem)
        tree.Delete(selItem)
        tree.SelectItem(newItem)
        tree.ExpandAllChildren(newItem)
        tree.EnsureVisible(selItem)

    def OnContentsChange(self, evt, textctrl, type, imageId):
        pageCount = self.notebook_right.GetPageCount()
        if type == 'hhc':
            if not self.IsTreeToContents:
                self._recreate_tree(self.tree_menu, textctrl.GetValue(), type)
                ExpandTree(self.tree_menu)
            if pageCount == 3:
                self.notebook_right.SetPageImage(1, imageId)
        elif type == 'hhk':
            if not self.IsTreeToContents:
                self._recreate_tree(self.tree_index, textctrl.GetValue(), type)
                ExpandTree(self.tree_index)
            if pageCount == 3:
                self.notebook_right.SetPageImage(2, imageId)
        else:
            if pageCount == 3:
                self.notebook_right.SetPageImage(0, imageId)
    
    def OnTreeButtonClick(self, evt, btn, type):
        if self.notebook_right.GetPageCount() == 0:
            self.log.AppendText(_("Operation failed, project does not exist\n").decode("utf-8"))
            return

        if type == "menu":
            tree = self.tree_menu
        elif type == "index":
            tree = self.tree_index
        else:
            self.log.AppendText(_("Operation failed, invalid parameter\n").decode("utf-8"))
            return

        selItem = tree.GetSelection()
        if btn != 'add' and not selItem:
            self.log.AppendText(_("Operation failed, item unselected!\n").decode("utf-8"))
            return

        allfiles = []
        if btn == 'add':
            if not hasattr(self, "file_hhp"):
                self.ShowMsg(_("Project not saved!\nYou must first save it.").decode("utf-8"), _("Tips").decode("utf-8"))
                return

            defaultDir = GetAppPath()+'/chm/sunny' if GetAppPath() == os.getcwd() else os.getcwd()
            dlg = wx.FileDialog(self, message = _("Add tree node").decode("utf-8"), defaultDir = defaultDir, defaultFile = "", style = wx.OPEN | wx.CHANGE_DIR | wx.MULTIPLE,
                                wildcard = "HTML file (*.html)|*.html|HTML file (*.htm)|*.htm")
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                for _path in paths:
                    filename = _path.replace(os.getcwd(), '')[1:]
                    allfiles.append(filename)
                    datas    = {"name":os.path.basename(_path).replace(".html",'').replace(".htm",''), 
                                "local":'./' + filename, "imagenumber":"1"}
                    basepath = os.path.dirname(self.file_hhp) if hasattr(self, "file_hhp") else None
                    filepath = (basepath + "/" + datas["local"]).replace("/.", "")
                    image    = 0 if os.path.isfile(filepath) else 2
                    if not selItem:
                        selItem = tree.GetLastChild(tree.GetRootItem())
                    if selItem:
                        newItem = tree.InsertItem(tree.GetItemParent(selItem), selItem, datas["name"], image, data=wx.TreeItemData(datas))
                    else:
                        newItem = tree.AppendItem(tree.GetRootItem(), datas["name"], image, data=wx.TreeItemData(datas))
                    tree.SetItemImage(newItem, image+1, wx.TreeItemIcon_Selected)
                    selItem = newItem
                tree.SelectItem(selItem)

            dlg.Destroy()
        elif btn == 'left':
            self.MoveItemToLeft(tree, selItem)
        elif btn == 'right':
            self.MoveItemToRight(tree, selItem)
        elif btn == 'up':
            self.MoveItemToUp(tree, selItem)
        elif btn == 'down':
            self.MoveItemToDown(tree, selItem)
        elif btn == 'del':
            tree.Delete(selItem)
        else:
            pass

        #update content
        self.IsTreeToContents = True
        if type == "menu":
            SetTextctrlValue(self.text_hhc, self.CreateHhcContents(datas = ConvertTreeToDatas(tree)))
        else: #type == "index":
            SetTextctrlValue(self.text_hhk, self.CreateHhkContents(datas = ConvertTreeToDatas(tree)))
        SetTextctrlValue(self.text_hhp, self.CreateHhpContents(allfiles))
        self.IsTreeToContents = False
        self.OnNotebookPageChanged(None, self.notebook_left)

    def OnNotebookPageChanged(self, evt, notebook = None):
        if notebook == None:
            notebook = evt.GetEventObject()
        if notebook.GetPageCount() == 2: #left
            if self.notebook_right.GetPageCount() > 0:
                self.notebook_right.SetSelection(notebook.GetSelection()+1)
        else: #right
            page = notebook.GetSelection()
            if page > 0:
                self.notebook_left.SetSelection(page - 1)

    def OnNew(self, evt):
        if not self.IsSaved():
            result = self.ShowMsg(_("Project not saved!\nAre you sure you want to discard?").decode("utf-8"), 
                          _("Warning").decode("utf-8"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if result == wx.ID_NO:
                return
        self.RemoveNotebookRightAllPages()
        content_hhp = self.CreateHhpContents()
        content_hhc = self.CreateHhcContents()
        content_hhk = self.CreateHhkContents()

        self._load_page_hhp(content_hhp) #hhp page
        self._load_page_hhc(content_hhc) #hhc page
        self._load_page_hhk(content_hhk) #hhk page

    def OnOpen(self, evt):
        if not self.IsSaved():
            result = self.ShowMsg(_("Project not saved!\nAre you sure you want to discard?").decode("utf-8"), 
                          _("Warning").decode("utf-8"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if result == wx.ID_NO:
                return

        # Create the dialog
        defaultDir = GetAppPath()+'/chm/sunny' if GetAppPath() == os.getcwd() else os.getcwd()
        if not os.path.isdir(defaultDir):
            os.makedirs(defaultDir)
        dlg = wx.FileDialog(self, message = _("Open project").decode("utf-8"), defaultDir = defaultDir, defaultFile = "", style = wx.OPEN | wx.CHANGE_DIR,
                            wildcard = "HTML Help project (*.hhp)|*.hhp")

        # Show the dialog and retrieve the user response. If it is the OK response, process the data.
        if dlg.ShowModal() == wx.ID_OK:
            self.RemoveNotebookRightAllPages()
            file_hhp = self.SetHhpFileName(dlg.GetPath())
            try:
                content_hhp = FileGetContents(file_hhp)
                self.log.AppendText(_('Open file: %s\n').decode("utf-8") % file_hhp)
            except:
                content_hhp = None
                delattr(self, "file_hhp")
                self.log.AppendText(_('Open file failed: %s\n').decode("utf-8") % file_hhp)

            if content_hhp != None:
                allfiles = self.GetAllFiles(content_hhp)
                self._load_page_hhp(content_hhp, 0) #hhp page

                #Try to read contents file content
                try:
                    file_hhc = os.path.dirname(file_hhp) + '/' + self.SetHhcFileName(content_hhp)
                    content_hhc = FileGetContents(file_hhc)
                except:
                    content_hhc = self.CreateHhcContents(allfiles)
                self._load_page_hhc(content_hhc, 0) #hhc page

                #try to read index file content
                try:
                    file_hhk = os.path.dirname(file_hhp) + '/' + self.SetHhkFileName(content_hhp)
                    content_hhk = FileGetContents(file_hhk)
                except:
                    content_hhk = self.CreateHhkContents(allfiles)

                self._load_page_hhk(content_hhk, 0) #hhk page

        # Destroy the dialog. Don't do this until you are done with it! BAD things can happen otherwise!
        dlg.Destroy()


    def OnSave(self, evt):
        if self.notebook_right.GetPageCount() > 0:
            if not hasattr(self, "file_hhp"):
                defaultDir = GetAppPath()+'/chm/sunny' if GetAppPath() == os.getcwd() else os.getcwd()
                if not os.path.isdir(defaultDir):
                    os.makedirs(defaultDir)
                dlg = wx.FileDialog(self, message = _("Save file as ...").decode("utf-8"), defaultDir = defaultDir, 
                                    defaultFile = "sunny", wildcard = "HTML Help project (*.hhp)|*.hhp", style=wx.SAVE | wx.CHANGE_DIR)

                # Show the dialog and retrieve the user response.
                if dlg.ShowModal() == wx.ID_OK:
                    self.file_hhp = dlg.GetPath()
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return

            FilePutContents(self.file_hhp, self.text_hhp.GetValue())
            basepath = os.path.dirname(self.file_hhp) if hasattr(self, "file_hhp") else None
            html_tpl = CFG.template_html
            for file in self.GetAllFiles(self.text_hhp.GetValue()):
                filepath = (basepath + "/" + file).replace("/.", "")
                if not os.path.isfile(filepath):
                    title = file.replace(".html", '').replace(".htm", '')
                    FilePutContents(filepath, html_tpl.replace("{__title__}", title).replace("{__content__}", file))
            self.OnContentsChange(None, self.text_hhp, 'hhp', 0)
            self.OnContentsChange(None, self.text_hhc, 'hhc', 0)
            self.OnContentsChange(None, self.text_hhk, 'hhk', 0)
            try:
                file_hhc = os.path.dirname(self.file_hhp) + '/' + self.SetHhcFileName(self.text_hhp.GetValue())
                FilePutContents(file_hhc, self.text_hhc.GetValue())
            except:
                self.ShowMsg(_("Save file failed: %s").decode("utf-8") % file_hhc, _("Tips").decode("utf-8"))

            try:
                file_hhk = os.path.dirname(self.file_hhp) + '/' + self.SetHhkFileName(self.text_hhp.GetValue())
                FilePutContents(file_hhk, self.text_hhk.GetValue())
            except:
                self.ShowMsg(_("Save file failed: %s").decode("utf-8") % file_hhk, _("Tips").decode("utf-8"))
        else:
            self.log.AppendText(_("Save failed, project does not exist\n").decode("utf-8"))

    def OnComplie(self, evt):
        if hasattr(self, "file_hhp"):
            self.log.AppendText(_("\n### Complie starting ... ###\n").decode("utf-8"))
            try:
                if not hasattr(self, "process_complie"):
                    self.process_complie = wx.Process(self)
                    self.process_complie.Redirect()
                    self.process_complie.Bind(wx.EVT_END_PROCESS, self.OnEndComplie)
                cmd = (GetAppPath() + '/ext/hhc.exe').decode('gbk')
                self.Enable(False)
                self.GetToolBar().Enable(False)
                wx.Execute(('"%s" "%s"' % (cmd, self.file_hhp)).decode("utf-8"), wx.EXEC_ASYNC, self.process_complie)
            except:
                self.OnEndComplie(None)
            
        else:
            if self.notebook_right.GetPageCount() > 0:
                self.ShowMsg(_("Please save the file before compilation").decode("utf-8"), _("Tips").decode("utf-8"))
            else:
                self.log.AppendText(_("Compilation failed, project does not exist\n").decode("utf-8"))

    def OnEndComplie(self, evt):
        try:
            stream = self.process_complie.GetInputStream()
            if stream.CanRead():
                self.log.AppendText(re.sub(r"[\n\r]+", '\n', "\n%s\n" % stream.read()))
        except:
            pass
        self.log.AppendText(_("\n### Complie is done ... ###\n\n").decode("utf-8"))
        self.Enable(True)
        self.GetToolBar().Enable(True)

    def OnHelp(self, evt):
        helpfile = GetAppPath() + '/data/sunny.chm'
        if not os.path.isfile(helpfile):
            FilePutContents(helpfile, base64.b64decode(CFG.sunnychm_chm.strip("\n")), "wb")
        cmd = GetAppPath() + '/ext/hh.exe'
        wx.Execute('"%s" "%s"' % (cmd, helpfile))

    def OnDonate(self, evt):
        dlg = wx.Dialog(self, -1, _('Donate').decode('utf-8').decode('utf-8'), 
                        size=(500, 308), pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnScreen()
        dlg.SetBackgroundColour('#f8fcf8')
        wx.StaticBitmap(dlg, -1, IMG.Wechat.GetBitmap(), (24,  0))
        wx.StaticBitmap(dlg, -1, IMG.Alipay.GetBitmap(), (270, 0))
        dlg.ShowModal()
        dlg.Destroy()

    def OnShowFind(self, evt):
        if self.notebook_right.GetPageCount() <1 or self.dlg_find != None:
            return
        page = self.notebook_right.GetSelection()
        if page == 1:
            textctrl = self.text_hhc
        elif page == 2:
            textctrl = self.text_hhk
        else:
            textctrl = self.text_hhp

        start, end = textctrl.GetSelection()
        self.dlg_find_data.SetFindString(textctrl.GetRange(start, end))
        self.dlg_find = wx.FindReplaceDialog(self, self.dlg_find_data, _("Find & Replace").decode("utf-8"),
                        wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD | wx.FR_REPLACEDIALOG)
        self.dlg_find.Show(True)


    def OnFindUpdate(self, evt):
        evt.Enable(self.dlg_find == None)


    def OnFind(self, evt, IsReplace = False):
        page = self.notebook_right.GetSelection()
        if page == 1:
            textctrl = self.text_hhc
        elif page == 2:
            textctrl = self.text_hhk
        else:
            textctrl = self.text_hhp
            self.notebook_right.SetSelection(0)

        end = textctrl.GetLastPosition()
        textstring = textctrl.GetRange(0, end).lower()
        findstring = self.dlg_find_data.GetFindString().lower()
        backward = not (self.dlg_find_data.GetFlags() & wx.FR_DOWN)
        if backward:
            start = textctrl.GetSelection()[0]
            loc = textstring.rfind(findstring, 0, start)
        else:
            start = textctrl.GetSelection()[1]
            loc = textstring.find(findstring, start)
        if loc == -1 and start != 0:
            # string not found, start at beginning
            if backward:
                start = end
                loc = textstring.rfind(findstring, 0, start)
            else:
                start = 0
                loc = textstring.find(findstring, start)
        if loc == -1 and not IsReplace:
            self.dlg_find.Hide()
            self.ShowMsg( _("Find String Not Found").decode("utf-8"), _("Tips").decode("utf-8"))
            self.dlg_find.Show(True)
        if self.dlg_find:
            if loc == -1:
                self.dlg_find.SetFocus()
                return
            else:
                pass

        textctrl.ShowPosition(loc)
        textctrl.SetSelection(loc, loc + len(findstring))

    def OnFindReplace(self, evt):
        page = self.notebook_right.GetSelection()
        if page == 1:
            textctrl = self.text_hhc
        elif page == 2:
            textctrl = self.text_hhk
        else:
            textctrl = self.text_hhp
            self.notebook_right.SetSelection(0)
        start, end = textctrl.GetSelection()
        if start == end:
            self.OnFind(evt, True)
        else:
            textctrl.WriteText(evt.GetReplaceString())

    def OnFindReplaceAll(self, evt):
        page = self.notebook_right.GetSelection()
        if page == 1:
            textctrl = self.text_hhc
        elif page == 2:
            textctrl = self.text_hhk
        else:
            textctrl = self.text_hhp
            self.notebook_right.SetSelection(0)
        
        textctrl.SetSelection(0, 0)
        while True:
            self.OnFind(evt, True)
            start, end = textctrl.GetSelection()
            if start == end:
                break
            else:
                textctrl.WriteText(evt.GetReplaceString())

    def OnFindClose(self, evt):
        evt.GetDialog().Destroy()
        self.dlg_find = None

    def OnAbout(self, evt):
        dlg = wx.AboutDialogInfo()
        dlg.SetIcon(IMG.Empty.GetIcon())
        dlg.SetName(CFG.AppName)
        dlg.SetVersion(CFG.Version)
        dlg.SetDescription("最新版本获取: \t\t".decode('utf-8'))
        dlg.WebSite = ("https://github.com/uniqid/sunnychm", "SunnyCHM on GitHub")
        year = int(datetime.now().strftime("%Y"), 10)
        copyright = ('(c)2016' if year <= 2016 else '(c)2016-'+ year) + " Jacky Yu, All rights reserved    "
        dlg.SetCopyright(copyright.decode('utf-8'))
        dlg.Developers = ["Jacky Yu <jacky325@qq.com>".decode('utf-8')]
        dlg.SetLicence(CFG.AppName + " is a freeware".decode('utf-8'))
        wx.AboutBox(dlg)

    def OnQuit(self, evt):
        if not self.IsSaved():
            result = self.ShowMsg(_("Project not saved!\nAre you sure you want to quit?").decode("utf-8"), 
                          _("Warning").decode("utf-8"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if result == wx.ID_NO:
                return

        self.mgr.UnInit()
        self.Destroy()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

def main():
    try:
        gettext.translation(CFG.AppName, "./locale", languages=['cn']).install()
        os.chdir(GetAppPath())
        reload(sys)
        sys.setdefaultencoding("utf-8")
    except:
        pass
    app = SunnyApp(False)
    app.MainLoop()

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
if __name__ == '__main__':
    main()

