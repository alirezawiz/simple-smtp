light_blue = '\033[0;34m'
light_green = '\033[1;32m'
black = '\033[0;30m'
red = '\033[0;31m'
nc = '\033[0m'


def print_server(text):
    print(light_blue + text)


def print_client(text):
    print(light_green + ">>> " + black + text)


def print_err(text):
    print(red + text)
