import sublime
import sublime_plugin
import re

if sublime.version() > "3000":
    from .julia_unicode import latex_symbols, emoji_symbols
else:
    from julia_unicode import latex_symbols, emoji_symbols


CONTAINS_COMPLETIONS = re.compile(r".*(\\[:_0-9a-zA-Z+-^]*)$")
symbols = latex_symbols + emoji_symbols


def get_prefix(view):
    sel = view.sel()[0]
    pt = sel.end()
    line = view.substr(sublime.Region(view.line(pt).begin(), pt))
    m = CONTAINS_COMPLETIONS.match(line)
    if m:
        return m.group(1)
    else:
        return None


class JuliaUnicodeListener(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if view.settings().get('is_widget'):
            return

        if view.score_selector(locations[0], "source.julia") == 0:
            return None

        prefix = get_prefix(view)
        if not prefix:
            return None
        ret = [(s[0] + "\t" + s[1], s[1]) for s in symbols if s[0].startswith(prefix)]
        return ret

    def on_query_context(self, view, key, operator, operand, match_all):
        if view.settings().get('is_widget'):
            return

        if key == 'julia_unicode_only_match':
            prefix = get_prefix(view)
            count = 0
            for s in symbols:
                if s[0].startswith(prefix):
                    count = count + 1
            return (count == 1) == operand
        elif key == 'julia_unicode_has_prefix':
            prefix = get_prefix(view)
            return (prefix is not None) == operand

        return None


class JuliaUnicodeInsertBestCompletion(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.run_command("insert_best_completion",  {"default": "\t", "exact": False})
        for sel in view.sel():
            pt = sel.begin()
            if view.substr(sublime.Region(pt-3, pt-1)) == "\\:":
                view.replace(edit, sublime.Region(pt-3, pt-1), "")


class JuliaUnicodeAutoComplete(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.run_command("auto_complete")
        for sel in view.sel():
            pt = sel.begin()
            if view.substr(sublime.Region(pt-3, pt-1)) == "\\:":
                view.replace(edit, sublime.Region(pt-3, pt-1), "")


class JuliaUnicodeCommitComplete(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.run_command("commit_completion")
        for sel in view.sel():
            pt = sel.begin()
            if view.substr(sublime.Region(pt-3, pt-1)) == "\\:":
                view.replace(edit, sublime.Region(pt-3, pt-1), "")
