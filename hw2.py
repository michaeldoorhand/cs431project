import time as ti
import tkinter as tk
import hashlib
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
def SJF(processes,window,canvas):
    #declare initial values
    time = 0
    incoming = processes
    ready_queue = []
    results = []
    running = []
    curr_anims = False

    #while there is processes to join the ready queue, 
    #processes in the ready queue, or a process is running the scheduler must run
    while (incoming or ready_queue) or running:
        #print('Current time: ' + str(time))
        #check if any processes can join the ready queue and add them
        add_to_queue = find_process(incoming,time)
        if add_to_queue:
            for p in add_to_queue:
                #print (p.name + ' ADDED')
                ready_queue.append(p)
                incoming.remove(p)

        #if no process is running go find one to schedule
        if not running:
            #if we have any processes in the queue, find the shortest one
            if ready_queue:
                shortest_p = ready_queue[0]
                for p in ready_queue:
                   if p.burst_time < shortest_p.burst_time:
                       shortest_p = p

                running.append(shortest_p)
                ready_queue.remove(shortest_p)

        #if a process is currently running (or one was just added and started running)
        #decrement the remaining burst time and increase all processes in the queue wait time
        if running:
            running[0].burst_time = running[0].burst_time - 1
            #print(running[0].name + ' is running, time left: ' + str(running[0].burst_time))
            for p in ready_queue:
                p.wait_time = p.wait_time + 1

            if time == 0 and not curr_anims:
                curr_anims = update_anim(window,canvas,ready_queue,incoming,False,time,running)
            else:
                curr_anims = update_anim(window,canvas,ready_queue,incoming,curr_anims,time,running)
            #if the process is done running add it to the results and clear running.
            if running[0].burst_time == 0:
                results.append(running[0])
                running = []
        
        time = time + 1
        ti.sleep(.2)

    return results

def update_anim(window,canvas,ready_queue,incoming,anims,time,running):
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
            
            block_value = int(hashlib.sha256(running[0].name.encode()).hexdigest(), 16)
            block_color = "#{:06x}".format(block_value % 0x1000000)

            canvas.create_rectangle(x, y, x+w, y+h, fill=block_color, outline=block_color)
            canvas.create_text(x+50,y+35,text=running[0].name,font=('Arial','12'))
            
            if running[0].burst_time == 0:
                canvas.create_line(x+w-1,y,x+w-1,y+h+10)
                canvas.create_text(x+w-1,y+h+20,text=str(time+1),font=('Arial','10'))
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

def display_results(window,results,processes):
    def display_left():
        top = tk.Toplevel()
        top.geometry("1600x700")

        top.title("Top-level Window")
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

        results_frame = tk.Frame(top,padx=20,pady=5)
        results_frame.grid(row=0,column=0)
        # Create a grid layout to organize labels and values

        for i in range(len(labels)):
            label = tk.Label(results_frame, text=labels[i],font=('Arial','14'))
            
            if float(values[i]) > 60 and not labels[i]=="Total Processes:":
                both = divmod(float(values[i]),60)
                mins = str(int(both[0]))
                secs = str(int(both[1]))
                value = tk.Label(results_frame, text=mins + 'min ' + secs + 's'    ,font=('Arial','12'))
            elif labels[i] != "Total Processes:":
                value = tk.Label(results_frame, text=values[i]+'s',font=('Arial','12'))
            elif labels[i] == "Total Processes:":
                value = tk.Label(results_frame, text=values[i],font=('Arial','12'))
            
            label.grid(row=i, column=0,padx=0,pady=0)
            value.grid(row=i, column=1)
        
        processes_frame = tk.Frame(top,padx=20,pady=5)
        processes_frame.grid(row=1,column=0,sticky="w")

        title_label = tk.Label(processes_frame, text='Process List:',font=('Arial','14'))
        title_label.grid(row=0,column=2)

        name_header = tk.Label(processes_frame, text='Name',font=('Arial','12'))
        name_header.grid(row=1,column=0,padx=2,pady=0)

        arrival_header = tk.Label(processes_frame, text='Arrival Time',font=('Arial','12'))
        arrival_header.grid(row=1,column=1,padx=2,pady=0)

        burst_header = tk.Label(processes_frame, text='Burst Time',font=('Arial','12'))
        burst_header.grid(row=1,column=2,padx=2,pady=0)

        priority_header = tk.Label(processes_frame, text='Priority',font=('Arial','12'))
        priority_header.grid(row=1,column=3,padx=2,pady=0)

        total_wait_header = tk.Label(processes_frame, text='Total Wait',font=('Arial','12'))
        total_wait_header.grid(row=1,column=4,padx=2,pady=0)

        for i in range(len(processes)):
            name_label = tk.Label(processes_frame, text=str(processes[i].name),font=('Arial','12'))
            name_label.grid(row=i+2, column=0, padx=10,pady=2)

            arrival_label = tk.Label(processes_frame, text=str(processes[i].arrival_time)+'s',font=('Arial','12'))
            arrival_label.grid(row=i+2, column=1, padx=10,pady=2)

            burst_label = tk.Label(processes_frame, text=str(processes[i].burst_time)+'s',font=('Arial','12'))
            burst_label.grid(row=i+2, column=2, padx=10,pady=2)

            priority_label = tk.Label(processes_frame, text=str(processes[i].priority),font=('Arial','12'))
            priority_label.grid(row=i+2, column=3, padx=10,pady=2)

            for p in results:
                if p.name == processes[i].name:
                    total_wait = p.wait_time

            total_wait_label = tk.Label(processes_frame, text=str(total_wait)+'s',font=('Arial','12'))
            total_wait_label.grid(row=i+2, column=4, padx=10,pady=2)


        label = tk.Label(top, text="This is a top-level window with a label")

    display_left() 

    


def main():
    window, C = make_window()

    #get a list of processes from a txt file
    processes = get_processes('processes.txt')
    
    #run shortest job first simulation on the list of processes
    results = SJF(processes,window,C)
    
    processes = get_processes('processes.txt')

    display_results(window,results,processes)
    #calculate total wait time
    total_wait = 0
    for p in results:
        total_wait = total_wait + p.wait_time

    #display results and calculate average wait time
    #print('The result list is in order of when they ran. With the top being who ran first.')
    #print('Final Results: ')
    #print('Avg wait time: ' + str(total_wait/len(results)))
    #print_process_list(results)
    window.mainloop()

main()
