import socket
import Protocol02
import msvcrt
import select


def input_func():
    """
    this is a non blocking input and output function
    :return: the client's command
    """

    string = ""
    cmd = ""
    while 1:
        if not msvcrt.kbhit():                      # if the user doesnt press on the keyboard
            r_list, w_list, x_list = select.select([my_socket], [], [], 0)
            for current_socket in r_list:           # check if someone wants to send something
                data = Protocol02.get_msg(current_socket)
                if data is not None and data != "":
                    print("Server replied:", data)  # print the message
        else:                                       # if the user wants to send something, get the chars
            key = msvcrt.getch()
            if key == chr(13).encode():             # if the user press ENTER, break the loop
                break
            else:
                cmd += string + key.decode()        # keep the message
                print(string + key.decode(), end="", flush=True)  # print the char that the user just wrote

    print('\n')
    return cmd                                      # return the command


my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1", 5588))
print("Pls enter message")
msg = input_func()

while msg != "EXIT" and msg != "":        # close the socket if the client send EXIT or just press on the key: ENTER

    message = Protocol02.create_msg(msg)  # create the message correctly
    my_socket.send(message.encode())      # send it
    msg = input_func()                    # get another command from the user

my_socket.close()                         # close the socket

