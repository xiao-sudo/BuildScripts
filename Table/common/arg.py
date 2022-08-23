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


def single_xls_arg_parser():
    arg_parser = argparse.ArgumentParser(description='Single Xls Parser')
    _preparse_single_xls_parser(arg_parser)

    return arg_parser


def single_sheet_arg_parser():
    arg_parser = argparse.ArgumentParser(description='Single Sheet Parser')
    _preparse_single_xls_parser(arg_parser)
    arg_parser.add_argument('--sheet_name', required=True, help='sheet name')

    return arg_parser


def _preparse_single_xls_parser(parser):
    parser.add_argument('--xls_path', required=True, help='xls file path')
    parser.add_argument('--csv_dir', required=True, help='export csv dir')
    parser.add_argument('--pb_dir', required=True, help='export pb dir')
    return parser
