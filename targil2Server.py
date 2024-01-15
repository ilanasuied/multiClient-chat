import socket
import select
import Protocol02

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5588
SERVER_IP = '0.0.0.0'
client_socketsDic = {}
messages_to_send = []
client_sockets = []


def print_client_sockets():
    """
    printing the details of all the clients
    """
    for c in client_sockets:
        print("\t", c.getpeername())


def add_client(msg, cur_socket):
    """

    :param msg: srt of the message that we get from the client
    :param cur_socket: the socket of the current client
    :return: hello with the name of the client
    """
    index = msg.find(" ")
    key = msg[index+1:]
    if key in client_socketsDic.keys():  # check that the name has not yet been taken
        return Protocol02.create_msg("ERROR, this name is taken\n")
    if cur_socket in client_socketsDic.values():  # check if this client exist already in the dic with another name
        value = str({j for j in client_socketsDic if client_socketsDic[j] == cur_socket})
        old_name = ""
        for ch in value:
            if ch.isalpha():
                old_name += ch
        print(old_name, "changed his names to:", key)  # send to the server that the client changed his name
        del client_socketsDic[old_name]  # delete the old one
    client_socketsDic[key] = cur_socket  # add the new one in the directory
    return Protocol02.create_msg("Hello " + msg[msg.find("NAME") + 5:])  # return hello + the name


def msg_cmd(msg, curr_socket):
    """

    :param msg: the message that the current client wants to send
    :param curr_socket: the current client
    :return: if the client exist, return the message, else return an ERROR message
    """
    lst_msg = msg.split()
    msg_to = lst_msg[1]  # keep the name of the client to whom we want to send the message
    lst_msg = lst_msg[2:]  # keep the message
    msg_send = ""
    for word in lst_msg:
        msg_send += ' ' + word
    if msg_to in client_socketsDic.keys():  # find the name of this current client
        value = str({i for i in client_socketsDic if client_socketsDic[i] == curr_socket})
        msg_from = ""
        for val in value:
            if val.isalpha():
                msg_from += val
        send_msg = (msg_from + " send you:" + msg_send)  # build the correct message
        return messages_to_send.append((client_socketsDic[msg_to], Protocol02.create_msg(send_msg)))  # send it
    return Protocol02.create_msg("ERROR, this client not exist")  # if the client not exist, return ERROR


def get_names():
    """
    :return: a string of all the clients
    """
    list_of_clients = ""
    lst = list(client_socketsDic.keys())
    for client in lst:
        list_of_clients += ' ' + client
    return list_of_clients


def check_msg(msg, socket_current):
    """
    check what the client wants and return the correct answer
    :param msg: the client message
    :param socket_current: the socket of the current client
    :return: the correct answer for this message
    """
    lst_msg = msg.split()
    if msg.find("NAME") == 0 and len(lst_msg) > 1:  # check if this is "name" command
        return add_client(msg, socket_current)
    elif msg.find("GET_NAMES") == 0 and len(lst_msg) == 1:  # check if this is "get_names" command
        return Protocol02.create_msg(get_names())  # return the list of all the client's name
    elif msg.find("MSG") == 0 and len(lst_msg) > 2:  # check if this is "msg" command
        return msg_cmd(msg, socket_current)
    return Protocol02.create_msg("ERROR, wrong command\n")  # default, the command is incorrect


print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Listening for clients...")

while True:
    r_list, w_list, x_list = select.select([server_socket] + client_sockets, client_sockets, [])
    for current_socket in r_list:
        if current_socket is server_socket:
            connection, client_address = current_socket.accept()
            print("New client joined!", client_address)
            client_sockets.append(connection)
            print_client_sockets()
        else:
            data = Protocol02.get_msg(current_socket)
            if data == "":
                print("Connection closed", )
                for i in client_socketsDic:
                    if client_socketsDic[i] == current_socket:
                        del client_socketsDic[i]  # delete this client from the dictionary
                        break
                client_sockets.remove(current_socket)  # remove this client also from the list
                current_socket.close()  # close his socket
                print_client_sockets()
            elif data == "ERROR, wrong protocol":
                messages_to_send.append((current_socket, Protocol02.create_msg(data)))
            else:
                replay = check_msg(data, current_socket)
                messages_to_send.append((current_socket, replay))  # add to the list of tuples the message + socket
    for message in messages_to_send:
        current_socket, data = message
        if current_socket in w_list and data is not None:  # if there is something to send to someone, send it
            current_socket.send(data.encode())
            messages_to_send.remove(message)  # delete the message after sending it

    if not client_sockets:  # if all the clients close their socket
        break               # break the loop and close the server socket

server_socket.close()  # close the server's socket
