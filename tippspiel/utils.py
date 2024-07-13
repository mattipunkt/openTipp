def get_current_tab():
    with open("/tmp/currtab", "r") as file:
        return int(file.read())