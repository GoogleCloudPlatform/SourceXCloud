"""Project intermediate infrastructure.
"""

class Project(object):

  def __init__(self, staging_dir, dependencies=None, extensions=None):
    self.staging_dir = staging_dir
    self.dependencies = dependencies or []
    self.extensions = extensions or {}
