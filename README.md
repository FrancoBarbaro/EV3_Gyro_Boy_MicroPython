# EV3_Gyro_Boy_MicroPython
Self-balancing program for the EV3 core set model "Gyro Boy", based on the original LEGO® MINDSTORMS® Education EV3 Classroom block code program.  You can download this software in the official [LEGO® Education site](https://education.lego.com/en-us/downloads/mindstorms-ev3/software).

## LEGO® MINDSTORMS® EV3 Brick Robot Setup
To get my Lego Midstorms EV3 Brick robot set up I followed the instructions from [ev3dev.org](https://www.ev3dev.org/docs/getting-started/)

## Configuring Python for EV3 Development
Getting Python configured correctly for EV3 Development can be challenging because your OS may already have different (and perhaps old) versions of Python installed.  I followed the instructions from this blog post, which made it really easy and worked seemlessly:
    [The right and wrong way to set Python 3 as default on a Mac](https://opensource.com/article/19/5/python-3-default-mac).


## Configuring VSCode
To configure my development environment I first followed the instructions on the [Lego Education](https://education.lego.com/en-us/support/mindstorms-ev3/python-for-ev3) site, under the section _Visual Studio Code (Steps 4-5)_.

I installed the following **Extensions**.

- [LEGO® MINDSTORMS® EV3 MicroPython](https://marketplace.visualstudio.com/items?itemName=lego-education.ev3-micropython) - this allows you to create MicroPython projects on VSCode and lets you create Run configurations so you can download and run your program in the EV3.
  
- [ev3dev-browser](https://github.com/ev3dev/vscode-ev3dev-browser) - this lets you connect to your EV3 robot, browse, download, and delete files on your robot.
  
- [ms-python.python](https://github.com/Microsoft/vscode-python) - this provides code formatting, syntax checking, and code completion (Intellisense) for the Python programming language.

Finally, I installed the `ev3dev2` Python stubs so that I can have code completion (Intellisense) for this API.  This is incredibly helpful to discover functions and classes available in the API and to simplify the development process.  To get the stubs installed I followed the instructions under the *Code Completion* section on the README.md of the [vscode-hello-python](https://github.com/ev3dev/vscode-hello-python#code-completion) repository.

## Other Helpful Resources

These sites provided me with helpful information to help me get my program completed and working.

- [Python language bindings for ev3dev](https://python-ev3dev.readthedocs.io/en/ev3dev-stretch/index.html) - official site of the `ev3dev2` API containing tutorials and the API docs.

- [EV3Dev Python Site](https://sites.google.com/site/ev3devpython/) - this site is full of useful examples and step-by-step guides.
