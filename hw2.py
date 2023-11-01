import time as ti
import tkinter as tk
import hashlib
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator
import numpy as np

#Each process is an object with the following attributes
class process:
    def __init__(self, name, arrival_time, burst_time, priority, wait_time=0):
        self.name = name
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.priority = int(priority)
        self.wait_time = int(wait_time)

    def print_process(self):
        print(str(self.name) + ' ' + str(self.arrival_time) + ' ' + str(self.burst_time) + ' ' + str(self.priority) + ' wait time is: ' + str(self.wait_time))
        return

#prints a list of processes
def print_process_list(arr):
    for p in arr:
        p.print_process()

#reads from a csv of processes where the order is:
# name, arrival time, burst_time, priority, wait time (optional, defaults to 0)
def get_processes(file_path):
    processes = []
    with open(file_path, 'r') as file:
        for line in file:
            contents = line.split(',')
            p = process(contents[0],contents[1],contents[2],contents[3])
            processes.append(p)
    return processes

#finds processes whos arrival time = current time from the incoming processes
def find_process(processes,time):
    found = []
    for p in processes:
        if p.arrival_time == time:
            found.append(p)

    if len(found) > 0:
        return found
    else:
        return False

#performs a shortest job first cpu scheduler simulation
def SJF(processes, window, canvas):
    # declare initial values
    time = 0
    incoming = processes
    ready_queue = []
    results = []
    running = []
    stats = []
    curr_anims = False
    prev_run = None  # Change to None initially

    # while there are processes incoming, in ready queue, or running, the scheduler runs
    while incoming or ready_queue or running:
        # check if any processes can join the ready queue and add them
        add_to_queue = find_process(incoming, time)
        if add_to_queue:
            for p in add_to_queue:
                ready_queue.append(p)
                incoming.remove(p)
        
        # if no process is running, find one to schedule
        if not running:
            if ready_queue:
                shortest_p = min(ready_queue, key=lambda p: p.burst_time)
                running.append(shortest_p)
                ready_queue.remove(shortest_p)

        # if a process is running (or one was just added and started running)
        if running:
            running[0].burst_time -= 1
            for p in ready_queue:
                p.wait_time += 1

            total_wait = sum(p.wait_time for p in ready_queue)
            stats.append([time, total_wait])

            if time == 0 and not curr_anims:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, False, time, running, prev_run,False)
            else:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, curr_anims, time, running, prev_run,False)

            # if the process is done running, add it to the results and store previous running
            if running[0].burst_time == 0:
                results.append(running[0])
                prev_run = running[:]  # Create a copy of the running list
                running = []
            else:
                prev_run = running[:]

        time += 1
        ti.sleep(0.05)

    update_anim(window, canvas, ready_queue, incoming, curr_anims, time, False, prev_run,True)
    return results, stats

def STR(processes, window, canvas):
    # declare initial values
    time = 0
    incoming = processes
    ready_queue = []
    results = []
    running = []
    stats = []
    curr_anims = False
    prev_run = None  # Change to None initially

    # while there are processes incoming, in ready queue, or running, the scheduler runs
    while incoming or ready_queue or running:
        # check if any processes can join the ready queue and add them
        add_to_queue = find_process(incoming, time)
        if add_to_queue:
            for p in add_to_queue:
                ready_queue.append(p)
                incoming.remove(p)

        # if no process is running, find one to schedule
        if ready_queue:
            shortest_p = min(ready_queue, key=lambda p: p.burst_time)
            if running:
                if shortest_p.burst_time < running[0].burst_time:
                    preempt = running.pop(0)
                    ready_queue.append(preempt)
                    running.append(shortest_p)
                    ready_queue.remove(shortest_p)
            else:
                running.append(shortest_p)
                ready_queue.remove(shortest_p)

        # if a process is running (or one was just added and started running)
        if running:
            running[0].burst_time -= 1
            for p in ready_queue:
                p.wait_time += 1

            total_wait = sum(p.wait_time for p in ready_queue)
            stats.append([time, total_wait])

            if time == 0 and not curr_anims:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, False, time, running, prev_run,False)
            else:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, curr_anims, time, running, prev_run,False)


            # if the process is done running, add it to the results and store previous running
            if running[0].burst_time == 0:
                results.append(running[0])
                prev_run = running[:]  # Create a copy of the running list
                running = []
            else:
                prev_run = running[:]

        time += 1
        ti.sleep(0.05)

    update_anim(window, canvas, ready_queue, incoming, curr_anims, time, False, prev_run,True)
    return results, stats

