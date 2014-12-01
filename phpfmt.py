import csv
import os
import os.path
import shutil
import sublime
import sublime_plugin
import subprocess
import time
import csv
from os.path import dirname, realpath

def dofmt(eself, eview, sgter = None):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr1_naming = s.get("psr1_naming", psr1)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    enable_auto_align = s.get("enable_auto_align", False)
    visibility_order = s.get("visibility_order", False)
    autoimport = s.get("autoimport", True)
    short_array = s.get("short_array", False)
    merge_else_if = s.get("merge_else_if", False)
    smart_linebreak_after_curly = s.get("smart_linebreak_after_curly", True)
    yoda = s.get("yoda", False)
    autopreincrement = s.get("autopreincrement", False)
    remove_leading_slash = s.get("remove_leading_slash", False)
    linebreak_after_namespace = s.get("linebreak_after_namespace", False)
    linebreak_between_methods = s.get("linebreak_between_methods", False)
    remove_return_empty = s.get("remove_return_empty", False)
    add_missing_parentheses = s.get("add_missing_parentheses", False)
    wrong_constructor_name = s.get("wrong_constructor_name", False)
    join_to_implode = s.get("join_to_implode", False)
    encapsulate_namespaces = s.get("encapsulate_namespaces", False)
    ignore_list = s.get("ignore_list", "")
    laravel_style = s.get("laravel_style", False)
    cakephp_style = s.get("cakephp_style", False)

    php_bin = s.get("php_bin", "php")
    formatter_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "fmt.php")
    config_file = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "php.tools.ini")

    uri = view.file_name()
    dirnm, sfn = os.path.split(uri)
    ext = os.path.splitext(uri)[1][1:]

    if "php" != ext:
        if debug:
            print("phpfmt: not a PHP file")
        return False

    if "" != ignore_list:
        ignore_list = ignore_list.split(" ")
        for v in ignore_list:
            pos = uri.find(v)
            if -1 != pos:
                if debug:
                    print("phpfmt: skipping file")
                return False;

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
        if debug:
            print("phpfmt (oracle file): not found")
        oracleFname = None
    else:
        if debug:
            print("phpfmt (oracle file): "+oracleFname)

    if debug:
        print("phpfmt:", uri)

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

        if not debug:
            cmd_fmt.append("-ddisplay_errors=stderr")

        cmd_fmt.append(formatter_path)
        cmd_fmt.append("--config="+config_file)

        if psr:
            psr1 = True
            psr1_naming = True
            psr2 = True

        if psr1:
            cmd_fmt.append("--psr1")

        if psr1_naming:
            cmd_fmt.append("--psr1-naming")

        if psr2:
            cmd_fmt.append("--psr2")

        if indent_with_space:
            cmd_fmt.append("--indent_with_space")

        if enable_auto_align:
            cmd_fmt.append("--enable_auto_align")

        if visibility_order:
            cmd_fmt.append("--visibility_order")

        if smart_linebreak_after_curly:
            cmd_fmt.append("--smart_linebreak_after_curly")

        if yoda:
            cmd_fmt.append("--yoda")

        if laravel_style:
            cmd_fmt.append("--laravel")

        if cakephp_style:
            cmd_fmt.append("--cakephp")

        if sgter is not None:
            cmd_fmt.append("--setters_and_getters="+sgter)
            cmd_fmt.append("--constructor="+sgter)

        if autoimport is True and oracleFname is not None:
            cmd_fmt.append("--oracleDB="+oracleFname)


        extras = []
        if short_array:
            extras.append("ShortArray")

        if merge_else_if:
            extras.append("MergeElseIf")

        if autopreincrement:
            extras.append("AutoPreincrement")

        if remove_leading_slash:
            extras.append("RemoveUseLeadingSlash")

        if linebreak_after_namespace:
            extras.append("PSR2LnAfterNamespace")

        if wrong_constructor_name:
            extras.append("WrongConstructorName")

        if join_to_implode:
            extras.append("JoinToImplode")

        if len(extras) > 0:
            cmd_fmt.append("--passes="+','.join(extras))

        preextras = []
        if encapsulate_namespaces:
            preextras.append("EncapsulateNamespaces")

        if linebreak_between_methods:
            preextras.append("SpaceBetweenMethods")

        if remove_return_empty:
            preextras.append("ReturnNull")

        if add_missing_parentheses:
            preextras.append("AddMissingParentheses")

        if len(preextras) > 0:
            cmd_fmt.append("--prepasses="+','.join(preextras))

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
        if debug:
            print("err:\n", err.decode('utf-8'))
        sublime.set_timeout(revert_active_window, 50)
        time.sleep(1)
        sublime.active_window().active_view().run_command("phpfmt_vet")
    else:
        if debug:
            print("lint error: ", lint_out)


