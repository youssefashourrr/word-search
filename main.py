import tkinter as tk
import random
from tkinter import messagebox
import time
import json
import os


found_counter = 0
color_counter = 0
tries_counter = 0
max_tries = 0
root = None
correct_submissions = []

categories = {1: 'Animals', 2: 'Capitals and Countries', 3: 'Fruits and Vegetables', 4: 'Sports'}

# Function that starts the game by managing the player's category choice and name input
def word_choice():
    global root
    root = tk.Tk()  
    root.title("Setup")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = 575
    window_height = 325

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    create_input_entry(root, "Enter your name:") 
    create_input_entry(root, "Choose category (1 for Animals, 2 for Countries and Capitals, 3 for Fruits and Vegetables, 4 for Sports):")  

    difficulty_menu = tk.Menubutton(root, text="New Game", relief=tk.RAISED)
    difficulty_menu.pack(side="top", pady=7)
    difficulty_menu.menu = tk.Menu(difficulty_menu, tearoff=0)
    difficulty_menu["menu"] = difficulty_menu.menu

    difficulty_menu.menu.add_command(label="Easy", command=lambda: mode(root, "easy"))
    difficulty_menu.menu.add_command(label="Medium", command=lambda: mode(root, "medium"))
    difficulty_menu.menu.add_command(label="Hard", command=lambda: mode(root, "hard"))

    load_menu_button = tk.Menubutton(root, text="Load Game", relief=tk.RAISED)
    load_menu_button.pack(side="top", pady=7)
    load_menu_button.menu = tk.Menu(load_menu_button, tearoff=0)
    load_menu_button["menu"] = load_menu_button.menu

    existing_saves = get_existing_saves()
    if existing_saves:
        for save_file in existing_saves:
            load_menu_button.menu.add_command(label=save_file, command=lambda sf=save_file: load_game(sf))
    else:
        load_menu_button.menu.add_command(label="No saved games found", state=tk.DISABLED)       

    root.mainloop()


# Function to create an input entry and a label above it in a chosen window
def create_input_entry(window, label_text):
    label = tk.Label(window, text=label_text)
    label.pack(side="top", pady=10)

    entry = tk.Entry(window)
    entry.pack(side="top", pady=10)  


# Function for starting the game according to the difficulty button clicked by the user (different word count and grid size)
def mode(window, difficulty):
    global words_to_find
    global max_tries  
    words_to_find = []
    entry_name = window.winfo_children()[1].get() 
    category_choice = window.winfo_children()[3].get()  

    try:
        category_choice = int(category_choice)
    except ValueError:
        invalid_category = tk.Label(root, text="Enter a valid category number")
        invalid_category.pack(side="top", pady=8)
        root.after(1500, lambda: invalid_category.pack_forget())
        return

    if 1 <= category_choice <= 4:
        category_file_name = f'Word Lists\\{categories[category_choice]}.txt' 
        words = read_words_from_file(category_file_name)  

        if difficulty == "easy":
            num_words = 5
            grid_size = 8
            max_tries = 2

        elif difficulty == "medium":
            num_words = 7
            grid_size = 10
            max_tries = 4

        elif difficulty == "hard":
            num_words = 10
            grid_size = 12
            max_tries = 6

        while True:
            new_word = random.choice(words).strip()
            if len(words_to_find) == num_words:
                break
            elif new_word not in words_to_find:
                words_to_find.append(new_word)
            else:
                continue  

        capitalized_words = [word.capitalize() for word in words_to_find]
        hint_text = f"Hi {entry_name}, how many words can you find?\nHint: the words are {', '.join(capitalized_words)}" 

        create_word_search(grid_size, grid_size, words_to_find, max_tries, hint=hint_text)
        
    else:
        invalid_category = tk.Label(root, text="Invalid category number\n Choose from (1, 2, 3 or 4)")
        invalid_category.pack(side="top", pady=8)
        root.after(1500, lambda: invalid_category.pack_forget())


# Function to read words from a file and store each line as an element of a list
def read_words_from_file(file_path):
    with open(file_path, 'r') as list_file:
        return list_file.readlines()


