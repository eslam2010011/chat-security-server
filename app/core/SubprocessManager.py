import subprocess


class SubprocessManager:
    def __init__(self):
        self.processes = []

    def start_process(self, command):

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   shell=True)
        self.processes.append(process)

    def stop_all_processes(self):
        for process in self.processes:
            process.terminate()
        self.processes = []

    def get_all_output(self):
        output = []
        for process in self.processes:
            out, err = process.communicate()

            output.append(out.decode('utf-8'))
        self.processes = []
        return output

    def get_live_output(self):
        output = []
        for process in self.processes:
            while True:
                line = process.stdout.readline().decode('utf-8')
                if not line:
                    break
                output.append(line.rstrip('\n'))
        return output