def dogeneratephpdoc(eself, eview):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr1_naming = s.get("psr1_naming", psr1)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    enable_auto_align = s.get("enable_auto_align", False)
    visibility_order = s.get("visibility_order", False)
    autoimport = s.get("autoimport", True)
    short_array = s.get("short_array", False)
    merge_else_if = s.get("merge_else_if", False)
    php_bin = s.get("php_bin", "php")
    formatter_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "fmt.php")
    config_file = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "php.tools.ini")
    laravel_style = s.get("laravel_style", False)
    cakephp_style = s.get("cakephp_style", False)

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

    if debug:
        print("phpfmt:", uri)
        if enable_auto_align:
            print("auto align: enabled")
        else:
            print("auto align: disabled")



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

        if not debug:
            cmd_fmt.append("-ddisplay_errors=stderr")

        cmd_fmt.append(formatter_path)
        cmd_fmt.append("--config="+config_file)

        if psr:
            psr1 = True
            psr1_naming = True
            psr2 = True

        if psr1:
            cmd_fmt.append("--psr1")

        if psr1_naming:
            cmd_fmt.append("--psr1-naming")

        if psr2:
            cmd_fmt.append("--psr2")

        if indent_with_space:
            cmd_fmt.append("--indent_with_space")

        if enable_auto_align:
            cmd_fmt.append("--enable_auto_align")

        if visibility_order:
            cmd_fmt.append("--visibility_order")

        if laravel_style:
            cmd_fmt.append("--laravel")

        if cakephp_style:
            cmd_fmt.append("--cakephp")

        extras = []
        if short_array:
            extras.append("ShortArray")

        if merge_else_if:
            extras.append("MergeElseIf")

        if len(extras) > 0:
            cmd_fmt.append("--passes="+','.join(extras))

        cmd_fmt.append("--prepasses=GeneratePHPDoc")

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
        sublime.set_timeout(revert_active_window, 50)
    else:
        print("lint error: ", lint_out)

def doreordermethod(eself, eview):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr1_naming = s.get("psr1_naming", psr1)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    enable_auto_align = s.get("enable_auto_align", False)
    visibility_order = s.get("visibility_order", False)
    autoimport = s.get("autoimport", True)
    short_array = s.get("short_array", False)
    merge_else_if = s.get("merge_else_if", False)
    php_bin = s.get("php_bin", "php")
    formatter_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "fmt.php")
    config_file = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "php.tools.ini")
    laravel_style = s.get("laravel_style", False)
    cakephp_style = s.get("cakephp_style", False)

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

    if debug:
        print("phpfmt:", uri)
        if enable_auto_align:
            print("auto align: enabled")
        else:
            print("auto align: disabled")



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

        if not debug:
            cmd_fmt.append("-ddisplay_errors=stderr")

        cmd_fmt.append(formatter_path)
        cmd_fmt.append("--config="+config_file)

        if psr:
            psr1 = True
            psr1_naming = True
            psr2 = True

        if psr1:
            cmd_fmt.append("--psr1")

        if psr1_naming:
            cmd_fmt.append("--psr1-naming")

        if psr2:
            cmd_fmt.append("--psr2")

        if indent_with_space:
            cmd_fmt.append("--indent_with_space")

        if enable_auto_align:
            cmd_fmt.append("--enable_auto_align")

        if visibility_order:
            cmd_fmt.append("--visibility_order")

        if laravel_style:
            cmd_fmt.append("--laravel")

        if cakephp_style:
            cmd_fmt.append("--cakephp")

        extras = ['OrderMethod']
        if short_array:
            extras.append("ShortArray")

        if merge_else_if:
            extras.append("MergeElseIf")

        if len(extras) > 0:
            cmd_fmt.append("--passes="+','.join(extras))

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
        sublime.set_timeout(revert_active_window, 50)
    else:
        print("lint error: ", lint_out)


