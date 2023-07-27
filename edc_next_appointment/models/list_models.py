from edc_list_data.model_mixins import ListModelMixin


class InfoSources(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Information Source"
        verbose_name_plural = "Information Sources"
