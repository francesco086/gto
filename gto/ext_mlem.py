"""This is temporary file that should be moved to mlem.gto module"""
from mlem.core.errors import MlemObjectNotFound
from mlem.core.metadata import load_meta
from mlem.core.objects import MlemMeta, ModelMeta, DatasetMeta
from pydantic import BaseModel

from gto.ext import Enrichment, EnrichmentInfo
import mlem


class MlemInfo(EnrichmentInfo):
    meta: MlemMeta

    def get_object(self) -> BaseModel:
        return self.meta

    def get_human_readable(self) -> str:
        # TODO: create `.describe` method in MlemMeta https://github.com/iterative/mlem/issues/98
        description = f"""Mlem {self.meta.object_type}"""
        if isinstance(self.meta, ModelMeta):
            description += f": {self.meta.model_type.type}"
        if isinstance(self.meta, DatasetMeta):
            description += f": {self.meta.dataset.dataset_type.type}"
        return description


class MlemEnrichment(Enrichment):
    def is_enriched(self, obj: str) -> bool:
        try:
            mlem.api.load_meta(obj)
            return True
        except MlemObjectNotFound:
            return False

    def describe(self, obj: str) -> MlemInfo:
        return MlemInfo(source="mlem", meta=load_meta(obj))