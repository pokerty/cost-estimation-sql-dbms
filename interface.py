import customtkinter as ctk
import psycopg2
import json
from tkinter import messagebox
from PIL import Image
from graphviz import Digraph
from explain import analyze_and_explain
from queries import query_dict

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Declare constant used for database connection
CONN = None

# Main application class for GUI
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure_window()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def configure_window(self):
        self.title("Query Plan Visualiser")
        self._state_before_windows_set_titlebar_color = 'zoomed'  # maximize the app window on launch
        
    def create_widgets(self):
        self.create_sidebar_frame()
    
    # Creates all widgests in the sidebar frame
    def create_sidebar_frame(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.connect_button = ctk.CTkButton(self.sidebar_frame, text="Connect to Database", command=self.prompt_credentials)
        self.connect_button.pack(padx=20, pady=30)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Please enter or select an SQL query:", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        # Create dropdown list
        options = ["Query 1", "Query 2", "Query 3", "Query 4", 
                   "Query 5", "Query 6", "Query 7", "Query 8",
                   "Query 9", "Query 10", "Query 11", "Query 12",
                   "Query 13", "Query 14", "Query 15"]
        
        self.query_options = ctk.CTkComboBox(self.sidebar_frame, width=200, values=options, state="disabled",command=self.query_select)
        self.query_options.pack(padx=20, pady=20)

        # Create text box for query input
        self.query_box = ctk.CTkTextbox(self.sidebar_frame, wrap="word", width=350, height=500, state="disabled", font=ctk.CTkFont("Consolas", size=15))
        self.query_box.pack(padx=20, pady=10)
        
        self.submit_query_button = ctk.CTkButton(self.sidebar_frame, text="Submit", state="disabled", command=self.submit_query)
        self.submit_query_button.pack(padx=20, pady=10)

        # Create a container frame for the two scrollable frames
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.pack(fill="both", expand=True)

        # Create the first scrollable frame for Query Execution Plan
        self.query_plan_frame = ctk.CTkScrollableFrame(self.container_frame, label_text="Query Execution Plan", label_font=ctk.CTkFont("", 25, "bold"))
        self.query_plan_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5, anchor="nw")

        # Create the second scrollable frame for Query Plan Explanations
        self.query_explain_frame = ctk.CTkScrollableFrame(self.container_frame, label_text="Query Plan Explanations", label_font=ctk.CTkFont("", 25, "bold"))
        self.query_explain_frame.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5, anchor="ne")

        self.create_appearance_widgets()

    # Create widgets to change appearance of the application
    def create_appearance_widgets(self):
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:")
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        
        self.scaling_optionemenu.pack(padx=20, pady=(10, 20), side="bottom")
        self.scaling_label.pack(padx=20, pady=(10, 0), side="bottom")
        self.appearance_mode_optionemenu.pack(padx=20, pady=(10, 10), side="bottom")
        self.appearance_mode_label.pack(padx=20, pady=(20, 0), side="bottom")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    # Function that is called when user click on connect to database button
    def prompt_credentials(self):
        db_window = DatabaseWindow(self)
        db_window.grab_set()  # Make the login window modal
        self.wait_window(db_window)  # Wait for the login window to be closed

        # Check if the login window was closed with successful login
        if db_window.db_success:
            self.connect_button.configure(state="disabled", fg_color="green", text="Connected to Database")
            self.query_options.configure(state="normal")
            self.query_options.set("---Please select a query---")
            self.query_box.configure(state="normal")
            self.submit_query_button.configure(state="normal")

    # Function to handle window closing event
    def on_closing(self):
        # Ensure DB connection is closed before closing
        try:
            if hasattr(self, 'CONN'):
                CONN.close()
        except Exception as e:
            print(f"Failed to stop DB connection: {e}")
        self.destroy()

    # To make query look organised in text box
    def strip_query(self, query):
        # Split the query into lines
        lines = query.split('\n')
        # Strip leading spaces from each line
        stripped_lines = [line.strip() for line in lines]
        # Join the lines back together
        stripped_query = '\n'.join(stripped_lines)
        return stripped_query

    # Function that is called when user selcts a query from the dropdown list
    def query_select(self, choice):
        if choice in query_dict.keys():
            selected_query = self.strip_query(query_dict[choice])
            self.query_box.delete("1.0", "end")  # Clear any previous text in the text box
            self.query_box.insert("1.0", selected_query)  # Insert the selected query into the text box
        else:
            self.query_box.delete("1.0", "end")  # Clear the text box if an invalid option is selected

    # This function extract relevant details from the QEP
    def extract_qep_plan(self, plan):
        node_type = plan.get("Node Type", "")
        total_cost = plan.get("Total Cost", "")
        relation_name = plan.get("Relation Name", "")
        qep_node = {
            "Node Type": node_type,
            "Total Cost": total_cost,
            "Relation Name": relation_name
        }
        if "Plans" in plan:
            qep_node["Plans"] = [self.extract_qep_plan(subplan) for subplan in plan["Plans"]]
        return qep_node

    # This function is called when user clicks the submit button, used to send query and get result from DB
    def submit_query(self):
        global CONN

        # Clear the old diagram if it exists
        if hasattr(self, 'diagram_label'):
            self.diagram_label.destroy()

        # Clear the query explanations if it exists
        if hasattr(self, 'query_explain_box'):
            self.query_explain_box.destroy()

        # If query box is not empty
        if not self.query_box.compare("end-1c", "==", "1.0"):
            query = self.query_box.get("1.0","end") # Get user query from 

            try:
                query_append = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" # Append explain query into user query
                final_query = query_append + query

                cur = CONN.cursor()
                cur.execute(final_query)
                result = cur.fetchall()

                if result:
                    # Extracting the JSON part from the result
                    json_portion = result[0][0]
                    json_string = json.dumps(json_portion, indent=2)
                    qep_json = json.loads(json_string) # JSON result
                    qep_plan = [self.extract_qep_plan(plan_info["Plan"]) for plan_info in qep_json]
                    
                    # Get the QEP explanations
                    explanations = analyze_and_explain(result)

                    # Generate graph for display
                    self.display_qep_plan_explanation(qep_plan, explanations)

            except Exception as e:
                CONN.rollback()
                messagebox.showerror("Query Failed", f"The query failed to execute.\nError: {e}")
                return
        else:
            messagebox.showerror("Empty Query", "Please enter a query.")
            return

    # Generate graph from QEP by calling GraphGeneration Class, display graph and explanations
    def display_qep_plan_explanation(self, qep_plan ,explanations=None):
        graph_path = "query_plan"
        image_path ="query_plan.png"
        graph_generator = GraphGeneration(qep_plan)
        graph_generator.generate_graph(graph_path)

        # Open the image
        image = Image.open(image_path)

        # Calculate the dimensions for resizing
        width, height = image.size
        max_width = 600  # Maximum width for the image
        max_height = 900  # Maximum height for the image

        # Calculate the resizing ratio based on the maximum dimensions
        width_ratio = max_width / width
        height_ratio = max_height / height

        # Choose the minimum ratio to fit within the maximum dimensions
        resize_ratio = min(width_ratio, height_ratio)

        # Resize the image
        new_width = int(width * resize_ratio)
        new_height = int(height * resize_ratio)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Create the image widget with the resized image
        graph_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(new_width, new_height))

        # Display the image in the GUI
        self.diagram_label = ctk.CTkLabel(self.query_plan_frame, text="", image=graph_image)
        self.diagram_label.image = graph_image
        self.diagram_label.pack(pady=10)
        
        # Display query plan explanations textbox
        self.query_explain_box = ctk.CTkTextbox(self.query_explain_frame, wrap="word", width=1200, height=800, font=ctk.CTkFont("", size=15))
        self.query_explain_box.pack(padx=20, pady=10)

        self.query_explain_box.insert("1.0", explanations)

