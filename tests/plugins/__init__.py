# this piece of bullshit is necessary so plugins can import the plugin "interface" class
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
