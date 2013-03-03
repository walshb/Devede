##Creating a DVD at the command line

First clone the code and switch to the "command_line" branch:

```
git clone https://github.com/walshb/Devede.git
cd Devede
git checkout command_line
```

Now the DVD .iso image can be created:

```
./devede_cli.py --path myvideo.avi --output --finalfolder /var/tmp --outputname mydvd
```

This produces quite a lot of verbose output, after which the results can be seen in /var/tmp/mydvd.

Alternatively the DVD description can be created in the GUI (see below), saved, and run at the command line:

```
./devede_cli.py mydvd.devede2
```

The .devede2 file is in "ini" format and can be edited using a text editor.

More details are available by typing:

```
./devede_cli.py --help
```

##Creating a DVD using the GUI

The Devede GUI is still available to create DVDs:

```
./devede.py
```