def round_robin(processes, window, canvas, time_q):
    time = 0
    incoming = processes
    ready_queue = []
    results = []
    running = []
    stats = []
    curr_anims = False
    prev_run = None
    multiples = [time_q * i for i in range(1, 300 + 1)]
    cycle = 0

    while incoming or ready_queue or running:
        add_to_queue = find_process(incoming, time)
        if add_to_queue:
            for p in add_to_queue:
                ready_queue.append(p)
                incoming.remove(p)

        if not running and ready_queue:
            running.append(ready_queue.pop(0))

        if cycle == time_q-1:
            preempt = running.pop(0)
            ready_queue.append(preempt)
            running.append(ready_queue.pop(0))
            cycle = 0
            
        if running:
            running[0].burst_time -= 1
            if time == 0:
                pass
            elif prev_run[0].name == running[0].name:
                cycle = cycle + 1

            for p in ready_queue:
                p.wait_time += 1

            total_wait = sum(p.wait_time for p in ready_queue)
            stats.append([time, total_wait])

            if time == 0 and not curr_anims:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, False, time, running, prev_run, False)
            else:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, curr_anims, time, running, prev_run, False)

            if running[0].burst_time == 0:
                cycle = 0
                results.append(running[0])
                prev_run = running[:]  # Create a copy of the running list
                running = []
            else:
                prev_run = running[:]

        

        time += 1
        ti.sleep(0.05)

    update_anim(window, canvas, ready_queue, incoming, curr_anims, time, False, prev_run, True)
    return results, stats


def round_robin_priority(processes, window, canvas, time_q):
    time = 0
    incoming = processes
    ready_queue = []
    results = []
    running = []
    stats = []
    curr_anims = False
    prev_run = None
    multiples = [time_q * i for i in range(1, 300 + 1)]
    cycle = 0
    rr = []

    while incoming or ready_queue or running:
        add_to_queue = find_process(incoming, time)
        if add_to_queue:
            for p in add_to_queue:
                ready_queue.append(p)
                incoming.remove(p)

        if not running and ready_queue:
            lowest_p = min(ready_queue, key=lambda p: p.priority) 
            running.append(lowest_p)
            ready_queue.remove(lowest_p)

        for p in ready_queue:
            if p.priority == running[0].priority:    
                if cycle == time_q-1:
                    preempt = running.pop(0)
                    ready_queue.append(preempt)
                    running.append(p)
                    ready_queue.remove(p)
                    cycle = 0
                    break
            
        if running:
            running[0].burst_time -= 1
            if time == 0:
                pass
            elif prev_run[0].name == running[0].name:
                cycle = cycle + 1

            for p in ready_queue:
                p.wait_time += 1

            total_wait = sum(p.wait_time for p in ready_queue)
            stats.append([time, total_wait])

            if time == 0 and not curr_anims:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, False, time, running, prev_run, False)
            else:
                curr_anims = update_anim(window, canvas, ready_queue, incoming, curr_anims, time, running, prev_run, False)

            if running[0].burst_time == 0:
                cycle = 0
                results.append(running[0])
                prev_run = running[:]  # Create a copy of the running list
                running = []
            else:
                prev_run = running[:]

        

        time += 1
        ti.sleep(1)

    update_anim(window, canvas, ready_queue, incoming, curr_anims, time, False, prev_run, True)
    return results, stats

