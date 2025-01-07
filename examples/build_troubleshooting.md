## Dependencies
### Mandatory Dependencies

**Linux/MacOS:** you need a C++ compiler, CMake and GNU make.
  To run the planner, you also need Python 3.

  On Debian/Ubuntu, the following should install all these dependencies:
  ```
  sudo apt install cmake g++ make python3
  ```

**Windows:** install [Visual Studio >= 2017](https://visualstudio.microsoft.com/de/vs/older-downloads/),
[Python](https://www.python.org/downloads/windows/), and [CMake](http://www.cmake.org/download/).
During the installation of Visual Studio, the C++ compiler is not installed by default, but the IDE prompts you to install it when you create a new C++ project.

### Compiling on Windows

Windows does not interpret the shebang in Python files, so you have to call `build.py` as `python3 build.py` (make sure `python3` is on your `PATH`). Also note that options are passed without `--`, e.g., `python3 build.py build=debug`.

Note that compiling from the terminal is only possible with the right environment. The easiest way to get such an environment is to use the `Developer PowerShell for VS 2019` or `Developer PowerShell`.

Alternatively, you can [create a Visual Studio Project](https://www.fast-downward.org/ForDevelopers/CMake#Custom_Builds), open it in Visual Studio and build from there. Visual Studio creates its binary files in subdirectories of the project that our driver script currently does not recognize. If you build with Visual Studio, you have to run the individual components of the planner yourself.

## Troubleshooting

* If you changed the build environment, delete the `builds` directory and rebuild.
* **Windows:** If you cannot execute the Fast Downward binary in a new command line, then it might be unable to find a dynamically linked library.
  Use `dumpbin /dependents PATH\TO\DOWNWARD\BINARY` to list all required libraries and ensure that they can be found in your `PATH` variable.
* **MacOS:** If your compiler doesn't find flex or bison when building VAL, your include directories might be in a non-standard location. In this case you probably have to specify where to look for includes and libraries in VAL's   
  Makefile (probably `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr`).

