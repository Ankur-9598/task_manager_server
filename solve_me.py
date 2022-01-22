import collections
from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            for line in file.readlines():
                completed_task = line[:-1]
                self.completed_items.append(completed_task);
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        try:
            if len(args) == 0:
                raise Exception("Priority and Task name is not given!")

            if len(args) == 1:
                raise Exception("Task name is not provided!")

            curr_priority = int(args[0])
            curr_task = args[1]

            print(f'Added task: "{curr_task}" with priority {curr_priority}')

            while(self.current_items.get(curr_priority)):
                temp_task_name = self.current_items.get(curr_priority)
                self.current_items[curr_priority] = curr_task
                curr_task = temp_task_name
                curr_priority += 1
            
            self.current_items[curr_priority] = curr_task
            self.write_current()

        except TypeError:
            print("Error: No prority and task name is given!")

        except Exception as e:
            print(e)

    def done(self, args):
        try:
            task_priority = int(args[0])
            if not self.current_items.get(task_priority):
                raise Exception(f"Error: no incomplete item with priority {task_priority} exists.")
            
            completed_task = self.current_items[task_priority]
            self.completed_items.append(completed_task)
            self.write_completed()

            self.current_items.pop(task_priority)
            self.write_current()

            print("Marked item as done.")
        
        except TypeError:
            print("Error: No task priority is given to mark done!")

        except Exception as e:
            print(e)

    def delete(self, args):
        try:
            task_priority = int(args[0])
            if not self.current_items.get(task_priority):
                raise Exception(f"Error: item with priority {task_priority} does not exist. Nothing deleted.")

            self.current_items.pop(task_priority)
            print(f"Deleted item with priority {task_priority}")

        except TypeError:
            print("No task priority given!")

        except Exception as e:
            print(e)

    def ls(self):
        if len(self.current_items) == 0:
            print("No incomplete tasks!")
            return
        for index, priority in enumerate(self.current_items):
            print(f"{index + 1}. {self.current_items[priority]} [{priority}]")

    def report(self):
        pending_task_cnt = len(self.current_items)
        print(f"Pending : {pending_task_cnt}")
        self.ls()
        print()

        completed_task_cnt = len(self.completed_items)
        print(f"Completed : {completed_task_cnt}")
        for index, completed_task in enumerate(self.completed_items):
            print(f"{index + 1}. {completed_task}")

    def render_pending_tasks(self):
        self.read_current()
        content_header = self.header("Incompleted Tasks")
        content_list = ""
        if len(self.current_items) == 0:
            content_list += "<h3>All tasks completed.</h3>"
        else:
            content_list = "<ol>"
            for priority in self.current_items:
                content_list += f"<li>{self.current_items[priority]} [{priority}]</li>"
            content_list += "</ol>"

        return content_header + self.add_links(content_list)

    def render_completed_tasks(self):
        self.read_completed()
        content_header = self.header("Completed Tasks")
        content_list = ""
        if len(self.completed_items) == 0:
            content_list += "<h3>No task is completed yet!</h3>"
        else:
            content_list += "<ol>"
            for task in self.completed_items:
                content_list += f"<li>{task}</li>"
            content_list += "</ol>"

        return content_header + self.add_links(content_list)

    def render_add_task(self):
        return """<div>
            <h2>Add Task</h2>
            <form action="add_task" method="get">
                <input type="text" placeholder="Task name" name="task_name" required >
                <input type="number" placeholder="Task priority" name="task_priority" min="1" required >
                <button type="submit">Add</button>
            </form>
        </div>
        """

    def render_done_task(self):
        return """<div>
            <h2>Mark Task Done</h2>
            <form action="done_task" method="get">
                <input type="number" placeholder="Task priority" name="task_priority" min="1" required >
                <button type="submit">Mark Done</button>
            </form>
        </div>
        """

    def header(self, heading):
        return f"<h1>{heading}:-</h1>"

    def add_links(self, content):
        add_page = "<div><a href=\"/add\">Go to Add Task Page</a></div>"
        done_page = "<div><a href=\"/done\">Go to Mark Task Done Page</a></div>"
        return content + add_page + done_page

    def add_go_back(self):
        task_page = "<div><a href=\"/tasks\">See Pending Tasks</a></div>"
        completed_page = "<div><a href=\"/completed\">See Completed Tasks</a></div>"
        return task_page + completed_page


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        elif self.path == "/add":
            content = task_command_object.render_add_task()
        elif self.path.startswith("/add_task?"):
            url_params = self.path.split("?")[1].split("&")
            task_name = url_params[0].split("=")[1].split("+")
            task_name = " ".join(task_name)
            task_priority = url_params[1].split("=")[1]
            args = [task_priority, task_name]
            self.add(args)
            content = f"<h2>Task \"{task_name}\" added with priority {task_priority}</h2>" + task_command_object.add_go_back()
            
        elif self.path == "/done":
            content = task_command_object.render_done_task()
        elif self.path.startswith("/done_task?"):
            url_params = self.path.split("?")[1].split("=")
            task_priority = url_params[1]
            args = [task_priority]
            self.done(args)
            content = f"<h2>Task with priority {task_priority} marked done.</h2>" + task_command_object.add_go_back()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def do_POST(self):
        self._set_headers()
        if self.path == "/add":
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            print(post_body)

        self.send_response(200)
        self.end_headers()
