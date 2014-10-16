from dexy.wrapper import Wrapper
import os

class SupplementaryWrapper(Wrapper):
    """
    Wrapper which will add its files and work to an existing set of caches
    rather than work from scratch
    """
    def check(self):
        if not os.path.exists(self.this_cache_dir()):
            self.create_cache_dir_with_sub_dirs(self.this_cache_dir())

        # Load information about arguments from previous batch.
        self.load_node_argstrings()

        self.check_cache()

        # Save information about this batch's arguments for next time.
        self.save_node_argstrings()

    def run(self):
        if self.target:
            matches = self.roots_matching_target()
        else:
            matches = self.roots

        for node in matches:
            for task in node:
                task()

