# Basic file operations
from os import remove, walk, path
# File cleanup in background
from apscheduler.schedulers.background import BackgroundScheduler


class CleanupDaemon(object):
    """
    CleanupDaemon will start a background daemon to clean a directory if the given
    maximum folder size has been exceeded. It will delete the oldest files in the
    directory until the maximum folder size is respected. Nifti, trk and json files
    will be prioritized.

    :param directory: path for the folder to cleanup
    :param interval: timer in-between cleaning in minutes
    :param dir_size: the maximum folder size to respect
    """
    def __init__(self, directory=".", interval=10, dir_size=10737418240):
        if not path.exists(directory):
            raise ValueError(directory, "doesn't exist.")
        elif not path.isdir(directory):
            raise ValueError(directory, "isn't a directory.")
        self.directory = directory
        self.interval = interval
        self.max_dir_size = dir_size
        self.__sched = None
        self.__launched = False
        self.__daemon_id = "dir_cleaner"

    def __free_dir(self, file_dict, current_dir_size):
        # order files based on last access
        file_dict = {k: v for k, v in sorted(file_dict.items(),
                                             key=lambda item: item[1])}
        final_dir_size = current_dir_size

        for file, access_time in file_dict.items():
            try:
                file_size = path.getsize(file)
                print("  deleting", file)
                remove(file)
                final_dir_size = final_dir_size - file_size
                print("  ... done")
            except Exception as e:
                #print(e)
                print("  ... skipping")
                pass

            if final_dir_size < self.max_dir_size:
                break
        return final_dir_size

    # Daemon function to cleanup tmp directory
    def __dir_cleanup(self):
        print("cleanup starts in", self.directory)
        dir_size = 0
        priority_file_dict = {}
        file_dict = {}
        for dir_name, subdir_list, all_file_names in walk(self.directory):
            for f_name in all_file_names:
                abs_path = f"{dir_name}{path.sep}{f_name}"
                if f_name[0] != '.':
                    f_extension = f_name[f_name.rindex('.') + 1:]
                    if f_extension == "nii" or f_extension == "trk" or f_extension == "json":
                        priority_file_dict[abs_path] = path.getatime(abs_path)
                    else:
                        file_dict[abs_path] = path.getatime(abs_path)
                dir_size = dir_size + path.getsize(abs_path)

        if dir_size > self.max_dir_size:
            dir_size = self.__free_dir(priority_file_dict, dir_size)
            if dir_size > self.max_dir_size:
                self.__free_dir(file_dict, dir_size)

        print("cleanup done")

    def start(self):
        if not self.__launched:
            self.sched = BackgroundScheduler(daemon=True)
            self.sched.add_job(self.__dir_cleanup, 'interval', minutes=self.interval, id=self.__daemon_id)
            self.sched.start()
            self.__launched = True

    def stop(self):
        if self.__launched:
            self.sched.remove_job(self.__daemon_id)
            self.__launched = False

    def __del__(self):
        self.stop()
