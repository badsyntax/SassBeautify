import commands, subprocess
import sublime, sublime_plugin

class SassBeautifyCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.save()
    self.beautify(edit)

  def save(self):
    self.view.run_command("save")

  def beautify(self, edit):

    cmd = ["sass-convert",self.view.file_name(),"-T","scss"]

    if sublime.platform()=='windows':
      p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
      html = p.communicate()[0]
    # TODO: test this works on Linux/OSX
    else:
      html = commands.getoutput('"'+'" "'.join(cmd)+'"')

    if len(html) > 0:
      self.view.replace(edit, sublime.Region(0, self.view.size()), html.decode('utf-8'))
      sublime.set_timeout(self.save, 100)
    # TODO: we should be checking STDERR and display that back to the user instead
    else:
      sublime.error_message('There was an error beautifying your Scss. Check for syntax errors.')