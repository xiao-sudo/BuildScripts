import argparse


def new_arg_parser():
    arg_parser = argparse.ArgumentParser(description="Table Build Parser")

    arg_parser.add_argument("--xls_dir", required=True, help="xls input dir")
    arg_parser.add_argument("--csv_dir", required=True, help="csv dir")
    arg_parser.add_argument("--temp_dir", required=True, help="temp dir, save intermediate files")

    return arg_parser


def prepare_csharp_parser(parser):
    parser.add_argument("--cs_pb", required=True, help="out csharp protobuf scripts dir")
    parser.add_argument("--cs_bytes", required=True, help="out csharp protobuf data dir")