def update_anim(window,canvas,ready_queue,incoming,anims,time,running,prev_run,last_run):
    def quit_me():
        window.quit()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", quit_me)
    def handle_queues():
        def draw_stack(width,height,xroot,yroot,array,anims):
            if anims:
                for key,values in anims.items():
                    for item in values:
                        canvas.delete(item)
            curr = {}
            assets = []
            w = width
            h = height
            x = xroot
            y = yroot
            for process in array:
                box = canvas.create_rectangle(x, y, x+w, y+h, fill="teal", outline="black")
                text_name = canvas.create_text(x+50,y+15,text=process.name,font=('Arial','12'))
                text_burst_time = canvas.create_text(x+50,y+40,text="burst time: " + str(process.burst_time),font=('Arial','12'))
                #text_wait_time = canvas.create_text(x+50,y+50,text="wait time: " + str(process.wait_time),font=('Arial','12'))
                text_priority = canvas.create_text(x+50,y+60,text="priority: " + str(process.priority),font=('Arial','12'))
                assets.append(box)
                assets.append(text_name)
                assets.append(text_burst_time)
                #assets.append(text_wait_time)
                assets.append(text_priority)
                name = process.name
                curr[name] = assets
                y = y + h + 10
                window.update()
                assets = []

            return curr
        
        ready_col1 = []
        ready_col2 = [] 
        for i in range(len(ready_queue)):
            if i < 8:
                ready_col1.append(ready_queue[i])
            else:
                ready_col2.append(ready_queue[i])

        incoming_col1 = []
        incoming_col2 = []
        for i in range(len(incoming)):
            if i < 8:
                incoming_col1.append(incoming[i])
            else:
                incoming_col2.append(incoming[i])

        boxes = {}
        boxes1 = draw_stack(100,80,1100,50,ready_col1,anims)
        boxes2 = draw_stack(100,80,1210,50,ready_col2,anims)
        boxes3 = draw_stack(100,80,1350,50,incoming_col1,anims)
        boxes4 = draw_stack(100,80,1460,50,incoming_col2,anims)

        boxes.update(boxes1)
        boxes.update(boxes2)
        boxes.update(boxes3)
        boxes.update(boxes4)
        return boxes
    
    def handle_gnatt():
        def draw_gnatt(width,height,xroot,yroot,running):
            w = width
            h = height
            x = xroot
            y = yroot 
            curr_proc = running
            print(time)
        
            if last_run:
                line = canvas.create_line(x,y,x,y+h+10)
                canvas.create_text(x,y+h+20,text=str(time),font=('Arial','10'))
                canvas.tag_raise(line)
            else:
                block_value = int(hashlib.sha256(running[0].name.encode()).hexdigest(), 16)
                block_color = "#{:06x}".format(block_value % 0x1000000)

                canvas.create_rectangle(x, y, x+w, y+h, fill=block_color, outline=block_color)
                canvas.create_text(x+50,y+35,text=running[0].name,font=('Arial','12'))
                
                if time == 0:
                    #line = canvas.create_line(x+w+1,y,x+w+1,y+h+10)
                    #canvas.tag_raise(line)
                    canvas.create_text(x-w+1,y-h+20,text=str(time),font=('Arial','10'))
                elif (running[0].name != prev_run[0].name):
                    line = canvas.create_line(x,y,x,y+h+10)
                    canvas.tag_raise(line)
                    canvas.create_text(x,y+h+20,text=str(time),font=('Arial','10'))

                if prev_run != None:
                    print('prev: ' + prev_run[0].name + 'current: ' + running[0].name)
                else:
                    print('current: ' + running[0].name)

            
            window.update()

        if time in range(0,10):
            xroot = 25 + (105 * time)
            yroot = 125
            draw_gnatt(105,75,xroot,yroot,running)
        elif time in range(10,20):
            xroot = 25 + (105 * (time - 10))
            yroot = 125 * 2
            draw_gnatt(105,75,xroot,yroot,running)
        elif time in range(20,30):
            xroot = 25 + (105 * (time - 20))
            yroot = 125 * 3
            draw_gnatt(105,75,xroot,yroot,running)
        elif time in range(30,40):
            xroot = 25 + (105 * (time - 30))
            yroot = 125 * 4
            draw_gnatt(105,75,xroot,yroot,running)
        elif time in range(40,50):
            xroot = 25 + (105 * (time - 40))
            yroot = 125 * 5
            draw_gnatt(105,75,xroot,yroot,running)

    all = {}
    all_q = handle_queues()
    all_g = handle_gnatt()
    all.update(all_q)

    return all

        

    
    

def make_window():
    # Create the main window
    window = tk.Tk()
    window.title("CPU Scheduler animation")
    window.geometry("1600x800")

    # Calculate the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates for centering the window
    x = (screen_width - 1600) // 2  # Adjust 1600 to your desired width
    y = (screen_height - 800) // 2  # Adjust 800 to your desired height

    # Set the window's position
    window.geometry(f"1600x800+{x}+{y}")

    C = tk.Canvas(window, bg="white", height=900, width=1600)

    C.create_text(1200,25,text="Ready Queue",font=('Arial','16'))
    C.create_text(1450,25,text="Incoming Processes",font=('Arial','16'))
    C.create_rectangle(25, 125, 1075, 200, fill="white", outline="black")
    C.create_text(25,210,text="0",font=('Arial','10'))

    C.pack()

    return window, C

