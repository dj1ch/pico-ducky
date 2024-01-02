# test_environment
This is a test environment to test a duckyscript string on your **own** computer.

### How to use
- Download [Thonny](https://thonny.org/)
- Clone this repo

```shell
git clone https://github.com/dj1ch/pico-ducky.git
```

- Open this folder(in this case `test_environment`) with Thonny/Open the main
- Click the run button to run, it will test mouse movements by default, but you can make your own functions and execute them. 
- Go down to line 330 and you can modify the string: 

```python
ducky_script = """MOUSE MOVE 100 100"""
```

- This string will be run and interpreted using the `parseLine(line)` function, which should handle both mouse movements and keystrokes. 