# Function to create the word search game window
def create_word_search(rows, cols, words_to_find, tries, hint=None):
    global start_time
    global total_score 
    global grid
    global game_window
    game_window = tk.Toplevel()
    game_window.title("Word Search by Hello World")
    game_window.attributes('-fullscreen', True)
    game_window.configure(bg="#C6DEF1")

    grid_frame = tk.Frame(game_window)
    grid_frame.pack()  
    submit_button = tk.Button(game_window, text="SUBMIT", font=("Impact", 15), width=10, height=3, bg="lightgreen", relief=tk.RAISED, command=lambda: checkWords(grid))  
    submit_button.pack(side="bottom", pady=10)  

    grid = []  
    for _ in range(rows):
        row = []  
        for _ in range(cols):
            cell_label = tk.Label(grid_frame, text='_', font=("Arial", 9, "bold"), width=6, height=4, borderwidth=2, bg="white", relief=tk.RIDGE)
            row.append(cell_label)
        grid.append(row)  

    game_window.bind("<Escape>", lambda event: on_escape_key(root))

    start_time = time.time()
    total_score = 0
    
    hint_label = tk.Label(game_window, text=hint, bg="#C6DEF1", fg="darkorange", bd=4, font=("Verdana", 14, "bold italic"))
    hint_label.pack(side="top", pady=15)

    add_words_to_grid(grid, words_to_find)
    fill_empty_spaces(grid) 
    display_grid(grid)  


# Function used for word placement and/or arrangement
def add_words_to_grid(game_grid, words):
    for word in words:
        placed = False
        while not placed:
            row = random.randint(0, len(game_grid) - 1)  
            col = random.randint(0, len(game_grid[0]) - 1)
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1)])

            valid_placement = True
            for i in range(len(word)):
                new_row = row + i * direction[0]
                new_col = col + i * direction[1]  

                if not (0 <= new_row < len(game_grid) and 0 <= new_col < len(game_grid[0])) or game_grid[new_row][new_col]['text'] != '_':
                    valid_placement = False
                    break

            if valid_placement:
                for i in range(len(word)):
                    game_grid[row + i * direction[0]][col + i * direction[1]]['text'] = word[i]  # Place the word in the grid
                placed = True
    return game_grid


# Function for filling the empty spaces in the grid (containing an underscore)
def fill_empty_spaces(game_grid):
    for row in range(len(game_grid)):
        for col in range(len(game_grid[0])):
            if game_grid[row][col]["text"] == '_':
                game_grid[row][col]["text"] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


# Function for displaying the grid as separate labels in the window
def display_grid(game_grid):
    for r in range(len(game_grid)):
        for c in range(len(game_grid[0])):
            game_grid[r][c].grid(row=r, column=c)
            game_grid[r][c].bind("<Button-1>", lambda event, label=game_grid[r][c]: on_cell_click(label))  


# Function for changing the color of each label when a certain button input is given
def on_cell_click(label):
    current_bg = label.cget("bg")
    if current_bg == "white":
        label.config(bg="yellow")
    elif current_bg == "yellow":
        label.config(bg="white")


# Function for checking right and wrong attempts by the user        
def checkWords(game_grid):
    global found_counter
    global color_counter
    global tries_counter
    global max_tries
    global total_score
    global start_time
    global correct_submissions

    word_found = ""
    answer_colors = ["red", "blue", "green", "grey", "purple", "orange", "pink", "turquoise", "brown"]

    for r in range(len(game_grid)):
        for c in range(len(game_grid[0])):
            if game_grid[r][c].cget("bg") == "yellow":
                word_found = word_found + (game_grid[r][c].cget("text"))  

    if word_found in words_to_find or word_found[::-1] in words_to_find:
        end_time = time.time()
        time_taken = int(end_time) - int(start_time)
        word_length_bonus = len(word_found)
        time_bonus = max(0, 15 - time_taken)
        word_score = int(word_length_bonus + time_bonus)

        total_score += word_score
        found_counter += 1
        color_counter += 1
        correct_submissions.append(word_found)
        correctLabel = tk.Label(game_window, text=f"Correct Answer\nScore: {total_score}", font=("Courier New", 13, "bold"), fg="darkgreen", bg="#C6DEF1")
        correctLabel.pack(side="bottom", pady=5)
        game_window.after(1500, lambda: correctLabel.pack_forget())

        start_time = time.time()

        for r in range(len(game_grid)):
            for c in range(len(game_grid[0])):
                if game_grid[r][c].cget("bg") == "yellow" and color_counter <= 9:
                    game_grid[r][c].config(bg=answer_colors[color_counter - 1])

        if found_counter == len(words_to_find):
            messagebox.showinfo("Congratulations", f"You Win!\nTotal Score: {total_score}")
            game_window.after(1000, game_window.destroy())
            root.after(1000, root.destroy())

    else:
        incorrectLabel = tk.Label(game_window, text=f"Wrong Answer\n Remaining tries:{max_tries-1}", font=("Courier New", 13, "bold"), fg="red", bg="#C6DEF1")
        incorrectLabel.pack(side="bottom", pady=5)
        game_window.after(1500, lambda: incorrectLabel.pack_forget())
        max_tries -= 1
        if max_tries == 0:
            messagebox.showinfo("Game Over", "You've run out of tries.")
            game_window.destroy()
            root.destroy()


