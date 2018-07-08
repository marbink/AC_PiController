As you would notice, my IR commands are not the usual raw format you can see in LIRC or other IR softwares.
Examples:
Raw Lirc format:
```4500 4300 600 1550 600 500 600 1500 650 1550 600 450 600 500 600 1550 600 500 600 450 600 1550 600 500 600 500 600 1550 600 1550 600 450 600 1600 550 500 600 1550 600 1550 600 1550 600 1600 600 450 600 1600 550 1550 600 1600 550 500 600 500 600 450 600 500 600 1550 600 500 600 450 600 1600 550 1600 550 1600 550 500 600 500 600 500 550 500 600 500 550 550 550 500 600 500 600 1550 550 1600 600 1550 550 1600 600 1550 600 5150 4400 4350 600 1550 600 500 550 1600 550 1600 600 500 550 550 550 1550 600 500 600 500 550 1600 550 500 600 500 600 1550 550 1600 600 500 550 1600 550 550 550 1600 550 1600 550 1600 550 1600 600 500 550 1600 550 1600 550 1600 550 550 550 500 600 500 550 550 550 1600 550 550 550 500 550 1600 600 1600 550 1550 600 500 600 500 550 500 550 550 550 500 600 500 600 500 550 550 550 1550 600 1600 550 1600 550 1600 550 1600 550 1600```

My format:
```101100100100110100011111111000000000100011110111```

I basically changed the format to have a more compact way to put commands in config.py, let me introduce one more data before explain how to convert it.
- This is a function declaration in _ir_tx.py file
`def convert_to_pulses(bin_string, pause=600, zero=500, one=1600, repeat=2, repeat_pause=5100, header=(4500, 4300)):`
As you can see I set some default parameters to avoid to pass them every time, but what you have to notice are the values


Let's start from recognize that my IR Raw command (the one in the Lirc format example) is basically composed by:

Header: `4500 4300`
Big block: `600 1550 ...`
Something I called `repeat_pause` in the middle: `600 5150`
than Header again
than Big Block again.

This exaplain the reason I set these values `repeat=2, repeat_pause=5100, header=(4500, 4300)`.

Now let's see the big block numbers. We have to assume about 100 tolerance for each number. We have to watch them as couples.
`600 1550` can be a 1,
`600 500` can be a 0.
Or viceversa, not really important as you can change values in py code accordingly to which decision you take.

`600` is a common part and that's the pause value.

That's why I set `pause=600, zero=500, one=1600`.

If you want to use raw numbers you can avoid the use of `convert_to_pulses` function and use directly `transmit(p, gpio_number=25, freq=38000)` as its first parameter is an array containing the lirc format integers.