def dorefactor(eself, eview, refactor_from = None, refactor_to = None):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr1_naming = s.get("psr1_naming", psr1)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    enable_auto_align = s.get("enable_auto_align", False)
    visibility_order = s.get("visibility_order", False)
    autoimport = s.get("autoimport", True)
    short_array = s.get("short_array", False)
    merge_else_if = s.get("merge_else_if", False)
    php_bin = s.get("php_bin", "php")
    refactor_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "refactor.php")

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

    cmd_lint = [php_bin,"-l",uri];
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
    else:
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
    lint_out, lint_err = p.communicate()

    if(p.returncode==0):
        cmd_refactor = [php_bin]

        if not debug:
            cmd_refactor.append("-ddisplay_errors=stderr")

        cmd_refactor.append(refactor_path)

        cmd_refactor.append("--from="+refactor_from)
        cmd_refactor.append("--to="+refactor_to)

        cmd_refactor.append(uri)

        uri_tmp = uri + "~"

        if debug:
            print("cmd_refactor: ", cmd_refactor)

        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd_refactor, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmd_refactor, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
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
    sublime.active_window().active_view().run_command("phpcs_sniff_this_file")

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

def hidePanel(name, eself, eedit):
        eself.output_view = eself.view.window().get_output_panel(name)
        eself.view.window().run_command("hide_panel", {"panel": "output."+name})

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


lastCalltip = ""
class CalltipCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global lastCalltip
        uri = self.view.file_name()
        dirnm, sfn = os.path.split(uri)
        ext = os.path.splitext(uri)[1][1:]

        if "php" != ext:
            return False

        if not lookForOracleFile(self.view):
            return False

        lookTerm = (self.view.substr(self.view.word(self.view.sel()[0].a)))
        if lastCalltip == lookTerm:
            return False

        lastCalltip = lookTerm

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
        cmdOracle.append("calltip")
        cmdOracle.append(lookTerm)
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmdOracle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=oracleDirNm, shell=False)
        res, err = p.communicate()

        output = res.decode('utf-8');

        self.view.set_status("phpfmt", output)


class FmtNowCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view)

class ToggleVetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        vet = s.get("vet", False)

        if vet:
            s.set("vet", False)
            print("phpfmt: vet disabled")
            sublime.status_message("phpfmt: vet disabled")
        else:
            s.set("vet", True)
            print("phpfmt: vet enabled")
            sublime.status_message("phpfmt: vet enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleRemoveLeadingSlash(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        remove_leading_slash = s.get("remove_leading_slash", False)

        if remove_leading_slash:
            s.set("remove_leading_slash", False)
            print("phpfmt: remove leading slash disabled")
            sublime.status_message("phpfmt: remove leading slash disabled")
        else:
            s.set("remove_leading_slash", True)
            print("phpfmt: remove leading slash enabled")
            sublime.status_message("phpfmt: remove leading slash enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleAutoAlignCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        enable_auto_align = s.get("enable_auto_align", False)

        if enable_auto_align:
            s.set("enable_auto_align", False)
            print("phpfmt: auto align disabled")
            sublime.status_message("phpfmt: auto align disabled")
        else:
            s.set("enable_auto_align", True)
            print("phpfmt: auto align enabled")
            sublime.status_message("phpfmt: auto align enabled")

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

class TogglePsrOneNamingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        psr1 = s.get("psr1", False)
        psr1_naming = s.get("psr1_naming", psr1)

        if psr1_naming:
            s.set("psr1_naming", False)
            print("phpfmt PSR1 Class and Method Naming disabled")
            sublime.status_message("phpfmt PSR1 Class and Method Naming disabled")
        else:
            s.set("psr1_naming", True)
            print("phpfmt PSR1 Class and Method Naming enable")
            sublime.status_message("phpfmt PSR1 Class and Method Naming enable")

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

class ToggleAddMissingParenthesesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        add_missing_parentheses = s.get("add_missing_parentheses", False)

        if add_missing_parentheses:
            s.set("add_missing_parentheses", False)
            print("phpfmt: add missing parentheses disabled")
            sublime.status_message("phpfmt: add missing parentheses disabled")
        else:
            s.set("add_missing_parentheses", True)
            print("phpfmt: add missing parentheses enabled")
            sublime.status_message("phpfmt: add missing parentheses enabled")

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

class ToggleAutoimportCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        autoimport = s.get("autoimport", False)

        if autoimport:
            s.set("autoimport", False)
            print("phpfmt: autoimport disabled")
            sublime.status_message("phpfmt: autoimport disabled")
        else:
            s.set("autoimport", True)
            print("phpfmt: autoimport enabled")
            sublime.status_message("phpfmt: autoimport enabled")
            if not lookForOracleFile(self.view):
                sublime.active_window().active_view().run_command("build_oracle")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleShortArrayCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        shortArray = s.get("short_array", False)

        if shortArray:
            s.set("short_array", False)
            print("phpfmt: shortArray disabled")
            sublime.status_message("phpfmt: shortArray disabled")
        else:
            s.set("short_array", True)
            print("phpfmt: shortArray enabled")
            sublime.status_message("phpfmt: shortArray enabled")

        sublime.save_settings('phpfmt.sublime-settings')


class ToggleMergeElseIfCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        MergeElseIf = s.get("merge_else_if", False)

        if MergeElseIf:
            s.set("merge_else_if", False)
            print("phpfmt: MergeElseIf disabled")
            sublime.status_message("phpfmt: MergeElseIf disabled")
        else:
            s.set("merge_else_if", True)
            print("phpfmt: MergeElseIf enabled")
            sublime.status_message("phpfmt: MergeElseIf enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleSmartLinebreakAfterCurlyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        smart_linebreak_after_curly = s.get("smart_linebreak_after_curly", True)

        if smart_linebreak_after_curly:
            s.set("smart_linebreak_after_curly", False)
            print("phpfmt: SmartLinebreakAfterCurly disabled")
            sublime.status_message("phpfmt: SmartLinebreakAfterCurly disabled")
        else:
            s.set("smart_linebreak_after_curly", True)
            print("phpfmt: SmartLinebreakAfterCurly enabled")
            sublime.status_message("phpfmt: SmartLinebreakAfterCurly enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleYodaCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        yoda = s.get("yoda", False)

        if yoda:
            s.set("yoda", False)
            print("phpfmt: Yoda Mode disabled")
            sublime.status_message("phpfmt: Yoda Mode disabled")
        else:
            s.set("yoda", True)
            print("phpfmt: Yoda Mode enabled")
            sublime.status_message("phpfmt: Yoda Mode enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleAutopreincrementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        autopreincrement = s.get("autopreincrement", False)

        if autopreincrement:
            s.set("autopreincrement", False)
            print("phpfmt: automatic preincrement disabled")
            sublime.status_message("phpfmt: automatic preincrement disabled")
        else:
            s.set("autopreincrement", True)
            print("phpfmt: automatic preincrement enabled")
            sublime.status_message("phpfmt: automatic preincrement enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleLinebreakAfterNamespaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        linebreak_after_namespace = s.get("linebreak_after_namespace", False)

        if linebreak_after_namespace:
            s.set("linebreak_after_namespace", False)
            print("phpfmt: automatic linebreak after namespace disabled")
            sublime.status_message("phpfmt: automatic linebreak after namespace disabled")
        else:
            s.set("linebreak_after_namespace", True)
            print("phpfmt: automatic linebreak after namespace enabled")
            sublime.status_message("phpfmt: automatic linebreak after namespace enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleLinebreakBetweenMethodsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        linebreak_between_methods = s.get("linebreak_between_methods", False)

        if linebreak_between_methods:
            s.set("linebreak_between_methods", False)
            print("phpfmt: automatic linebreak between methods disabled")
            sublime.status_message("phpfmt: automatic linebreak between methods disabled")
        else:
            s.set("linebreak_between_methods", True)
            print("phpfmt: automatic linebreak between methods enabled")
            sublime.status_message("phpfmt: automatic linebreak between methods enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleReturnEmptyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        remove_return_empty = s.get("remove_return_empty", False)

        if remove_return_empty:
            s.set("remove_return_empty", False)
            print("phpfmt: remove empty returns disabled")
            sublime.status_message("phpfmt: remove empty returns disabled")
        else:
            s.set("remove_return_empty", True)
            print("phpfmt: remove empty returns enabled")
            sublime.status_message("phpfmt: remove empty returns enabled")

        sublime.save_settings('phpfmt.sublime-settings')


class ToggleWrongConstructorNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        wrong_constructor_name = s.get("wrong_constructor_name", False)

        if wrong_constructor_name:
            s.set("wrong_constructor_name", False)
            print("phpfmt: update old style constructor disabled")
            sublime.status_message("phpfmt: update old style constructor disabled")
        else:
            s.set("wrong_constructor_name", True)
            print("phpfmt: update old style constructor enabled")
            sublime.status_message("phpfmt: update old style constructor enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleJoinToImplodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        join_to_implode = s.get("join_to_implode", False)

        if join_to_implode:
            s.set("join_to_implode", False)
            print("phpfmt: replace join() to implode() disabled")
            sublime.status_message("phpfmt: replace join() to implode() disabled")
        else:
            s.set("join_to_implode", True)
            print("phpfmt: replace join() to implode() enabled")
            sublime.status_message("phpfmt: replace join() to implode() enabled")

        sublime.save_settings('phpfmt.sublime-settings')

class ToggleEncapsulateNamespacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        encapsulate_namespaces = s.get("encapsulate_namespaces", False)

        if encapsulate_namespaces:
            s.set("encapsulate_namespaces", False)
            print("phpfmt: automatic namespace encapsulation disabled")
            sublime.status_message("phpfmt: automatic namespace encapsulation disabled")
        else:
            s.set("encapsulate_namespaces", True)
            print("phpfmt: automatic namespace encapsulation enabled")
            sublime.status_message("phpfmt: automatic namespace encapsulation enabled")

        sublime.save_settings('phpfmt.sublime-settings')


class ToggleLaravelStyleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        laravel_style = s.get("laravel_style", False)

        if laravel_style:
            s.set("laravel_style", False)
            print("phpfmt: Laravel style disabled")
            sublime.status_message("phpfmt: Laravel style disabled")
        else:
            s.set("laravel_style", True)
            print("phpfmt: Laravel style enabled")
            sublime.status_message("phpfmt: Laravel style enabled")

        sublime.save_settings('phpfmt.sublime-settings')


class ToggleCakephpStyleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        cakephp_style = s.get("cakephp_style", False)

        if cakephp_style:
            s.set("cakephp_style", False)
            print("phpfmt: CakePHP style disabled")
            sublime.status_message("phpfmt: CakePHP style disabled")
        else:
            s.set("cakephp_style", True)
            print("phpfmt: CakePHP style enabled")
            sublime.status_message("phpfmt: CakePHP style enabled")

        sublime.save_settings('phpfmt.sublime-settings')


class RefactorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def execute(text):
            self.token_to = text
            dorefactor(self, self.view, self.token_from, self.token_to)

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

class OrderMethodCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        doreordermethod(self, self.view)

class GeneratePhpdocCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dogeneratephpdoc(self, self.view)

class SgterSnakeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, 'snake')

class SgterCamelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, 'camel')

class SgterGoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view, 'golang')

class PhpfmtVetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings('phpfmt.sublime-settings')
        run_vet = s.get('vet', False)
        if not run_vet:
            return False

        view = self.view

        uri = view.file_name()
        dirNm, sfn = os.path.split(uri)
        ext = os.path.splitext(uri)[1][1:]
        if "php" != ext:
            print("phpfmt (vet): not a PHP file")
            return False


        php_bin = s.get("php_bin", "php")
        vetPath = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "vet.php")
        cmdVet = [php_bin]
        cmdVet.append(vetPath)
        cmdVet.append(view.file_name())
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmdVet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirNm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmdVet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirNm, shell=False)
        res, err = p.communicate()
        print("phpfmt (vet): "+res.decode('utf-8'))
        print("phpfmt (vet) err: "+err.decode('utf-8'))
        if len(res.decode('utf-8')) > 0:
            outputToPanel("phpfmtvet", self, edit, res.decode('utf-8'));
            # errors = res.decode('utf-8').split('\n')
            # x = csv.reader(errors)
            # regions = []
            # for row in x:
            #     line = self.view.full_line(self.view.text_point(row[1],0))
            #     regions.append(line)
            # view.erase_regions("vet")
            # view.add_regions("vet", [line], "comment", "dot")
            # print(view.get_regions("vet"))
            # print("draw line")
        else:
            hidePanel("phpfmtvet", self, edit)

class BuildOracleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def buildDB():
            if self.msgFile is not None:
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

        self.msgFile = None
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

def _ct_poller():
    s = sublime.load_settings('phpfmt.sublime-settings')
    if s.get("calltip", False):
        try:
            view = sublime.active_window().active_view()
            view.run_command('calltip')
        except Exception:
            pass
        sublime.set_timeout(_ct_poller, 5000)

_ct_poller()