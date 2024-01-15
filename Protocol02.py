LENGTH_FIELD_SIZE = 2
PORT = 8820


def create_msg(msg):
    """
    get a string and return the same string with his length at the beginning of the string
    :param msg: a str that contain the message
    :return message: a str of the same message with his length at the beginning of the str
    """
    data = str(msg)
    length = str(len(data))  # check the length of the message
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)  # according to the protocol-> length is a 2 digits number
    message = zfill_length + data  # return the message with his length
    return message


def get_msg(current_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    :param current_socket: the received massage
    :return the correct message without his length
    """
    len_data = current_socket.recv(LENGTH_FIELD_SIZE).decode()
    if len_data.isdigit():  # check if the command sanded in the correct protocol
        return current_socket.recv(int(len_data)).decode()
    if len_data == "":  # if the client just close the connection
        return ""
    return "ERROR, wrong protocol"
