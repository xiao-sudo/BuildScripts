from common import arg
from common import pipeline

if __name__ == '__main__':
    arg_parser = arg.new_arg_parser()
    arg.prepare_csharp_parser(arg_parser)

    args = arg_parser.parse_args()

    pipeline = pipeline.new_pipeline()
    pipeline.execute(args.xls_dir)
