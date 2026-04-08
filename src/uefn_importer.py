# yea yea the imports. so many imports. but it is what it is.
# i added little to no comments in the code itself because i think the UI is self explanatory enough and the code is a bit of a mess, but if you have any questions feel free to ask me on twitter @itsmarwanuefn or open an issue on github.
# so yea heres the code for the project. use it as you will but i dont think this will get far. ppl with less experience might find it useful but for someone who has been in the uefn community for a while this is pretty basic stuff.
# but please dont sell this. im not asking for money but it would be really disappointing to see someone else make a quick buck off of this without putting in the work themselves. if you want to support me, consider buying me a coffee or sharing this project with someone who might find it useful. thanks :)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, sys, json, shutil, zipfile, tempfile, threading, webbrowser, re, ctypes

def resource_pth(rel_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

# you shouldnt be able to see these comments in the compiled version but im leaving them here for anyone who looks at the source code. also for myself in case i forget why i did certain things XD
# also im really sorry for the code quality. i usually write quick and dirty scripts but this one got out of hand really fast ngl. i might clean it up in the future but for now it works and thats good enough for me
# check out uefndevkit.rweb.site. yes shameless plug but i have to get some use out of it after all the work i put into it.
# also follow me on twitter @itsmarwanuefn for updates and other cool projects im working on :)


#  Optional drag-and-drop support
#  If tkinterdnd2 is installed the window class is swapped to TkinterDnD.Tk
#  so the drop_target_register call actually works. If it's not installed
#  the app runs fine without drag-and-drop somehow.
#  man i dont know why i do this to myself but i really wanted drag and drop support and tkinterdnd2 is the only option that doesnt require a custom build of python, so here we are

try:
    from tkinterdnd2 import TkinterDnD as _TkDnD
    DND_READY = True
    BaseWin = _TkDnD.Tk
except ImportError:
    DND_READY = False
    BaseWin = tk.Tk

def get_def_cfg():
    b = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(b, "config.json")

def fetchConfig(pth=None):
    pth = pth or get_def_cfg()
    def_vals = {
        'uefn_project_dir': "",
        'warn_unsupported': True,
        'theme': 'system',
        'config_location': pth,
    }
    if os.path.isfile(pth):
        try:
            with open(pth, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            for k, v in def_vals.items(): file_data.setdefault(k, v)
            return file_data
        except Exception as e:
            print("cfg err:", e)
    return def_vals


def write_cfg_to_disk(cfgObj):
    p = cfgObj.get('config_location') or get_def_cfg()
    try:
        parent_dir = os.path.dirname(os.path.abspath(p))
        if parent_dir: os.makedirs(parent_dir, exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f: json.dump(cfgObj, f, indent=2)
        return True
    except Exception as err:
        messagebox.showerror('Config Error', f"Could not save config:\n{err}")
        return False

# colors. i want to cry. took me way too long to get these right. also the theme system is really jank ngl but it works so who cares
THEME_COLORS = {
    'dark': {
        'bg': '#1e1e1e', 'surface': '#252526', 'surface2': '#333333',
        'accent': '#007acc', 'accent_dim': '#005999', 'text': '#f0f0f0',
        'text_dim': '#9e9e9e', 'border': '#444444', 'success': '#4caf50',
        'warning': '#ff9800', 'danger': '#f44336', 'entry_bg': '#2d2d2d',
        'entry_fg': '#ffffff', 'btn_fg': '#ffffff'
    },
    'light': {
        'bg': '#f1f4fb', 'surface': '#ffffff', 'surface2': '#e6eaf5',
        'accent': '#3561d4', 'accent_dim': '#1e3d9e', 'text': '#181c30',
        'text_dim': '#636880', 'border': '#ced3e8', 'success': '#1a9e6a',
        'warning': '#c97a10', 'danger': '#cc2222', 'entry_bg': '#ffffff',
        'entry_fg': '#181c30', 'btn_fg': '#ffffff'
    }
}

# should work 
def getSystem_Theme(nm):
    if nm == 'system':
        try:
            import winreg
            rKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            val, _ = winreg.QueryValueEx(rKey, "AppsUseLightTheme")
            return 'light' if val else 'dark'
        except Exception: pass
        return 'dark'
    return nm if nm in THEME_COLORS else 'dark'

# valid file formats that the program accepts. if i find any other extensions other than these ill add them here.
ALLOWED_EXTENSIONS = {'.uasset', '.umap'}

def find_bad_exts(root_pth):
    bads = []
    for d, _, files_list in os.walk(root_pth):
        for file_name in files_list:
            if os.path.splitext(file_name)[1].lower() not in ALLOWED_EXTENSIONS:
                bads.append(os.path.relpath(os.path.join(d, file_name), root_pth))
    return bads

def unzip_it(zipFilePth, dest_folder):
    with zipfile.ZipFile(zipFilePth, 'r') as zfile: zfile.extractall(dest_folder)

class CustomToggle(tk.Canvas):
    W, H, R = 40, 22, 9
    def __init__(self, prnt, var, clrs, **kw):
        super().__init__(prnt, width=self.W, height=self.H, highlightthickness=0, bd=0, **kw)
        self.myVar = var; self.clrs = clrs
        self.myVar.trace_add('write', lambda *_: self.render())
        self.bind('<Button-1>', self.doToggle)
        self.render()

    def render(self):
        c = self.clrs
        is_on = bool(self.myVar.get())
        trk_clr = c['accent'] if is_on else c['border']
        knob_x = self.W - self.R - 3 if is_on else self.R + 3
        self.delete('all')
        self.create_oval(0, 1, self.H - 2, self.H - 1, fill=trk_clr, outline="")
        self.create_oval(self.W - self.H + 2, 1, self.W, self.H - 1, fill=trk_clr, outline="")
        self.create_rectangle(self.H // 2, 1, self.W - self.H // 2, self.H - 1, fill=trk_clr, outline="")
        self.create_oval(knob_x - self.R + 2, 3, knob_x + self.R - 2, self.H - 3, fill='#ffffff', outline="")

    def updateColors(self, new_clrs):
        self.clrs = new_clrs; self.render()

    def doToggle(self, _=None):
        self.myVar.set(not bool(self.myVar.get()))

class CustomRadio(tk.Frame):
    def __init__(self, p_root, opts_list, myVar, clrs, **kw):
        super().__init__(p_root, bg=clrs['bg'], **kw)
        self.myVar = myVar
        self.clrs = clrs
        self.btn_map = {}
        for v_val, lbl_str in opts_list:
            b = tk.Label(self, text=lbl_str, cursor='hand2', font=('Segoe UI', 9), padx=14, pady=6, relief='flat')
            b.pack(side='left', padx=(0, 6))
            b.bind('<Button-1>', lambda e, val=v_val: self.clickAction(val))
            self.btn_map[v_val] = b
        self.myVar.trace_add('write', lambda *_: self.reDraw())
        self.reDraw()

    def clickAction(self, val): self.myVar.set(val)

    def reDraw(self):
        c = self.clrs
        current = self.myVar.get()
        for v_val, btn in self.btn_map.items():
            if v_val == current: btn.configure(bg=c['accent'], fg=c['btn_fg'])
            else: btn.configure(bg=c['surface2'], fg=c['text_dim'])

    def updateColors(self, clrs):
        self.clrs = clrs
        self.configure(bg=clrs['bg'])
        self.reDraw()

class App(BaseWin):

    def __init__(self):
        super().__init__()
        
        try:
            myappid = 'itsmarwan.uefn_importer.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception: pass
        
        self.myCfg = fetchConfig()
        self.current_theme = getSystem_Theme(self.myCfg.get('theme', 'system'))
        self.clr = THEME_COLORS[self.current_theme]

        self.title('UEFN Asset Importer')
        # the window's width and height. these control how big the window should be. this isnt changeable by the user for now
        self.geometry('800x800')
        self.minsize(700, 520)
        self.resizable(True, True)

        self.sel_pth = None
        self.tmp_folder_dir = None
        self.tog_list = []
        self.radio_list = []

        self.setupTheStyles()
        
        icon_loc = resource_pth(os.path.join("images", "window.png"))
        if os.path.exists(icon_loc):
            try:
                icon_img = tk.PhotoImage(file=icon_loc)
                self.iconphoto(True, icon_img)
            except Exception: pass

        self.make_GUI()
        self.push_colors()

        uefn_pth = self.myCfg.get('uefn_project_dir')
        if not uefn_pth or not os.path.isdir(uefn_pth):
            self.after(150, self.do_first_launch_screen)

    def setupTheStyles(self):
        self.myStyle = ttk.Style(self)
        try: self.myStyle.theme_use('clam')
        except Exception: pass

    def push_colors(self):
        clr = self.clr
        self.configure(bg=clr['bg'])
        
        self.myStyle.configure('.', background=clr['bg'], foreground=clr['text'], fieldbackground=clr['entry_bg'], troughcolor=clr['surface2'], bordercolor=clr['border'], lightcolor=clr['bg'], darkcolor=clr['bg'], focuscolor=clr['bg'], font=('Segoe UI', 10))
        
        self.myStyle.configure('TNotebook', background=clr['bg'], borderwidth=0, tabmargins=0, lightcolor=clr['bg'], darkcolor=clr['bg'])
        self.myStyle.configure('TNotebook.Tab', background=clr['surface2'], foreground=clr['text_dim'], padding=(20, 9), borderwidth=0, font=('Segoe UI', 10), lightcolor=clr['surface2'], darkcolor=clr['surface2'], focuscolor=clr['surface'])
        self.myStyle.map('TNotebook.Tab', background=[('selected', clr['surface']), ('active', clr['surface'])], foreground=[('selected', clr['text']), ('active', clr['text'])], lightcolor=[('selected', clr['surface'])], darkcolor=[('selected', clr['surface'])])

        self.myStyle.configure('TFrame', background=clr['bg'])
        self.myStyle.configure('TLabel', background=clr['bg'], foreground=clr['text'])
        
        self.myStyle.configure('Accent.TButton', background=clr['accent'], foreground=clr['btn_fg'], borderwidth=0, focusthickness=0, relief='flat', font=('Segoe UI Semibold', 10), padding=(16, 9), lightcolor=clr['accent'], darkcolor=clr['accent'])
        self.myStyle.map('Accent.TButton', background=[('active', clr['accent_dim']), ('pressed', clr['accent_dim'])], foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        self.myStyle.configure('Secondary.TButton', background=clr['surface2'], foreground=clr['text'], borderwidth=0, focusthickness=0, relief='flat', font=('Segoe UI', 10), padding=(14, 8), lightcolor=clr['surface2'], darkcolor=clr['surface2'])
        self.myStyle.map('Secondary.TButton', background=[('active', clr['border']), ('pressed', clr['border'])], foreground=[('active', clr['text'])])

        self.myStyle.configure('TEntry', fieldbackground=clr['entry_bg'], foreground=clr['entry_fg'], bordercolor=clr['border'], relief='flat', padding=(8, 7), lightcolor=clr['entry_bg'], darkcolor=clr['entry_bg'])
        self.myStyle.map('TEntry', bordercolor=[('focus', clr['accent'])])

        self.myStyle.configure('TProgressbar', troughcolor=clr['surface2'], background=clr['accent'], borderwidth=0, thickness=4, lightcolor=clr['accent'], darkcolor=clr['accent'])

        self.color_da_tree(self)

    def color_da_tree(self, w):
        c = self.clr
        cls_name = w.__class__.__name__
        try:
            if cls_name == 'Frame': w.configure(bg=c['bg'])
            elif cls_name == 'Label': w.configure(bg=c['bg'], fg=c['text'])
            elif cls_name == 'Canvas': w.configure(bg=c['bg'])
        except: pass
        for kids in w.winfo_children(): self.color_da_tree(kids)

    def make_GUI(self):
        self.noteBook = ttk.Notebook(self)
        self.noteBook.pack(fill='both', expand=True)
        self.tab1 = ttk.Frame(self.noteBook)
        self.tab_settings_lmao = ttk.Frame(self.noteBook)
        self.noteBook.add(self.tab1, text='  Import  ')
        self.noteBook.add(self.tab_settings_lmao, text='  Settings  ')
        self.buildImportTab()
        self.build_settings_Tab()

    def buildImportTab(self):
        c = self.clr
        tb = self.tab1

        headr = tk.Frame(tb, bg=c['bg'])
        headr.pack(fill='x', padx=28, pady=(22, 0))
        tk.Label(headr, text='Import Assets', bg=c['bg'], fg=c['text'], font=('Segoe UI Semibold', 20)).pack(anchor='w')
        tk.Label(headr, text='Copy .uasset and .umap files into your UEFN project', bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 10)).pack(anchor='w', pady=(3, 0))

        tk.Frame(tb, bg=c['border'], height=1).pack(fill='x', pady=(16, 0))

        bdy = tk.Frame(tb, bg=c['bg'])
        bdy.pack(fill='both', expand=True, padx=28, pady=20)

        # Drop zone
        self.dropOuterFrame = tk.Frame(bdy, bg=c['border'], padx=1, pady=1)
        self.dropOuterFrame.pack(fill='x')
        self.dropCanvasArea = tk.Canvas(self.dropOuterFrame, height=118, bg=c['surface'], highlightthickness=0, cursor='hand2')
        self.dropCanvasArea.pack(fill='both', expand=True)
        self.dropCanvasArea.bind('<Configure>', lambda _: self.paint_drop_zone())
        self.dropCanvasArea.bind('<Button-1>', lambda _: self.btnActionDirSearch())
        self.dropCanvasArea.bind('<Enter>', self.hoverON)
        self.dropCanvasArea.bind('<Leave>', self.hoverOFF)
        self.dropOuterFrame.bind('<Enter>', self.hoverON)
        self.dropOuterFrame.bind('<Leave>', self.hoverOFF)

        if DND_READY:
            self.dropCanvasArea.drop_target_register('DND_Files')
            self.dropCanvasArea.dnd_bind('<<Drop>>', self.dnd_drop_handler)

        divider = tk.Frame(bdy, bg=c['bg'])
        divider.pack(fill='x', pady=(14, 10))
        tk.Frame(divider, bg=c['border'], height=1).pack(side='left', fill='x', expand=True, pady=10)
        tk.Label(divider, text='  or  ', bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 9)).pack(side='left')
        tk.Frame(divider, bg=c['border'], height=1).pack(side='left', fill='x', expand=True, pady=10)

        btn_container = tk.Frame(bdy, bg=c['bg'])
        btn_container.pack(fill='x')
        ttk.Button(btn_container, text='Select Folder', style='Secondary.TButton', command=self.btnActionDirSearch).pack(side='left', padx=(0, 8))
        ttk.Button(btn_container, text='Select ZIP', style='Secondary.TButton', command=self.btnActionZipSearch).pack(side='left', padx=(0, 8))
        ttk.Button(btn_container, text='Select Files (.uasset / .umap)', style='Secondary.TButton', command=self.btnActionFilesSearch).pack(side='left')

        self.pathVar = tk.StringVar(value='No source selected.')
        self.lbl_path = tk.Label(bdy, textvariable=self.pathVar, bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 9), anchor='w', wraplength=700)
        self.lbl_path.pack(fill='x', pady=(10, 0))

        tk.Frame(bdy, bg=c['border'], height=1).pack(fill='x', pady=(14, 14))

        p_row = tk.Frame(bdy, bg=c['bg'])
        p_row.pack(fill='x')
        tk.Label(p_row, text='Project Name', bg=c['bg'], fg=c['text'], font=('Segoe UI Semibold', 10), width=14, anchor='w').pack(side='left')
        self.projNameVar = tk.StringVar()
        ttk.Entry(p_row, textvariable=self.projNameVar, width=30).pack(side='left', padx=(8, 0))
        self.foundVarStr = tk.StringVar()
        self.lbl_found_msg = tk.Label(p_row, textvariable=self.foundVarStr, bg=c['bg'], fg=c['success'], font=('Segoe UI', 10))
        self.lbl_found_msg.pack(side='left', padx=(14, 0))

        i_row = tk.Frame(bdy, bg=c['bg'])
        i_row.pack(fill='x', pady=(14, 0))
        ttk.Button(i_row, text='Import to UEFN Project', style='Accent.TButton', command=self.trigger_import_logic).pack(side='left')

        tk.Frame(bdy, bg=c['border'], height=1).pack(fill='x', pady=(16, 10))
        self.stat_msg_var = tk.StringVar(value='Ready.')
        self.lbl_status = tk.Label(bdy, textvariable=self.stat_msg_var, bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 9), anchor='w')
        self.lbl_status.pack(fill='x')
        self.progressBar = ttk.Progressbar(bdy, mode='indeterminate')
        self.progressBar.pack(fill='x', pady=(6, 0))

    def paint_drop_zone(self):
        c = self.clr
        cv = self.dropCanvasArea
        cv.configure(bg=c['surface'])
        self.dropOuterFrame.configure(bg=c['border'])
        cv.delete('all')
        w = cv.winfo_width() or 740; h = cv.winfo_height() or 118
        centerX, centerY = w // 2, h // 2
        cv.create_rectangle(8, 8, w - 8, h - 8, outline=c['accent'], dash=(5, 4), width=2)
        top_text = "Drop a folder or ZIP file here" if DND_READY else "Click to browse for a folder"
        cv.create_text(centerX, centerY - 14, text=top_text, fill=c['text'], font=('Segoe UI Semibold', 12))
        cv.create_text(centerX, centerY + 13, text="Click anywhere in this box to browse", fill=c['text_dim'], font=('Segoe UI', 9))

    def hoverON(self, _=None): self.dropOuterFrame.configure(bg=self.clr['accent'])
    def hoverOFF(self, _=None): self.dropOuterFrame.configure(bg=self.clr['border'])

    def dnd_drop_handler(self, evt):
        raw_data = evt.data.strip()
        matches = re.findall(r'\{([^}]+)\}|(\S+)', raw_data)
        extracted = [x or y for x, y in matches]
        if extracted: self.handlePth(extracted[0])

    def build_settings_Tab(self):
        c = self.clr
        tb = self.tab_settings_lmao

        top_head = tk.Frame(tb, bg=c['bg'])
        top_head.pack(fill='x', padx=28, pady=(22, 0))
        tk.Label(top_head, text='Settings', bg=c['bg'], fg=c['text'], font=('Segoe UI Semibold', 20)).pack(anchor='w')
        tk.Label(top_head, text='Manage preferences and directories', bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 10)).pack(anchor='w', pady=(3, 0))

        tk.Frame(tb, bg=c['border'], height=1).pack(fill='x', pady=(16, 0))

        main_bod = tk.Frame(tb, bg=c['bg'])
        main_bod.pack(fill='both', expand=True, padx=28, pady=20)

        self.make_section(main_bod, 'UEFN Project Directory')
        d_r = tk.Frame(main_bod, bg=c['bg'])
        d_r.pack(fill='x', pady=(4, 16))
        self.uefnDirVar = tk.StringVar(value=self.myCfg.get('uefn_project_dir', ''))
        ttk.Entry(d_r, textvariable=self.uefnDirVar, width=52).pack(side='left', padx=(0, 8))
        ttk.Button(d_r, text='Browse', style='Secondary.TButton', command=self.search_uefn).pack(side='left')

        self.make_section(main_bod, 'Config File Location')
        c_r = tk.Frame(main_bod, bg=c['bg'])
        c_r.pack(fill='x', pady=(4, 4))
        self.cfgLocVar = tk.StringVar(value=self.myCfg.get('config_location', get_def_cfg()))
        ttk.Entry(c_r, textvariable=self.cfgLocVar, width=52).pack(side='left', padx=(0, 8))
        ttk.Button(c_r, text='Browse', style='Secondary.TButton', command=self.search_cfg_loc).pack(side='left')
        tk.Label(main_bod, text='config.json is stored next to this application by default.', bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 8)).pack(anchor='w', pady=(2, 14))

        self.make_section(main_bod, 'Warnings')
        w_r = tk.Frame(main_bod, bg=c['bg'])
        w_r.pack(fill='x', pady=(6, 16))
        self.chk_warn = tk.BooleanVar(value=self.myCfg.get('warn_unsupported', True))
        t_obj = CustomToggle(w_r, self.chk_warn, c, bg=c['bg'])
        t_obj.pack(side='left')
        self.tog_list.append(t_obj)
        tk.Label(w_r, text='Warn about unsupported file types', bg=c['bg'], fg=c['text'], font=('Segoe UI', 10)).pack(side='left', padx=(10, 0))

        self.make_section(main_bod, 'Appearance')
        self.cur_theme_var = tk.StringVar(value=self.myCfg.get('theme', 'system'))
        r_row = CustomRadio(main_bod, [('system', 'System Default'), ('dark', 'Dark'), ('light', 'Light')], self.cur_theme_var, c)
        r_row.pack(anchor='w', pady=(6, 16))
        self.radio_list.append(r_row)

        tk.Frame(main_bod, bg=c['border'], height=1).pack(fill='x', pady=(0, 14))
        ttk.Button(main_bod, text='Save Settings', style='Accent.TButton', command=self.save_the_settings).pack(anchor='w')

        self.make_section(main_bod, 'Support')
        tk.Label(main_bod, text='If this tool is useful, consider buying me a coffee.', bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 9)).pack(anchor='w', pady=(4, 8))
        ttk.Button(main_bod, text="Buy Me a Coffee",
                   style="Secondary.TButton",
                   command=lambda: webbrowser.open(
                       "https://www.buymeacoffee.com/itsmarwan")).pack(anchor="w") # i couldnt help but add it. yes i know its cheap but it is what it is 🤷‍♂️

    def make_section(self, p, txt):
        c = self.clr
        tk.Label(p, text=txt, bg=c['bg'], fg=c['text'], font=('Segoe UI Semibold', 11)).pack(anchor='w', pady=(10, 2))
        tk.Frame(p, bg=c['border'], height=1).pack(fill='x', pady=(0, 4))

    def search_uefn(self):
        fol = filedialog.askdirectory(title="Select UEFN Project Directory")
        if fol: self.uefnDirVar.set(fol)

    def search_cfg_loc(self):
        fil = filedialog.asksaveasfilename(title="Config File Location", defaultextension=".json", filetypes=[("JSON", "*.json")], initialfile="config.json")
        if fil: self.cfgLocVar.set(fil)

    def save_the_settings(self):
        uFol = self.uefnDirVar.get().strip()
        if uFol and not os.path.isdir(uFol):
            messagebox.showwarning("Invalid Path", "The UEFN project directory does not exist.")
            return

        oldPath = self.myCfg.get('config_location')
        newPath = self.cfgLocVar.get().strip() or get_def_cfg()

        self.myCfg['uefn_project_dir'] = uFol
        self.myCfg['warn_unsupported'] = self.chk_warn.get()
        self.myCfg['theme'] = self.cur_theme_var.get()
        self.myCfg['config_location'] = newPath

        if oldPath and oldPath != newPath and os.path.isfile(oldPath):
            try: os.remove(oldPath)
            except: pass

        if write_cfg_to_disk(self.myCfg):
            self.current_theme = getSystem_Theme(self.myCfg['theme'])
            self.clr = THEME_COLORS[self.current_theme]
            self.push_colors()
            self.print_status("Settings saved.", "success")
            messagebox.showinfo("Settings", "Settings saved.")


    def do_first_launch_screen(self):
        c = self.clr
        w = tk.Toplevel(self)
        w.title("Welcome")
        w.geometry("540x230"); w.resizable(False, False)
        w.grab_set()
        w.configure(bg=c['bg'])

        tk.Label(w, text="Welcome to UEFN Asset Importer", bg=c['bg'], fg=c['text'], font=('Segoe UI Semibold', 16)).pack(pady=(24, 4))
        tk.Label(w, text="Set your UEFN projects root directory to get started.", bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 10)).pack()
        tk.Frame(w, bg=c['border'], height=1).pack(fill='x', padx=24, pady=14)

        rw = tk.Frame(w, bg=c['bg'])
        rw.pack(padx=24, fill='x')
        pVar = tk.StringVar()
        ttk.Entry(rw, textvariable=pVar, width=46).pack(side='left', padx=(0, 8))

        def _b():
            fol = filedialog.askdirectory(title="UEFN Project Directory")
            if fol: pVar.set(fol)

        ttk.Button(rw, text="Browse", style='Secondary.TButton', command=_b).pack(side='left')

        def _c():
            txt = pVar.get().strip()
            if not txt or not os.path.isdir(txt):
                messagebox.showwarning("Invalid", "Please select a valid directory.", parent=w)
                return
            self.myCfg['uefn_project_dir'] = txt
            self.uefnDirVar.set(txt)
            write_cfg_to_disk(self.myCfg)
            w.destroy()

        ttk.Button(w, text="Continue", style='Accent.TButton', command=_c).pack(pady=20)

    def btnActionDirSearch(self):
        fld = filedialog.askdirectory(title="Select Asset Folder")
        if fld: self.handlePth(fld)

    def btnActionZipSearch(self):
        z = filedialog.askopenfilename(title="Select ZIP File", filetypes=[("ZIP archives", "*.zip")])
        if z: self.handlePth(z)

    def btnActionFilesSearch(self):
        ff = filedialog.askopenfilenames(title="Select .uasset / .umap Files", filetypes=[("UEFN Assets", "*.uasset *.umap"), ("All files", "*.*")])
        if not ff: return
        tmp = tempfile.mkdtemp(prefix="uefn_files_")
        for f in ff: shutil.copy2(f, tmp)
        self.sel_pth = tmp
        self.pathVar.set(f"Selected {len(ff)} file(s)")
        self.foundVarStr.set("")
        self.print_status(f"Loaded {len(ff)} file(s).", "dim")

    def handlePth(self, p):
        p = p.strip().strip("{}")
        if os.path.isfile(p) and zipfile.is_zipfile(p): self.process_zip(p)
        elif os.path.isdir(p):
            self.sel_pth = p
            self.pathVar.set(p)
            self.foundVarStr.set("")
            self.print_status("Folder loaded.", "dim")
        else: messagebox.showwarning("Unsupported", "Please select a folder, a ZIP file, or .uasset/.umap files.")

    def process_zip(self, zPath):
        self.print_status("Extracting ZIP...", "dim")
        self.progressBar.start(12)

        def w_thread():
            try:
                if self.tmp_folder_dir and os.path.isdir(self.tmp_folder_dir): shutil.rmtree(self.tmp_folder_dir, ignore_errors=True)
                self.tmp_folder_dir = tempfile.mkdtemp(prefix="uefn_zip_")
                unzip_it(zPath, self.tmp_folder_dir)
                self.sel_pth = self.tmp_folder_dir
                self.after(0, lambda: self.zip_finished(zPath))
            except Exception as ex:
                self.after(0, lambda: self.print_status(f"ZIP error: {ex}", "danger"))
                self.after(0, self.progressBar.stop)

        threading.Thread(target=w_thread, daemon=True).start()

    def zip_finished(self, zPath):
        self.progressBar.stop()
        self.pathVar.set(f"[ZIP] {zPath}")
        self.foundVarStr.set("")
        self.print_status("ZIP extracted.", "success")

    def trigger_import_logic(self):
        uDir = self.myCfg.get('uefn_project_dir', "").strip()
        if not uDir or not os.path.isdir(uDir):
            messagebox.showwarning("No Directory", "Set your UEFN project directory in Settings first.")
            return
        if not self.sel_pth:
            messagebox.showwarning("Nothing Selected", "Please select a folder, ZIP, or files first.")
            return
        pNm = self.projNameVar.get().strip()
        if not pNm:
            messagebox.showwarning("No Project Name", "Please enter the project name.")
            return

        self.progressBar.start(12)
        self.print_status("Working...", "dim")
        self.foundVarStr.set("")

        def w_thread2():
            try: self.execute_copy_routine(uDir, pNm)
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Import Error", str(ex)))
                self.after(0, lambda: self.print_status(f"Error: {ex}", "danger"))
            finally: self.after(0, self.progressBar.stop)

        threading.Thread(target=w_thread2, daemon=True).start()

    def execute_copy_routine(self, uDir, pNm):
        src = self.sel_pth
        target_lw = pNm.lower()

        base_nm = os.path.basename(src.rstrip("/\\"))
        if base_nm.lower() == target_lw:
            a_root = src
            self.after(0, lambda: self.display_match_res("exact"))
        else:
            fnd_sub = None
            for d_pth, dir_nms, _ in os.walk(src):
                for d in dir_nms:
                    if d.lower() == target_lw:
                        fnd_sub = os.path.join(d_pth, d)
                        break
                if fnd_sub: break

            if fnd_sub:
                a_root = fnd_sub
                self.after(0, lambda: self.display_match_res("sub"))
            else:
                a_root = src
                self.after(0, lambda: self.display_match_res("none"))

        inv_files = find_bad_exts(a_root)
        if inv_files and self.myCfg.get('warn_unsupported', True):
            ans = [None]
            ev = threading.Event()

            def do_diag():
                ans[0] = self.open_warn_modal(inv_files)
                ev.set()

            self.after(0, do_diag)
            ev.wait(timeout=120)

            if not ans[0]:
                self.after(0, lambda: self.print_status("Import cancelled.", "dim"))
                return

        dst = os.path.join(uDir, pNm, "Plugins", pNm, "Content")
        os.makedirs(dst, exist_ok=True)

        cnt = 0
        for r_p, _, f_list in os.walk(a_root):
            for f_n in f_list:
                if os.path.splitext(f_n)[1].lower() in ALLOWED_EXTENSIONS:
                    s_f = os.path.join(r_p, f_n)
                    r_l = os.path.relpath(s_f, a_root)
                    d_f = os.path.join(dst, r_l)
                    os.makedirs(os.path.dirname(d_f), exist_ok=True)
                    shutil.copy2(s_f, d_f)
                    cnt += 1

        txtMsg = f"Done. Imported {cnt} file(s) to:\n{dst}"
        self.after(0, lambda: self.print_status(f"Done. Imported {cnt} file(s) to: {dst}", "success"))
        self.after(0, lambda: messagebox.showinfo("Import Complete", txtMsg))

    def display_match_res(self, res_type):
        c = self.clr
        if res_type == 'exact':
            self.foundVarStr.set("Found! (folder name matched)")
            self.lbl_found_msg.configure(fg=c['success'])
        elif res_type == 'sub':
            self.foundVarStr.set("Found! (matched subfolder)")
            self.lbl_found_msg.configure(fg=c['success'])
        else:
            self.foundVarStr.set("No match found, importing root folder")
            self.lbl_found_msg.configure(fg=c['text_dim'])


    # man do i love the warn dialog. i cooked so hard on this 🥲
    def open_warn_modal(self, inv_files):
        c = self.clr
        pop = tk.Toplevel(self)
        pop.title("Unsupported Files")
        pop.geometry("530x370")
        pop.resizable(False, True)
        pop.grab_set()
        pop.configure(bg=c['bg'])

        tk.Label(pop, text="Unsupported Files Detected", bg=c['bg'], fg=c['warning'], font=('Segoe UI Semibold', 14)).pack(pady=(20, 4), padx=24, anchor='w')
        tk.Label(pop, text=("These files are not .uasset or .umap and will be skipped. " "Only valid UEFN assets will be imported."), bg=c['bg'], fg=c['text_dim'], font=('Segoe UI', 9), wraplength=482, justify='left').pack(padx=24, anchor='w')

        listWrapper = tk.Frame(pop, bg=c['surface2'])
        listWrapper.pack(fill='both', expand=True, padx=24, pady=10)
        s_bar = tk.Scrollbar(listWrapper)
        s_bar.pack(side='right', fill='y')
        list_box = tk.Listbox(listWrapper, yscrollcommand=s_bar.set, bg=c['surface2'], fg=c['text'], selectbackground=c['accent'], relief='flat', bd=0, font=('Consolas', 9))
        for f in inv_files[:300]: list_box.insert('end', "  " + f)
        if len(inv_files) > 300: list_box.insert('end', f"  ... and {len(inv_files) - 300} more")
        list_box.pack(side='left', fill='both', expand=True)
        s_bar.config(command=list_box.yview)

        bottom_opt = tk.Frame(pop, bg=c['bg'])
        bottom_opt.pack(fill='x', padx=24, pady=(0, 6))
        dn_var = tk.BooleanVar(value=False)
        tggl = CustomToggle(bottom_opt, dn_var, c, bg=c['bg'])
        tggl.pack(side='left')
        tk.Label(bottom_opt, text="Don't show this warning again", bg=c['bg'], fg=c['text'], font=('Segoe UI', 10)).pack(side='left', padx=(10, 0))

        resHolder = [False]

        def yesFunc():
            if dn_var.get():
                self.myCfg['warn_unsupported'] = False
                self.chk_warn.set(False)
                write_cfg_to_disk(self.myCfg)
            resHolder[0] = True
            pop.destroy()

        def noFunc(): pop.destroy()

        btns_row = tk.Frame(pop, bg=c['bg'])
        btns_row.pack(pady=(4, 18), padx=24, anchor='w')
        ttk.Button(btns_row, text="Continue Anyway", style='Accent.TButton', command=yesFunc).pack(side='left', padx=(0, 10))
        ttk.Button(btns_row, text="Cancel", style='Secondary.TButton', command=noFunc).pack(side='left')

        self.wait_window(pop)
        return resHolder[0]

    def print_status(self, text, state="dim"):
        c = self.clr
        myMap = { 'success': c['success'], 'warning': c['warning'], 'danger': c['danger'], 'dim': c['text_dim'] }
        self.stat_msg_var.set(text)
        self.lbl_status.configure(fg=myMap.get(state, c['text_dim']))

    def quit_app(self):
        if self.tmp_folder_dir and os.path.isdir(self.tmp_folder_dir): shutil.rmtree(self.tmp_folder_dir, ignore_errors=True)
        self.destroy()

if __name__ == "__main__":
    my_app = App()
    my_app.protocol("WM_DELETE_WINDOW", my_app.quit_app) # dont get scared for this line, its just to make sure the temp directory gets cleaned up when the app is closed.
    my_app.mainloop()

# 2026 (c) Marwan. All rights reserved.
# This software is licensed under the MIT License.