# SassBeautify :: Beautify your Sass! (or Scss!)
# Author: Richard Willis (willis.rh@gmail.com)
# https://github.com/badsyntax/SassBeautify
# Depends on the `sass-convert` utility

import os
import subprocess
import sublime
import sublime_plugin

class SassBeautifyCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    # A file has to be saved before beautifying so we can get the conversion
    # type from the file extension.
    if self.view.file_name() == None:
      return sublime.error_message(
        'Please save this file before trying to beautify.'
      );

    self.beautify(edit)

  def generate_cmd(self, ext):

    settings = sublime.load_settings('SassBeautify.sublime-settings')

    cmd = [
      'sass-convert',
      '--unix-newlines',
      '--stdin',
      '--indent', str(settings.get('indent')),
      '--from', ext,
      '--to', ext
    ]

    # Convert underscores to dashes
    if settings.get('dasherize') == True:
      cmd.append('--dasherize')

    # Output the old-style ":prop val" property syntax.
    # Only meaningful when generating Sass
    if settings.get('old') == True and ext == 'sass':
      cmd.append('--old')

    return cmd;

  def exec_cmd(self, ext):

    sublime.status_message('Beautifying, please wait... ')

    text = self.view.substr(sublime.Region(0, self.view.size()))
    cmd = self.generate_cmd(ext)
    shell = sublime.platform() == 'windows'

    p = subprocess.Popen(
      cmd,
      shell=shell,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )

    output, err = p.communicate(input=text)

    return p.returncode, output, err

  def update_sass(self, sass, edit):

    # Although we asked sass-convert to give us unix-style newlines, it refuses
    # to do so when run on windows, so we have to manually convert the
    # windows-style newlines to unix-style.
    sass = sass.replace('\r\n', '\n')

    self.view.replace(
      edit,
      sublime.Region(0, self.view.size()),
      sass.decode('utf-8')
    )

  def get_ext(self):
    basename, ext = os.path.splitext(self.view.file_name());
    return ext.strip('.');

  def save(self):
    self.view.run_command('save')
    sublime.status_message('Sucessfully beautified ' + self.view.file_name())

  def beautify(self, edit):

    ext = self.get_ext();

    if ext != 'sass' and ext != 'scss':
      return sublime.error_message('Not a valid Sass file.');

    exitstatus, output, err = self.exec_cmd(ext)

    if exitstatus != 0:
      return sublime.error_message(
        'There was an error beautifying your Sass.\n\n' + err
      );

    self.update_sass(output, edit)
    sublime.set_timeout(self.save, 1)