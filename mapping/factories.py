import factory

from mapping.enums import ProjectTypes, RuleCorrelations
from mapping.models import MappingCodesystem, MappingCodesystemComponent, MappingEclPart, MappingProject, MappingTask



class MappingCodesystemFactory(factory.django.DjangoModelFactory):
    """Mapping Codesystem Factory."""

    class Meta:
        model = MappingCodesystem

    codesystem_title = factory.Sequence(lambda n: f"Codesystem #{n}")
    codesystem_version = factory.Sequence(lambda n: 1000 + n)


class MappingCodesystemComponentFactory(factory.django.DjangoModelFactory):
    """Mappign Codesystem Component Factory."""

    class Meta:
        model = MappingCodesystemComponent

    codesystem_id = factory.SubFactory(MappingCodesystemFactory)
    component_id = factory.Sequence(lambda n: f"Component #{n}")


class MappingProjectFactory(factory.django.DjangoModelFactory):
    """Mapping Project Factory."""

    class Meta:
        model = MappingProject

    title = factory.Sequence(lambda n: f"Project #{n}")
    project_type = ProjectTypes.snomed_ecl_to_one.value
    active = True


class MappingTaskFactory(factory.django.DjangoModelFactory):
    """Mapping Task Factory."""

    class Meta:
        model = MappingTask

    project_id = factory.SubFactory(MappingProjectFactory)
    category = factory.Sequence(lambda n: f"Category #{n}")
    source_component  = factory.SubFactory(MappingCodesystemComponentFactory)


class MappingECLPartFactory(factory.django.DjangoModelFactory):
    """Mapping ECL Part Factory."""

    class Meta:
        model = MappingEclPart


    task = factory.SubFactory(MappingTaskFactory)
    mapcorrelation = RuleCorrelations.exact_match.value