from . import stage
from . import table


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
    pipeline_instance.add_stage(stage.MultipleExportStage('Table to CSV', [
        {'name': 'Client', 'out_dir': './client', 'tag_filter': _client_tag_filter},
        {'name': 'Server', 'out_dir': './server', 'tag_filter': _server_tag_filter}
    ]))
    # pipeline_instance.add_stage(stage.ExportStage("Server CSV", '.', _server_tag_filter))
    # pipeline_instance.add_stage(stage.PrintStage("Print Table"))
    return pipeline_instance


def _server_tag_filter(tag):
    return tag == table.Tag.Server or tag == table.Tag.CS


def _client_tag_filter(tag):
    return tag == table.Tag.Client or tag == table.Tag.CS
