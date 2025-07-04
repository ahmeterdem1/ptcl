# PTCL

Design and compose modular protocols

_pip install ptcl_

_Currently, this library only supports finite acyclic protocols._

This library is designed to easily create, save and load protocols and implement
client-server systems with them. The code given as is, even though not version 1.0,
works.

A "protocol", in the eyes of _ptcl_, is a directed acyclic graph of _Transform_ objects.
Each Transform object either works on bytes or string. When its _.transform_ method is called,
a Transform object does something to its input and returns its changes.

Transform objects are chained with ">>" operator, to yield a directed acyclic graph whose nodes
are Transform's. A Transform can have multiple parents or children. When a Transform has multiple
children, the runtime expects it to return an index and a data. The runtime decides which child
to continue with using the index, and passes the data to it.

Graphs of Transform's are wrapped with Protocol class. This class needs a root Transform to wrap.
Save and load operations are governed with this class.

A server needs a Protocol object when initialized. When a connection is recevied, server immediatelly
creates a thread and passes everything to this thread. This thread runs the _run_ method of a Socket,
whose class is also given to the server. This socket, answers its client using the Protocol object,
which is also provided by the server.

Further and more complete documentation will be provided later. This is only to explain the methodology
of the library.

````python
from ptcl.transform import *
from ptcl.protocol import Protocol

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

protocol = Protocol(root)
````

Above code implements a protocol, which gets a text and splits it with " " as the separator.
The first token of this splitted text is extracted and separated from the test. The router,
generates an index depending on what this extracted token is (we expect it to be "Hello").
Depending on the generated index, the rest of the data is routed into either ``hello_counter``,
``world_counter`` or ``exclamation_counter``. In this case, it is supposed to be ``hello_counter``.

A counter transform, CountPasses, increments an internal integer if data is received, then simply
transmits this same data. Therefore after running this protocol on the input string "Hello World!",
we expect ``hello_counter`` to have an internal integer of 1, and 0 for the rest.

Here is the step by step transformation of the input string "Hello World!":

- "Hello World!"
- ["Hello", "World", "!"]
- [["World", "!"], "Hello"]
- [0, ["World", "!"]]  (index given to token ["Hello"] is 0)
- Data ["World", "!"] routed to  ``hello_counter``, which increments its counter
