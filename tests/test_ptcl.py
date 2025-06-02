from ptcl.transform import *

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


