# Flask app
address = "127.0.0.1"
port = 5000
debug = True

# Daemon for cleaning `static/tmp` directory
interval = 10  # In minutes. Interval for daemon execution
max_dir_size = 10737418240  # In bytes. The maximum size of tmp folder