# Function for retrieving all json save files
def get_existing_saves():
    try:
        save_files = [file for file in os.listdir("Saves") if file.endswith("_game_progress.txt")]
        return save_files
    except FileNotFoundError:
        return []


# Function for binding the ESC key to a function
def on_escape_key(window):
    pause = tk.Toplevel(window)
    pause.geometry("250x125")
    pause.title("Game Paused")

    message_label = tk.Label(pause, text="Do you want to:\n(i) Exit and save?\n(ii) Exit without saving?")
    message_label.pack(pady=10)
    save_and_exit_button = tk.Button(pause, text="i", command=lambda: handle_exit(root, pause, True))
    save_and_exit_button.pack(side="left", padx=20)
    exit_button = tk.Button(pause, text="ii", command=lambda: handle_exit(root, pause, False))
    exit_button.pack(side="right", padx=20)


# Function for handling the process of closing the game
def handle_exit(primary, secondary, save):
    if save == True:
        player_name = primary.winfo_children()[1].get()
        save_game(player_name)
    secondary.destroy()
    primary.destroy()


# Function for saving the data needed for loading to a text file
def save_game(username):
    data = f"Player Name: {username}\nFound Counter: {found_counter}\nColor Counter: {color_counter}\nWords Found: {correct_submissions}\nGame Grid: {add_words_to_grid}"
    file_name = f'Saves\\{username.replace(" ", "_")}_game_progress.txt'
    with open(file_name, 'w') as save_file:
        save_file.write(data)

def create_loaded_grid(game_grid):
    global start_time
    global total_score 
    global grid
    global game_window
    game_window = tk.Toplevel()
    game_window.title("Word Search by Hello World")
    game_window.attributes('-fullscreen', True)
    game_window.configure(bg="#C6DEF1")

    grid_frame = tk.Frame(game_window)
    grid_frame.pack()  
    submit_button = tk.Button(game_window, text="SUBMIT", font=("Impact", 15), width=10, height=3, bg="lightgreen", relief=tk.RAISED, command=lambda: checkWords(grid))  
    submit_button.pack(side="bottom", pady=10)  

    game_window.bind("<Escape>", lambda event: on_escape_key(root))

    start_time = time.time()
    total_score = 0
    
    hint_label = tk.Label(game_window, text="", bg="#C6DEF1", fg="darkorange", bd=4, font=("Verdana", 14, "bold italic"))
    hint_label.pack(side="top", pady=15)
 
    display_grid(game_grid)

def load_game(file_name):
    with open(f'Saves//{file_name}', 'r') as load_file:
        loaded_name = load_file.readline().lstrip("Player Name: ").rstrip('\n')
        loaded_found_counter = int(load_file.readline().lstrip("Found Counter: ").rstrip('\n'))
        loaded_color_counter = int(load_file.readline().lstrip("Color Counter: ").rstrip('\n'))
        loaded_words_found = load_file.readline().lstrip("Words Found: ").rstrip('\n')
        loaded_grid = load_file.readline().lstrip("Game Grid: ").rstrip('\n')
    create_loaded_grid(loaded_grid)
        

word_choice()
