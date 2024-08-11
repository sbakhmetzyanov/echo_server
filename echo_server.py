import socket
from http import HTTPStatus
import re

HOST = '127.0.0.1'
PORT = 5000
statuses = [(status.value, status.phrase) for status in HTTPStatus]


def get_status_code(header: str) -> tuple:
    status_code = 200
    status_phrase = 'OK'

    if header.split()[0] == 'GET':
        try:
            received_status_code = int(re.search(r'status=(\d+)', header).group(1))
            for status in statuses:
                if received_status_code == status[0]:
                    status_code = status[0]
                    status_phrase = status[1]
                    break
        except Exception:
            print('Received an unexpected status. Return 200 OK.')

    return status_code, status_phrase


def prepare_server_response(received_data: str, addr) -> str:
    headers = received_data.split('\n')
    method = headers[0].split()[0]
    status_code, status_phrase = get_status_code(headers[0])

    server_response = f'HTTP/1.1 {status_code}\n\n'
    server_response += f'Request Method: {method}\n'
    server_response += f'Request Source: {addr}\n'
    server_response += f'Response Status: {status_code} {status_phrase}\n'

    for header in headers[2:]:
        server_response += f'{header}\n'

    return server_response


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f'Listening on port {PORT}...')

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break
        server_response = prepare_server_response(data, addr)
        conn.sendall(server_response.encode('utf-8'))
        print(server_response)
        conn.close()

    print('Connection closed.')