# This class represents the DB credentials window
class DatabaseWindow(ctk.CTkToplevel): 
    def __init__(self, parent):
        super().__init__()
        self.title("Database Credentials")
        width = 500
        height = 350
        # Calculate the coordinates for centering the window
        x = (parent.winfo_width() / 2) - (width / 2)
        y = (parent.winfo_height() / 2) - (height / 2)
        # Adjust the coordinates to center the window properly
        x -= width / 2
        y -= height / 2
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        self.resizable(False, False)
        self.db_success = False # Flag to indicate whether connection was successful
        self.create_widgets()

    # This function creates the necessary widgets for user to input DB credentials
    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Please enter your database credentials", font=("", 20, "bold"))
        self.label.pack(pady=10)

        self.host_entry = ctk.CTkEntry(self, placeholder_text="Host", width=300)
        self.host_entry.pack(pady=5)

        self.port_entry = ctk.CTkEntry(self, placeholder_text="Port", width=300)
        self.port_entry.pack(pady=5)

        self.database_entry = ctk.CTkEntry(self, placeholder_text="Database", width=300)
        self.database_entry.pack(pady=5)
        
        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.user_entry.pack(pady=5)
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=5)
        
        self.login_button = ctk.CTkButton(self, text="Enter", command=self.connect_to_database)
        self.login_button.pack(pady=20)

        self.host_entry.insert(0, "localhost")
        self.port_entry.insert(0, "5432")
        
    # Function to connect to database once credentials are correct   
    def connect_to_database(self):
        global CONN
        # Get user input
        host = self.host_entry.get()
        port = self.port_entry.get()
        db = self.database_entry.get()
        username = self.user_entry.get()
        password = self.password_entry.get()

        # Check if all inputs are filled
        if host and port and db and username and password:
            try:
                # Attempt database connection
                CONN = psycopg2.connect(database=db, user=username, host=host, password=password, port=port)
                messagebox.showinfo("Success", "Connected to database successfully!")
                self.db_success = True # Set DB success 
                self.destroy()

            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to connect to database: {e}")
                
        else:
            messagebox.showerror("Missing/Wrong Inputs", "Please fill up all inputs correctly.")

# This class is used to generate the graph based on the query execution plan
class GraphGeneration:
    def __init__(self, qep_plan):
        self.qep = qep_plan
        # Pre-defining the graph and node's visualization attributes
        graph_attribute = {'bgcolor': 'white', 'rankdir': 'BT'}
        node_attribute = {'style': 'filled', 'color': 'black', 'fillcolor': 'lightblue'}
        self.graph = Digraph(graph_attr=graph_attribute, node_attr=node_attribute)

    # A recursive function to build the graph
    def build_dot(self, qep, parent=None):
        node_id = str(hash(str(qep)))
        label = f"{qep['Node Type']} (Cost: {qep['Total Cost']:.2f})"
        if 'Relation Name' in qep:
            label += f"\nRelation Name: {qep['Relation Name']}"
        shape = 'box'
        self.graph.node(node_id, label, shape=shape)
        if parent is not None:
            self.graph.edge(node_id, parent)
        if 'Plans' in qep:
            for plan in qep['Plans']:
                self.build_dot(plan, node_id)

    # This function is used to generate the graph into png format
    def generate_graph(self, query_plan, format='png', view=True):
        for qep_node in self.qep:
            self.build_dot(qep_node)
        self.graph.attr('node', shape='box')  # set the shape of the nodes
        self.graph.render(query_plan, format=format, view=False, cleanup=True)