def make_start():
    def validate_input(action, value_if_allowed):
        if action == '1':  # Insert action
            if value_if_allowed.isdigit() or value_if_allowed == "":
                return True
            else:
                return False
        return True

    def on_validate(P):
        if P.isdigit() or P == "":
            return True
        else:
            return False

    start = tk.Tk()
    start.title("CPU Scheduler Selection")
    start.geometry("800x800")

    start_frame = tk.Frame(start, padx=20, pady=20)
    start_frame.grid(row=0, column=0, sticky="ns")

    label = tk.Label(start_frame, text='Choose an Algorithm:', font=('Arial', '14'))
    label.grid(row=0, column=0)

    selected_algorithm_var = tk.StringVar(value="Shortest Job First")
    selected_algorithm = None
    time_quantum_var = tk.StringVar(value="")

    def close_window():
        start.quit()

    def proceed():
        nonlocal selected_algorithm
        selected_algorithm = selected_algorithm_var.get()
        if selected_algorithm == "Round Robin" or selected_algorithm == "Round Robin (Priority)":
            time_quantum = time_quantum_var.get()
            if time_quantum.isdigit():
                selected_algorithm = [selected_algorithm,time_quantum]
            else:
                selected_algorithm = None
                return

        start.destroy()

    vcmd = start.register(validate_input)
    entry = tk.Entry(start_frame, textvariable=time_quantum_var, validate="key", validatecommand=(vcmd, '%d', '%P'))
    entry.grid(row=5, column=1)

    proceed_button = tk.Button(start_frame, text="Proceed", command=proceed)
    proceed_button.grid(row=6, column=0)

    # Create a dropdown (OptionMenu) for algorithm selection
    algorithms = ["Shortest Job First", "Shortest Time Remaining", "Round Robin", "Round Robin (Priority)"]
    option_menu = tk.OptionMenu(start_frame, selected_algorithm_var, *algorithms)
    option_menu.grid(row=2, column=0)

    label = tk.Label(start_frame, text='or', font=('Arial', '14'))
    label.grid(row=4, column=0)

    label = tk.Label(start_frame, text='Round Robin with t=', font=('Arial', '14'))
    label.grid(row=5, column=0)

    start.wait_window(start)
    return selected_algorithm


