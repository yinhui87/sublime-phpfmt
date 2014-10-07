import csv
import os
import os.path
import shutil
import sublime
import sublime_plugin
import subprocess
from os.path import dirname, realpath

def dofmtsel(code, refactor_from = None, refactor_to = None, sgter = None):
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

    if debug:
        print("phpfmt (sel):", code)
        if disable_auto_align:
            print("auto align (sel): disabled")
        else:
            print("auto align (sel): enabled")


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

    if sgter is not None:
        cmd_fmt.append("--setters_and_getters="+sgter)

    cmd_fmt.append("--timing")

    if debug:
        print("cmd_fmt (sel): ", cmd_fmt)

    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(cmd_fmt, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
    else:
        p = subprocess.Popen(cmd_fmt, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    originalCode = code
    if "<?" != originalCode[:2]:
        code = '<?php/*REMOVEME*/'+"\n"+code;
    bufferedCode = bytes(code, 'utf-8');
    res, err = p.communicate(input=bufferedCode)

    print("err:\n", err.decode('utf-8'))
    return res.decode('utf-8').replace('<?php/*REMOVEME*/'+"\n", '')


def dofmt(eself, eview, refactor_from = None, refactor_to = None, sgter = None):
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

    if "php" != ext:
        print("phpfmt: not a PHP file")
        sublime.status_message("phpfmt: not a PHP file")
        return False

    if not os.path.isfile(php_bin) and not php_bin == "php":
        print("Can't find PHP binary file at "+php_bin)
        if int(sublime.version()) >= 3000:
            sublime.error_message("Can't find PHP binary file at "+php_bin)

    # Look for oracle.serialize
    oracleDirNm = dirnm
    while oracleDirNm != "/":
        oracleFname = oracleDirNm+os.path.sep+"oracle.serialize"
        if os.path.isfile(oracleFname):
            break
        origOracleDirNm = oracleDirNm
        oracleDirNm = os.path.dirname(oracleDirNm)
        if origOracleDirNm == oracleDirNm:
            break

    if not os.path.isfile(oracleFname):
        print("phpfmt (oracle file): not found")
        oracleFname = None
    else:
        print("phpfmt (oracle file): "+oracleFname)

    if debug:
        print("phpfmt:", uri)
        if disable_auto_align:
            print("auto align: disabled")
        else:
            print("auto align: enabled")



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

        if sgter is not None:
            cmd_fmt.append("--setters_and_getters="+sgter)

        if oracleFname is not None:
            cmd_fmt.append("--oracleDB="+oracleFname)

        cmd_fmt.append("--timing")

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
        print("err:\n", err.decode('utf-8'))
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

def lookForOracleFile(view):
        uri = view.file_name()
        oracleDirNm, sfn = os.path.split(uri)
        originalDirNm = oracleDirNm

        while oracleDirNm != "/":
            oracleFname = oracleDirNm+os.path.sep+"oracle.serialize"
            if os.path.isfile(oracleFname):
                return True
            origOracleDirNm = oracleDirNm
            oracleDirNm = os.path.dirname(oracleDirNm)
            if origOracleDirNm == oracleDirNm:
                return False
        return False

def outputToPanel(name, eself, eedit, message):
        eself.output_view = eself.view.window().get_output_panel(name)
        eself.view.window().run_command("show_panel", {"panel": "output."+name})
        eself.output_view.set_read_only(False)
        eself.output_view.insert(eedit, eself.output_view.size(), message)
        eself.output_view.set_read_only(True)

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

class AnalyseThisCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not lookForOracleFile(self.view):
            sublime.active_window().active_view().run_command("build_oracle")
            return False

        lookTerm = (self.view.substr(self.view.word(self.view.sel()[0].a)))

        s = sublime.load_settings('phpfmt.sublime-settings')
        php_bin = s.get("php_bin", "php")
        oraclePath = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "oracle.php")

        uri = self.view.file_name()
        dirNm, sfn = os.path.split(uri)
        ext = os.path.splitext(uri)[1][1:]

        oracleDirNm = dirNm
        while oracleDirNm != "/":
            oracleFname = oracleDirNm+os.path.sep+"oracle.serialize"
            if os.path.isfile(oracleFname):
                break
            origOracleDirNm = oracleDirNm
            oracleDirNm = os.path.dirname(oracleDirNm)
            if origOracleDirNm == oracleDirNm:
                break

        cmdOracle = [php_bin]
        cmdOracle.append(oraclePath)
        cmdOracle.append("introspect")
        cmdOracle.append(lookTerm)
        print(cmdOracle)
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False)
        res, err = p.communicate()

        print("phpfmt (introspect): "+res.decode('utf-8'))
        print("phpfmt (introspect) err: "+err.decode('utf-8'))

        outputToPanel("phpfmtintrospect", self, edit, "Analysis:\n"+res.decode('utf-8'));

class FmtNowCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view)

class FmtSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                code = self.view.substr(region)
                result = dofmtsel(code)
                self.view.replace(edit, region, result)


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
            print("phpfmt: visibility order disabled")
            sublime.status_message("phpfmt: visibility order disabled")
        else:
            s.set("visibility_order", True)
            print("phpfmt: visibility order enabled")
            sublime.status_message("phpfmt: visibility order enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleIndentWithSpaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        indent_with_space = s.get("indent_with_space", False)

        if indent_with_space:
            s.set("indent_with_space", False)
            print("phpfmt: indent with space disabled")
            sublime.status_message("phpfmt: indent with space disabled")
        else:
            s.set("indent_with_space", True)
            print("phpfmt: indent with space enabled")
            sublime.status_message("phpfmt: indent with space enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class TogglePsrOneCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        psr1 = s.get("psr1", False)

        if psr1:
            s.set("psr1", False)
            print("phpfmt: PSR1 disabled")
            sublime.status_message("phpfmt: PSR1 disabled")
        else:
            s.set("psr1", True)
            print("phpfmt: PSR1 enable")
            sublime.status_message("phpfmt: PSR1 enable")

        sublime.save_settings('phpfmt.sublime-settings')

class TogglePsrTwoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        psr2 = s.get("psr2", False)

        if psr2:
            s.set("psr2", False)
            print("phpfmt: PSR2 disabled")
            sublime.status_message("phpfmt: PSR2 disabled")
        else:
            s.set("psr2", True)
            print("phpfmt: PSR2 enabled")
            sublime.status_message("phpfmt: PSR2 enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleFormatOnSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", False)

        if format_on_save:
            s.set("format_on_save", False)
            print("phpfmt: format on save disabled")
            sublime.status_message("phpfmt: format on save disabled")
        else:
            s.set("format_on_save", True)
            print("phpfmt: format on save enabled")
            sublime.status_message("phpfmt: format on save enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleAutocompleteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        autocomplete = s.get("autocomplete", False)

        if autocomplete:
            s.set("autocomplete", False)
            print("phpfmt: autocomplete disabled")
            sublime.status_message("phpfmt: autocomplete disabled")
        else:
            s.set("autocomplete", True)
            print("phpfmt: autocomplete enabled")
            sublime.status_message("phpfmt: autocomplete enabled")
            if not lookForOracleFile(self.view):
                sublime.active_window().active_view().run_command("build_oracle")

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

        s = ""
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)

        self.view.window().show_input_panel('Refactor From:', s, askForToTokens, None, None)

class SgterSnakeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, None, None, 'snake')

class SgterCamelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, None, None, 'camel')

class SgterGoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, None, None, 'golang')

class BuildOracleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def buildDB():
            self.msgFile.window().run_command('close_file')
            s = sublime.load_settings('phpfmt.sublime-settings')
            php_bin = s.get("php_bin", "php")
            oraclePath = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "oracle.php")
            cmdOracle = [php_bin]
            cmdOracle.append(oraclePath)
            cmdOracle.append("flush")
            cmdOracle.append(self.dirNm)
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.dirNm, shell=False, startupinfo=startupinfo)
            else:
                p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.dirNm, shell=False)
            res, err = p.communicate()
            print("phpfmt (oracle): "+res.decode('utf-8'))
            print("phpfmt (oracle) err: "+err.decode('utf-8'))
            sublime.status_message("phpfmt (oracle): done")


        #sublime.set_timeout_async(self.long_command, 0)
        def askForDirectory(text):
            self.dirNm = text
            if int(sublime.version()) >= 3000:
                sublime.set_timeout_async(buildDB, 0)
            else:
                sublime.set_timeout(buildDB, 50)

        view = self.view
        s = sublime.load_settings('phpfmt.sublime-settings')
        php_bin = s.get("php_bin", "php")

        uri = view.file_name()
        oracleDirNm, sfn = os.path.split(uri)
        originalDirNm = oracleDirNm

        while oracleDirNm != "/":
            oracleFname = oracleDirNm+os.path.sep+"oracle.serialize"
            if os.path.isfile(oracleFname):
                break
            origOracleDirNm = oracleDirNm
            oracleDirNm = os.path.dirname(oracleDirNm)
            if origOracleDirNm == oracleDirNm:
                break


        if not os.path.isfile(oracleFname):
            print("phpfmt (oracle file): not found -- dialog")

            self.msgFile = self.view.window().open_file(os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "message"))
            self.msgFile.set_read_only(True)
            self.view.window().show_input_panel('location:', originalDirNm, askForDirectory, None, None)
        else:
            print("phpfmt (oracle file): "+oracleFname)
            print("phpfmt (oracle dir): "+oracleDirNm)
            self.dirNm = oracleDirNm
            if int(sublime.version()) >= 3000:
                sublime.set_timeout_async(buildDB, 0)
            else:
                sublime.set_timeout(buildDB, 50)



class PHPFmtComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        s = sublime.load_settings('phpfmt.sublime-settings')

        autocomplete = s.get("autocomplete", False)
        if autocomplete is False:
                return []

        pos = locations[0]
        scopes = view.scope_name(pos).split()
        if not ('source.php.embedded.block.html' in scopes or 'source.php' in scopes):
            return []


        print("phpfmt (autocomplete): "+prefix);

        comps = []

        uri = view.file_name()
        dirNm, sfn = os.path.split(uri)
        ext = os.path.splitext(uri)[1][1:]


        oracleDirNm = dirNm
        while oracleDirNm != "/":
            oracleFname = oracleDirNm+os.path.sep+"oracle.serialize"
            if os.path.isfile(oracleFname):
                break
            origOracleDirNm = oracleDirNm
            oracleDirNm = os.path.dirname(oracleDirNm)
            if origOracleDirNm == oracleDirNm:
                break


        if not os.path.isfile(oracleFname):
            sublime.status_message("phpfmt: autocomplete database not found")
            return []

        if prefix in "namespace":
            ns = dirNm.replace(oracleDirNm, '').replace('/','\\')
            if ns.startswith('\\'):
                ns = ns[1:]
            comps.append((
                '%s \t %s \t %s' % ("namespace", ns, "namespace"),
                '%s %s;\n${0}' % ("namespace", ns),
            ))

        if prefix in "class":
            print("class guess")
            className = sfn.split(".")[0]
            comps.append((
                '%s \t %s \t %s' % ("class", className, "class"),
                '%s %s {\n\t${0}\n}\n' % ("class", className),
            ))

        php_bin = s.get("php_bin", "php")
        oraclePath = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "oracle.php")
        cmdOracle = [php_bin]
        cmdOracle.append(oraclePath)
        cmdOracle.append("autocomplete")
        cmdOracle.append(prefix)
        print(cmdOracle)
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False)
        res, err = p.communicate()
        print("phpfmt (autocomplete) err: "+err.decode('utf-8'))

        f = res.decode('utf-8').split('\n')
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if len(row) > 0:
                if "class" == row[3]:
                    comps.append((
                        '%s \t %s \t %s' % (row[1], row[0], "class"),
                        '%s(${0})' % (row[1]),
                    ))
                    comps.append((
                        '%s \t %s \t %s' % (row[0], row[0], "class"),
                        '%s(${0})' % (row[0]),
                    ))
                if "method" == row[3]:
                    comps.append((
                        '%s \t %s \t %s' % (row[1], row[2], "method"),
                        '%s' % (row[0].replace('$','\$')),
                    ))

        return comps
