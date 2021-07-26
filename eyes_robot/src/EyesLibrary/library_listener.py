from EyesLibrary.base import LibraryComponent


class LibraryListener(LibraryComponent):
    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, name, attrs):
        self._create_eyes_runner_if_needed()

    def end_suite(self, name, attrs):
        print(self.ctx.eyes_runner.get_all_test_results())

    def start_test(self, name, attrs):
        ...
        # dispatch("scope_start", attrs["longname"])

    def end_test(self, name, attrs):
        ...
        # dispatch("scope_end", attrs["longname"])
