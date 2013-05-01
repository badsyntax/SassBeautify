# SassBeautify :: Beautify your Sass! (or Scss!)
# Author: Richard Willis (willis.rh@gmail.com)
# https://github.com/badsyntax/SassBeautify
# Depends on the `sass-convert` utility

import os, commands, subprocess
import sublime, sublime_plugin

class SassBeautifyCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    self.save()
    self.beautify(edit)

  def save(self):
    self.view.run_command("save")

  def showerror(self, message):
    sublime.error_message('There was an error beautifying your Sass.\n\n' + message);

  def generate_cmd(self, ext):
    return [
      'sass-convert', self.view.file_name(),
      '-T', ext,
			'--indent', '4'
    ]

  def update_sass(self, sass, edit):
    if len(sass) > 0:
      self.view.replace(edit, sublime.Region(0, self.view.size()), sass.decode('utf-8'))
      sublime.set_timeout(self.save, 100)

  def beautify_windows(self, cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    return p.returncode, output or err

  def beautify_linux(self, cmd):
    return commands.getstatusoutput('"'+'" "'.join(cmd)+'"')

  def beautify(self, edit):

    basename, ext = os.path.splitext(self.view.file_name());
    ext = ext.strip('.');

    if ext != 'sass' and ext != 'scss':
      return sublime.error_message('Not a valid Sass file.');

    cmd = self.generate_cmd(ext)

    if sublime.platform() == 'windows':
      exitstatus, output = self.beautify_windows(cmd)
    else:
      exitstatus, output = self.beautify_linux(cmd)

    if exitstatus != 0:
      return self.showerror(output);

    self.update_sass(output, edit)