def display_results(window,results,processes,stats):
    top = tk.Toplevel()
    top.geometry("1850x700")

    def quit_me():
        top.quit()
        top.destroy()

    top.protocol("WM_DELETE_WINDOW", quit_me)
    top.title("Top-level Window")    
    def display_left():
       
        # Create labels and values for the results

        total_wait = 0
        for p in results:
            total_wait = total_wait + p.wait_time

        total_run_time = 0
        for p in processes:
            total_run_time = total_run_time + p.burst_time

        avg_wait = total_wait/len(results)

        labels = ["Total Wait Time:", "Total Time:", "Average Wait Time:","Total Processes:"]
        values = [str(total_wait), str(total_run_time), str(avg_wait), str(len(processes))]

        results_frame = tk.Frame(top,padx=20,pady=20)
        results_frame.grid(row=0,column=0, sticky="ns")
        # Create a grid layout to organize labels and values

        for i in range(len(labels)):
            label = tk.Label(results_frame, text=labels[i],font=('Arial','14'), anchor="w")
            
            if float(values[i]) > 60 and not labels[i]=="Total Processes:":
                both = divmod(float(values[i]),60)
                mins = str(int(both[0]))
                secs = str(int(both[1]))
                value = tk.Label(results_frame, text=mins + 'min ' + secs + 's'    ,font=('Arial','12'), anchor="w")
            elif labels[i] != "Total Processes:":
                value = tk.Label(results_frame, text=values[i]+'s',font=('Arial','12'), anchor="w")
            elif labels[i] == "Total Processes:":
                value = tk.Label(results_frame, text=values[i],font=('Arial','12'), anchor="w")
            
            label.grid(row=i, column=2,padx=0,pady=0)
            value.grid(row=i, column=3)
        
       # results_frame = tk.Frame(top,padx=20,pady=5)
       # results_frame.grid(row=1,column=0,sticky="w")

        title_label = tk.Label(results_frame, text='Process List:',font=('Arial','14'))
        title_label.grid(row=4,column=2,pady=10)

        name_header = tk.Label(results_frame, text='Name',font=('Arial','12'))
        name_header.grid(row=5,column=0,padx=2,pady=0)

        arrival_header = tk.Label(results_frame, text='Arrival Time',font=('Arial','12'))
        arrival_header.grid(row=5,column=1,padx=2,pady=0)

        burst_header = tk.Label(results_frame, text='Burst Time',font=('Arial','12'))
        burst_header.grid(row=5,column=2,padx=2,pady=0)

        priority_header = tk.Label(results_frame, text='Priority',font=('Arial','12'))
        priority_header.grid(row=5,column=3,padx=2,pady=0)

        total_wait_header = tk.Label(results_frame, text='Total Wait',font=('Arial','12'))
        total_wait_header.grid(row=5,column=4,padx=2,pady=0)

        for i in range(len(processes)):
            name_label = tk.Label(results_frame, text=str(processes[i].name),font=('Arial','12'))
            name_label.grid(row=i+7, column=0, padx=10,pady=2)

            arrival_label = tk.Label(results_frame, text=str(processes[i].arrival_time)+'s',font=('Arial','12'))
            arrival_label.grid(row=i+7, column=1, padx=10,pady=2)

            burst_label = tk.Label(results_frame, text=str(processes[i].burst_time)+'s',font=('Arial','12'))
            burst_label.grid(row=i+7, column=2, padx=10,pady=2)

            priority_label = tk.Label(results_frame, text=str(processes[i].priority),font=('Arial','12'))
            priority_label.grid(row=i+7, column=3, padx=10,pady=2)

            for p in results:
                if p.name == processes[i].name:
                    total_wait = p.wait_time

            total_wait_label = tk.Label(results_frame, text=str(total_wait)+'s',font=('Arial','12'))
            total_wait_label.grid(row=i+7, column=4, padx=10,pady=2)


        label = tk.Label(top, text="This is a top-level window with a label")

    def display_chart():
        chart_frame = tk.Frame(top, padx=20, pady=75)
        chart_frame.grid(row=0, column=1, sticky="nsew")  # Make it span the right side

        x = [point[0] for point in stats]
        y1 = [point[1] for point in stats]

        fig, ax1 = plt.subplots()
        ax1.plot(x, y1, marker='o', linestyle='-')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Total Wait')
        ax1.set_title('Current Wait Time in Queue at x')

        # Modify the stats for the second graph
        cumulative_total = []
        total = 0

        for point in stats:
            total += point[1]
            cumulative_total.append(total)
        y2 = cumulative_total

        fig2, ax2 = plt.subplots()
        ax2.plot(x, y2, marker='o', linestyle='-')
        ax2.set_xlabel('Time')
        ax2.set_title('Total wait time')

        major_locator = MultipleLocator(base=5)
        ax1.xaxis.set_major_locator(major_locator)
        ax2.xaxis.set_major_locator(major_locator)
        ax1.yaxis.set_major_locator(major_locator)
        #ax2.yaxis.set_major_locator()
        
        canvas1 = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas1.get_tk_widget().grid(row=0, column=0)  # Adjust row and column as needed

        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.get_tk_widget().grid(row=0, column=1)  # Adjust row and column as needed

        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)
    
    display_left() 
    display_chart()

    return




def main():
    processes = get_processes('processes.txt')
    selected_algorithm = make_start()
    print("Selected Algorithm:", selected_algorithm)

    window, C = make_window()

    if selected_algorithm == 'Shortest Job First':
        results, stats = SJF(processes,window,C)
        processes = get_processes('processes.txt')
        display_results(window,results,processes,stats)

    elif selected_algorithm == 'Shortest Time Remaining':
        print('gulp')
        results, stats = STR(processes,window,C)
        processes = get_processes('processes.txt')
        display_results(window,results,processes,stats)

    elif selected_algorithm[0] == 'Round Robin':
        print('guldsdasdasdasdasdp')
        time_quantum = int(selected_algorithm[1])
        results, stats = round_robin(processes,window,C,time_quantum)
        processes = get_processes('processes.txt')
        display_results(window,results,processes,stats)

    elif selected_algorithm[0] == 'Round Robin (Priority)':
        print(selected_algorithm[1])
        time_quantum = int(selected_algorithm[1])
        results, stats = round_robin_priority(processes,window,C,time_quantum)
        processes = get_processes('processes.txt')
        display_results(window,results,processes,stats)
    
    
    window.mainloop()

main()
