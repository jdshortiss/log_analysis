import time, re, os
import plotly.graph_objects as go

class Render_log:

    def __init__(self, filename: str, path: str):
        self.name = filename
        self.path = path
        self.file = self.read_file()

    def read_file(self):
        with open(self.path + '/' + self.name) as file:
            lines = file.readlines()
        return lines

    def get_time_utilization(self, times: list):

        t = []
        k = []
        util = []
        k_util = []

        for line in self.file:
            for key in times:

                if key in line:

                    if "|" in line:
                        v = line.split("|")[1].split()
                    else:
                        v = line.split()

                    t.append([x for x in v if self.isTimeFormat_hour(x)
                              or self.isTimeFormat_wo_hour(x)])
                    k.append(key)

                    machine_util = re.findall('\d*%', line)

                    if machine_util:
                        util.append(machine_util)
                        k_util.append(key)

        times = dict(zip(k, t))
        machine_utilization = dict(zip(k_util, util))

        return times, machine_utilization

    def get_errors_warnings(self, tags: list):

        tagged_lines = [line[:-1] for line in self.file for tag in tags
                        if tag in line]

        return tagged_lines

    def get_user(self):
        user = re.findall('[a-zA-Z0-9]\S*@\S*[a-zA-Z]', self.file[0])
        user = user[0].split('/')

        return user[-1:][0]

    def get_title(self):
        for line in self.file:

            if "Title" in line:
                v = line.split()

        return v[-1:][0]

    def get_memory(self):

        m = []

        for line in self.file:
            if 'Peak cache memory' in line:
                if "|" in line:
                    v = line.split("|")[1].split()
                else:
                    v = line.split()

                m.append([x for x in v if self.isFloat(x) or x == 'GB' or x == 'MB'])

        m = [item for sublist in m for item in sublist]
        memory = "".join(m)

        return memory

    def isTimeFormat_hour(self, input):
        try:
            time.strptime(input, '%H:%M:%S.%f')

            return True

        except ValueError:

            return False

    def isTimeFormat_wo_hour(self, input):
        try:
            time.strptime(input, '%M:%S.%f')

            return True

        except ValueError:

            return False

    def isFloat(self, input):
        try:
            float(input)

            return True

        except ValueError:

            return False


class Logs_in_dir:

    def __init__(self, path: str):
        self.directory = path

    def get_logs(self):
        included_extensions = ['log']

        log_names = [ln for ln in os.listdir(self.directory) if
                     any(ln.endswith(ext) for ext in included_extensions)]

        return log_names


def get_utilization_gauge(sc_utilization_int: int, name: str, log_name: str):
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=sc_utilization_int,
        mode="gauge+number",
        title={'text': name},
        gauge={'axis': {'range': [None, 100]},
               'steps': [
                   {'range': [0, 50], 'color': "lightgray"},
                   {'range': [50, 75], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}}))
    fig.write_image("images/" + log_name + " " + name + " %.png")