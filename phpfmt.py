import os
import os.path
import shutil
import sublime
import sublime_plugin
import subprocess
from os.path import dirname, realpath


def dofmt(eself, eview, refactor_from = None, refactor_to = None):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    disable_auto_align = s.get("disable_auto_align", False)
    visibility_order = s.get("visibility_order", False)
    php_bin = s.get("php_bin", "php")
    formatter_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "codeFormatter.php")

    uri = view.file_name()
    dirnm, sfn = os.path.split(uri)
    ext = os.path.splitext(uri)[1][1:]

    if not os.path.isfile(php_bin) and not php_bin == "php":
        print("Can't find PHP binary file at "+php_bin)
        if int(sublime.version()) >= 3000:
            sublime.error_message("Can't find PHP binary file at "+php_bin)

    if debug:
        print("phpfmt:", uri)
        if disable_auto_align:
            print("auto align: disabled")
        else:
            print("auto align: enabled")

    if "php" != ext:
        print("phpfmt: not a PHP file")
        sublime.status_message("phpfmt: not a PHP file")
        return False

    cmd_lint = [php_bin,"-l",uri];
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
    else:
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
    lint_out, lint_err = p.communicate()

    if(p.returncode==0):
        cmd_fmt = [php_bin]

        if debug:
            cmd_fmt.append("-ddisplay_errors=0")

        cmd_fmt.append(formatter_path)

        if psr:
            cmd_fmt.append("--psr")

        if psr1:
            cmd_fmt.append("--psr1")

        if psr2:
            cmd_fmt.append("--psr2")

        if indent_with_space:
            cmd_fmt.append("--indent_with_space")

        if disable_auto_align:
            cmd_fmt.append("--disable_auto_align")

        if visibility_order:
            cmd_fmt.append("--visibility_order")

        if refactor_from is not None and refactor_to is not None:
            cmd_fmt.append("--refactor="+refactor_from)
            cmd_fmt.append("--to="+refactor_to)

        cmd_fmt.append(uri)

        uri_tmp = uri + "~"

        if debug:
            print("cmd_fmt: ", cmd_fmt)

        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd_fmt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmd_fmt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
        res, err = p.communicate()
        if err:
            if debug:
                print("err: ", err)
        else:
            if int(sublime.version()) < 3000:
                with open(uri_tmp, 'w+') as f:
                    f.write(res)
            else:
                with open(uri_tmp, 'bw+') as f:
                    f.write(res)
            if debug:
                print("Stored:", len(res), "bytes")
            shutil.move(uri_tmp, uri)
            sublime.set_timeout(revert_active_window, 50)
    else:
        print("lint error: ", lint_out)

def revert_active_window():
    sublime.active_window().active_view().run_command("revert")


class phpfmt(sublime_plugin.EventListener):
    def on_post_save(self, view):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", True)

        if format_on_save and int(sublime.version()) < 3000:
            self.on_post_save_async(view)

    def on_post_save_async(self, view):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", True)
        if format_on_save:
            dofmt(self, view)

class FmtSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view)

class ToggleAutoAlignCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        disable_auto_align = s.get("disable_auto_align", False)

        if disable_auto_align:
            s.set("disable_auto_align", False)
            print("phpfmt: auto align enabled")
            sublime.status_message("phpfmt: auto align enabled")
        else:
            s.set("disable_auto_align", True)
            print("phpfmt: auto align disabled")
            sublime.status_message("phpfmt: auto align disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleVisibilityOrderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        visibility_order = s.get("visibility_order", False)

        if visibility_order:
            s.set("visibility_order", False)
            print("phpfmt: visibility order enabled")
            sublime.status_message("phpfmt: visibility order enabled")
        else:
            s.set("visibility_order", True)
            print("phpfmt: visibility order disabled")
            sublime.status_message("phpfmt: visibility order disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleIndentWithSpaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        indent_with_space = s.get("indent_with_space", False)

        if indent_with_space:
            s.set("indent_with_space", False)
            print("phpfmt: indent with space enabled")
            sublime.status_message("phpfmt: indent with space enabled")
        else:
            s.set("indent_with_space", True)
            print("phpfmt: indent with space disabled")
            sublime.status_message("phpfmt: indent with space disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class TogglePsrOneCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        psr1 = s.get("psr1", False)

        if psr1:
            s.set("psr1", False)
            print("phpfmt: PSR1 enabled")
            sublime.status_message("phpfmt: PSR1 enabled")
        else:
            s.set("psr1", True)
            print("phpfmt: PSR1 disabled")
            sublime.status_message("phpfmt: PSR1 disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class TogglePsrTwoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        psr2 = s.get("psr2", False)

        if psr2:
            s.set("psr2", False)
            print("phpfmt: PSR2 enabled")
            sublime.status_message("phpfmt: PSR2 enabled")
        else:
            s.set("psr2", True)
            print("phpfmt: PSR2 disabled")
            sublime.status_message("phpfmt: PSR2 disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleFormatOnSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", False)

        if format_on_save:
            s.set("format_on_save", False)
            print("phpfmt: format on save enabled")
            sublime.status_message("phpfmt: format on save enabled")
        else:
            s.set("format_on_save", True)
            print("phpfmt: format on save disabled")
            sublime.status_message("phpfmt: format on save disabled")

        sublime.save_settings('phpfmt.sublime-settings')

class RefactorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def execute(text):
            self.token_to = text
            dofmt(self, self.view, self.token_from, self.token_to)

        def askForToTokens(text):
            self.token_from = text
            self.view.window().show_input_panel('From '+text+' refactor To:', '', execute, None, None)

        uri = self.view.file_name()
        dirnm, sfn = os.path.split(uri)
        ext = os.path.splitext(uri)[1][1:]

        if "php" != ext:
            print("phpfmt: not a PHP file")
            sublime.status_message("phpfmt: not a PHP file")
            return False

        self.view.window().show_input_panel('Refactor From:', '', askForToTokens, None, None)
