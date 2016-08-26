import sublime, sublime_plugin
import subprocess, os, re

def load_settings():
  global settings
  settings = sublime.load_settings('GitOpenChangedFiles.sublime-settings')

class GitOpenChangedFiles(sublime_plugin.TextCommand):
  def print_with_status(self, message):
    sublime.status_message(message)
    print(message)

  def print_with_error(self, error_message):
    sublime.error_message(error_message)
    print(error_message)

  def system_folder_seperator(self):
    if sublime.platform() == "windows":
      return "\\\\"
    else:
      return "/"

  # http://stackoverflow.com/questions/9877462/is-there-a-python-equivalent-to-the-which-command
  def which(self, program_name):
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, program_name)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p

  def run(self, edit):
    sublime.run_command('refresh_folder_list')
    current_folder = sublime.active_window().folders()[0]

    if sublime.platform() == "windows":
      git_name = 'git.exe'
    else:
      git_name = 'git'

    git_path = self.which(git_name)

    if not git_path:
      self.print_with_error("git not found in PATH")
      return

    compare_branch_to = settings.get('compare_branch_to', 'master...')

    pr = subprocess.Popen("git diff --name-only "+compare_branch_to , cwd = current_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    (filenames, error) = pr.communicate()

    if error:
      self.print_with_error('Could not run git command. Ensure you have git properly installed: ' + str(error))
      return
    else:
      filenames_split = bytes.decode(filenames).splitlines()
      filename_pattern = re.compile("([^" + self.system_folder_seperator() + "]+$)")
      sorted_filenames = sorted(filenames_split, key=lambda fn: filename_pattern.findall(fn))

      for file_modified in sorted_filenames:
        filename = current_folder + self.system_folder_seperator() + file_modified
        if os.path.isfile(filename):
          sublime.active_window().open_file(filename)

      self.print_with_status("Git: Opened files modified in branch")

load_settings()
