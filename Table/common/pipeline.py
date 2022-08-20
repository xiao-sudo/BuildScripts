from . import stage
from .table import Tag


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
    pipeline_instance.add_stage(stage.ParseXlsStage("Xls To Table"))
    pipeline_instance.add_stage(stage.CSVExportStage("CSV Export", "./"))
    # pipeline_instance.add_stage(stage.MultipleExportStage('Table to CSV', [
    #     stage.CSVExportSetting('Client', './client', Tag.Client, _tag_compatible),
    #     stage.CSVExportSetting('Server', './server', Tag.Server, _tag_compatible)
    # ]))
    # pipeline_instance.add_stage(stage.GenProtoStage('Proto Gen'))
    return pipeline_instance


def _tag_compatible(target_tag, input_tag):
    return target_tag & input_tag


def _tag_exact_match(target_tag, input_tag):
    return target_tag == input_tag
