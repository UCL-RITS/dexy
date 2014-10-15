from dexy.reporters.website import Website
from jinja2 import FileSystemLoader
from wrapper import SupplementaryWrapper
from dexy.utils import safe_cwd
import os

class SupplementaryReporter(Website):
    """
    Acts like website reporter, but accepts additional template
    materials from some other location, merging in the contents of the
    .dexy file and other materials from that location.
    Use to write a template only once which you intend to apply to
    many websites
    """
    aliases = ['supplementary']
    _settings = {
        "supplementary-location" : ("Path to find supplementary files", os.path.dirname(__file__))
    }
    def setup(self):
        super(SupplementaryReporter, self).setup()
        self.add_indigo_nodes()

    def jinja_environment(self, template_path, additional_args=None):
        env = super(SupplementaryReporter, self).jinja_environment(template_path, additional_args)
        dirs = [".", self.setting('supplementary-location'), os.path.dirname(template_path)]
        env.loader = FileSystemLoader(dirs)
        return env

    def add_indigo_nodes(self):
        # Create a new wrapper object which dexifies the supplementary project folder
        # with cache objects etc being generated into the current cache, not a new one
        current_artifacts =  os.path.realpath(self.wrapper.artifacts_dir)
        with safe_cwd(self.setting('supplementary-location')):
           wrapper = SupplementaryWrapper()
           wrapper.artifacts_dir = current_artifacts
           wrapper.writeanywhere = True
           wrapper.run_from_new()
        # Copy the nodes and filemap from the new wrapper into the main wrapper
        # so that they are picked up by the reporter.
        self.wrapper.filemap.update(wrapper.filemap)
        self.wrapper.nodes.update(wrapper.nodes)
        for node in wrapper.nodes.values():
            self.wrapper.batch.add_doc(node)

