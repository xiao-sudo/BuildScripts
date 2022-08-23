from common import arg
from common import pipeline

if __name__ == '__main__':
    arg_parser = arg.single_sheet_arg_parser()
    args = arg_parser.parse_args()

    pipeline = pipeline.new_single_sheet_pipeline(args.sheet_name)
    pipeline.execute(args.xls_path)
