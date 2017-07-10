# C++ Compiler warning pragmas for Clang, GCC, and Visual Studio

warn.py is a small python3 untility to generate include files for warning pragmas. The main idea is from [ruslo](https://github.com/ruslo/sugar/wiki/Cross-platform-warning-suppression). The include file contains pragmas for Clang, GCC, and Visual Studio. The script parses a table [warnings.md](warnings.md) to decide which warnings to generate files for and how to name them. The Script parses files from [Barro's compiler-warnings](https://github.com/Barro/compiler-warnings) and [Microsoft](https://docs.microsoft.com/en-us/cpp/error-messages/compiler-warnings/) to figure out which compiler version that added which warning, and adds the corresponding checks in the files.

### Example usage
```
#include <warn/push>
#include <warn/ignore/switch-enum>

switch(val) {
    case Option:Val3: return 3;
    case Option:Val6: return 6;
    default: return 0;
}

#include <warn/push>
```

### Example warning file: switch-enum
```c++
#if !defined(WARN_INCLUDE_PUSH)
#   error "`warn/ignore/switch-enum` used without `warn/push`"
#endif

#if defined(WARN_IGNORE_SWITCH_ENUM)
#   error "`warn/ignore/switch-enum` already included"
#endif

#define WARN_IGNORE_SWITCH_ENUM

#if defined(__clang__)
#   if __clang_major__ > 3 || (__clang_major__ == 3  && __clang_minor__ > 2)
#       if __has_warning("-Wswitch-enum")
#           pragma clang diagnostic ignored "-Wswitch-enum"
#       endif
#   endif
#elif defined(__GNUC__)
#   if __GNUC__ > 3 || (__GNUC__ == 3  && __GNUC_MINOR__ > 4)
#       pragma GCC diagnostic ignored "-Wswitch-enum"
#   endif
#elif defined(_MSC_VER)
#   if (_MSC_FULL_VER >= 130000000)
#       pragma warning(disable: 4061)
#   endif
#endif
```

### Tool Usage
```
usage: warn [-h] [-w TABLE] [-e TABLE [TABLE ...]] [-o DIR]
            [--folder_name NAME] [--ignore_name NAME] [--prefix STR]
            [--header FILE] [--templates DIR] [--gcc_warnings DIR]
            [--clang_warnings DIR] [--vs_warnings DIR]

Generate warning files
Default directory structure:
    output/                (output_dir)
        warn/              (folder_name)
            ignore/        (ignore_name)
                all        (ignore all warnings)
                warning1   (first name from warning table)
                warning2   (second name from warning table)
                ...        (etc for all name in table)
            push           (push pragma state)
            pop            (pop pragma state)

optional arguments:
  -h, --help            show this help message and exit
  -w TABLE, --warnings TABLE
                        warning table file (default: 'warnings.md')
  -e TABLE [TABLE ...], --extra_warnings TABLE [TABLE ...]
                        extra warning table files
  -o DIR, --output_dir DIR
                        output destination (default: 'output')
  --folder_name NAME    base folder name (default: 'warn')
  --ignore_name NAME    ignore folder name (default: 'ignore')
  --prefix STR          include guard prefix (default: '')
  --header FILE         optional header file to include at start of each file
  --templates DIR       template directory, should contain a 'template',
                        'push', and 'pop' file (default: 'templates')
  --gcc_warnings DIR    GCC warnings directory (default: 'ext/barro/gcc')
  --clang_warnings DIR  Clang warnings directory (default: 'ext/barro/clang')
  --vs_warnings DIR     VS warnings directory (default: 'ext/VS')
```
