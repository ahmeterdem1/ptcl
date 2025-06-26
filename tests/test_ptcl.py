from ptcl.transform import *
from ptcl.protocol import Protocol
from ptcl.server import Server
from ptcl.socket import Socket

import pytest
import threading
import socket
import os

def test_transform():
    example_text = "Hello World !".encode('utf-8')
    root = RootTransform()
    to_string = ToString()
    split_text = SplitText(delimiter=" ")
    extractor = ExtractToken()
    router = RouteOnKeyword(["Hello", "World", "!"])
    hello_counter = CountPasses()
    world_counter = CountPasses()
    exclamation_counter = CountPasses()

    root >> to_string >> split_text >> extractor >> router
    router >> hello_counter
    router >> world_counter
    router >> exclamation_counter

    root(example_text)  # Runs the DAG

    assert hello_counter.count == 1 and world_counter.count == 0 and exclamation_counter.count == 0

@pytest.fixture
def test_get_client_protocol():
    root = RootTransform()
    reverse = ReverseTransform()
    to_bytes = ToBytes()

    root >> reverse >> to_bytes
    protocol = Protocol(root)
    return {"client_protocol": protocol}

@pytest.fixture
def test_get_server_protocol():
    root = RootTransform()
    to_string = ToString()
    reverse = ReverseTransform()
    to_bytes = ToBytes()

    root >> to_string >> reverse >> to_bytes
    protocol = Protocol(root)
    return {"server_protocol": protocol}

@pytest.fixture
def test_get_server(test_get_server_protocol):
    protocol = test_get_server_protocol["server_protocol"]
    server = Server(host="127.0.0.1", port=8888, protocol=protocol,
                    handler_class=Socket)
    return {"server": server}

def test_run_server(test_get_server, test_get_client_protocol):
    server = test_get_server["server"]
    thread = threading.Thread(target=server.run)
    thread.start()
    print("Server started.")
    client_protocol = test_get_client_protocol["client_protocol"]
    test_string = "Hello World!"
    data = client_protocol(test_string)

    assert data.decode("utf-8") == test_string[::-1]

    with socket.create_connection(('127.0.0.1', 8888)) as s:
        s.send(data)
        received = s.recv(1024)
    received = received.decode("utf-8")
    assert received == test_string
    thread.join(timeout=5)
    assert thread.is_alive()
    os._exit(0)
