import argparse
import glob
import os
import sys
from pathlib import Path

# current dir
build_lua_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# ../../Tools/LuaJit = svn path/client/Tools/LuaJIT
luajit_path = Path(build_lua_dir).parent.parent.absolute() / 'BuildTools' / 'LuaJIT'


def build_64_jit(src_file, dest_file):
    dest_sub_dir = os.path.dirname(dest_file)
    os.makedirs(dest_sub_dir, exist_ok=True)

    cmd = ".{}luajit64 -b -g {} {}".format(os.sep, src_file, dest_file)
    # print(cmd)
    os.system(cmd)


def build_32_jit(src_file, dest_file):
    dest_sub_dir = os.path.dirname(dest_file)
    os.makedirs(dest_sub_dir, exist_ok=True)

    cmd = ".{}luajit32 -b -g {} {}".format(os.sep, src_file, dest_file)
    # print(cmd)
    os.system(cmd)


def dispatch_64(src_lua_pairs, dest_dir):
    dest_platform_dir = "{}{}".format(dest_dir, '64')
    dispatch(src_lua_pairs, dest_platform_dir, build_64_jit)


def dispatch_32(src_lua_pairs, dest_dir):
    dest_platform_dir = "{}{}".format(dest_dir, '32')
    dispatch(src_lua_pairs, dest_platform_dir, build_32_jit)


def dispatch(src_lua_pairs, dest_sub_dir, build_func):
    for src_lua_pair in src_lua_pairs:
        full_dest_file = "{}/{}".format(dest_sub_dir, src_lua_pair[0])
        build_func(src_lua_pair[1], full_dest_file)


def dispatch_all(src_lua_pairs, dest_dir):
    dispatch_64(src_lua_pairs, dest_dir)
    dispatch_32(src_lua_pairs, dest_dir)


def dispatch_build(platform, src_dir, dest_dir):
    lookup = {
        '64': dispatch_64,
        '32': dispatch_32,
        'all': dispatch_all
    }

    dispatch_func = lookup.get(platform)

    lua_file_pattern = "{}/**/*.lua".format(src_dir)
    full_src_lua_files = glob.glob(lua_file_pattern, recursive=True)
    src_dir_len = len(src_dir)

    # pair (rel_src_lua, full_src_lua), for example
    # (Common\Str.lua,  G:\DHZ\client\Src\Master\DHZClient\AssetsEx\Lua\Common\Str.lua)
    src_lua_file_pairs = []

    for full_src_lua in full_src_lua_files:
        rel_src_lua = full_src_lua[src_dir_len::]
        src_lua_file_pairs.append((rel_src_lua, full_src_lua))

    # chdir to luajit path
    os.chdir(luajit_path)

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    dispatch_func(src_lua_file_pairs, dest_dir)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Build Lua Arg Parser")
    arg_parser.add_argument("-b", "--bit", default='64', choices=['32', '64', 'all'],
                            help="target platform 32bit or 64bit")
    arg_parser.add_argument("-s", "--source", required=True, help="source directory")
    arg_parser.add_argument("-d", "--dest", required=True, help="destination directory")

    args = arg_parser.parse_args()

    source_dir = args.source
    destination_dir = args.dest

    if source_dir[-1] != '/' or source_dir[-1] != os.sep:
        source_dir += "/"

    if destination_dir[-1] != '/' or destination_dir[-1] != os.sep:
        destination_dir += '\\'

    if os.path.exists(source_dir):
        dispatch_build(args.bit, source_dir, destination_dir)
        print("\nBuild LuaJIT is Done")
    else:
        print("{} is not exist".format(source_dir))
