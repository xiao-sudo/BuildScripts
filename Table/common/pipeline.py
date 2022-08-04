from . import stage


class Pipeline:
    _Stages = []

    def __init__(self, name):
        self.name = name

    def add_stage(self, one_stage: stage.Stage):
        self._Stages.append(one_stage)

    def execute(self, xls_dir):
        param = xls_dir
        for one_stage in self._Stages:
            param = one_stage.execute(param)


def new_pipeline():
    pipeline_instance = Pipeline("common pipeline")
    pipeline_instance.add_stage(stage.CollectXlsStage("Collect Xls", ["*.xlsx", "*.xlsm"]))
    pipeline_instance.add_stage(stage.ParseXlsStage("Xls To Csv"))
    pipeline_instance.add_stage(stage.PrintStage("Print Table"))
    return pipeline_instance
